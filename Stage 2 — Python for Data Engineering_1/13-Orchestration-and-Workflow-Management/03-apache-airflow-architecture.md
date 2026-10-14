# Apache Airflow Architecture

> **Module:** Stage 2 — Python for Data Engineering  
> **Folder:** `13-Orchestration-and-Workflow-Management/`  
> **Topic:** 03 — Apache Airflow Architecture  
> **Primary focus:** Apache Airflow 3.x  
> **Prerequisites:** `01-dags-dependencies-and-scheduling-concepts.md`, `02-limits-of-cron-and-why-orchestrators-exist.md`

---

## 1. Learning Objective

The goal of this lesson is to replace the beginner mental model:

> “I have a DAG file and Airflow runs it.”

with a production-oriented mental model:

```text
DAG source
    ↓
DAG Processor
    ↓
Scheduler
    ↓
Task eligibility
    ↓
Executor
    ↓
Worker / execution environment
    ↓
Task execution
    ↓
Logs + state
    ↓
Metadata Database
    ↓
Scheduler evaluates downstream work
```

By the end, you should be able to look at an Airflow deployment and explain:

- where DAG source code comes from;
- who parses it;
- who decides what should run;
- how DAG runs and task instances participate in execution;
- how dependencies and concurrency affect eligibility;
- what the executor contributes;
- where task work actually runs;
- what the Triggerer does;
- where orchestration state is stored;
- what the API Server provides;
- where logs go;
- why remote logging matters;
- what happens when a worker, scheduler, API Server, Triggerer, or metadata database has a problem;
- how Airflow scales;
- how local, distributed, and Kubernetes-oriented execution differ;
- what important architectural concepts changed between Airflow 2.x and Airflow 3.x;
- how to debug an Airflow architecture systematically.

---

# 2. Version-Aware Rule

This lesson teaches **Airflow 3.x as the primary architecture**.

When older material is discussed, it is explicitly labeled:

- **Airflow 2.x / legacy**
- **Older Airflow architecture**
- **Reference architecture**

Do not silently combine documentation from different major versions.

Before applying an example, check:

```text
Airflow version
Python version
provider version
deployment model
documentation version
```

This matters because online tutorials can mix older terminology such as:

```text
webserver
execution_date
Dataset
direct metadata-database access from task code
```

with newer Airflow 3.x concepts such as:

```text
API Server
DAG Processor
task SDK / supported API model
Assets terminology
```

The architectural objective is not to memorize version trivia. It is to understand **why the boundaries exist and how to identify the architecture you are actually running**.

---

# 3. The Simplest Airflow Mental Model

Start with the smallest useful picture:

```text
You write a DAG
      ↓
Airflow discovers it
      ↓
Airflow parses it
      ↓
Scheduler decides what should run
      ↓
Executor determines how execution is dispatched
      ↓
Worker / execution environment runs the task
      ↓
Logs and task state are recorded
      ↓
Scheduler evaluates downstream work
```

Think of Airflow as a coordination system.

For a simple pipeline:

```text
Extract
   ↓
Transform
   ↓
Validate
   ↓
Publish
```

Airflow's job is primarily to coordinate **when and under what conditions** those pieces of work execute.

It is not normally the system that should perform all of the heavy data processing itself.

For example:

```text
Airflow
   │
   ├── starts an extraction job
   ├── waits for it to succeed
   ├── starts a transformation job
   ├── waits for validation
   └── starts publishing
```

The actual work might happen in:

```text
Python
PostgreSQL
Spark
dbt
S3 / object storage
APIs
SFTP
Kubernetes
external services
```

A useful rule is:

> **Airflow coordinates work; the appropriate execution system performs the work.**

---

# 4. What Is Apache Airflow?

Apache Airflow is a workflow orchestration platform.

A workflow contains:

```text
tasks
dependencies
timing
state
execution
operational history
```

Airflow provides the machinery required to coordinate those concerns.

## 4.1 What problem does Airflow solve?

Suppose a business pipeline requires:

```text
1. Extract orders
2. Validate extraction
3. Transform orders
4. Load analytics tables
5. Run data-quality checks
6. Publish a downstream dataset
```

A simple script can execute those commands sequentially.

But production systems need more:

- dependency management;
- scheduling;
- task state;
- retries and recovery;
- concurrency control;
- distributed execution;
- logging;
- operational visibility;
- backfills and historical execution;
- external-system integrations;
- failure diagnosis.

Airflow provides an orchestration control plane for these concerns.

## 4.2 Why is Airflow not just a Python script?

A Python script usually has a single process controlling execution.

Airflow separates responsibilities across components.

Conceptually:

```text
DAG Processor
    understands workflow definitions

Scheduler
    decides what is eligible to run

Executor
    coordinates dispatch

Worker / execution environment
    performs task work

Metadata Database
    stores orchestration state

API Server
    provides supported operational access

Triggerer
    handles asynchronous waiting
```

This separation allows the platform to scale and fail independently in meaningful ways.

## 4.3 Why is Airflow not simply cron?

Cron can answer:

> “Run this command at this time.”

Airflow must answer questions such as:

> “Should this task run yet?”

> “Did its upstream task succeed?”

> “Is there capacity?”

> “Where should it execute?”

> “What state is this task in?”

> “What happened during the previous attempt?”

> “Can downstream work become eligible?”

That is a much larger coordination problem.

---

# 5. Airflow Architecture at a Glance

A simplified architecture is:

```text
                         ┌────────────────────┐
                         │     DAG Source     │
                         │ Python Definitions  │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   DAG Processor    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │     Scheduler      │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │     Executor       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      Workers       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                              Task Work
```

Operational access:

```text
                         ┌────────────────────┐
                         │    API Server      │
                         │     UI + REST      │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │  Metadata Database │
                         │    PostgreSQL      │
                         └────────────────────┘
```

Asynchronous waiting:

```text
                         ┌────────────────────┐
                         │     Triggerer      │
                         │ async waiting      │
                         └────────────────────┘
```

Logging:

```text
Task execution
     │
     ├── local logs
     │
     └── remote logs ──→ object storage / logging backend
```

These are conceptual architecture diagrams, not a guarantee that every deployment has exactly these processes or containers.

---

# 6. Component Responsibility Map

| Component | Primary responsibility | Heavy data processing? |
|---|---|---:|
| DAG Processor | Discover/process DAG source and produce usable DAG definitions | No |
| Scheduler | Determine what should run and coordinate scheduling | No |
| API Server | Supported UI/API operational access | No |
| Triggerer | Efficient asynchronous waiting for deferred work | No |
| Executor | Coordinate how eligible tasks are dispatched | No |
| Worker / execution environment | Perform task workloads | Yes, within the intended task model |
| Metadata Database | Store orchestration metadata and operational state | No |
| Providers | Integrate Airflow with external systems | No; they enable integrations |

The word **heavy** needs context.

A worker may legitimately launch:

```text
Spark job
SQL transformation
Python extraction
Kubernetes workload
data-quality check
```

The scheduler should not become the engine doing those workloads.

---

# 7. Scheduler

## 7.1 What is the scheduler?

The scheduler is the component responsible for determining which workflow work is eligible to proceed.

At a high level:

```text
Read current state
      ↓
Find candidate work
      ↓
Evaluate dependencies
      ↓
Check scheduling/concurrency constraints
      ↓
Queue eligible work
      ↓
Coordinate with executor
      ↓
Observe state changes
      ↓
Repeat
```

This is a conceptual loop, not a promise about a particular internal implementation.

## 7.2 Why does the scheduler exist?

Without a scheduler, something else would have to continually answer:

```text
Should this DAG run now?
Is this task eligible?
Did upstream work succeed?
Is there capacity?
Should downstream work start?
```

The scheduler centralizes this coordination responsibility.

## 7.3 What the scheduler does

The scheduler conceptually handles:

- scheduling decisions;
- dependency evaluation;
- task eligibility;
- concurrency coordination;
- dispatch toward execution;
- observing task/run state;
- advancing workflows as prerequisites are satisfied.

## 7.4 What the scheduler should not do

It should not become:

```text
a Spark cluster
a data warehouse
a bulk ETL engine
a 500 GB in-memory processor
a general-purpose application server
```

For example, do not design the architecture so that the scheduler itself performs:

```python
# Conceptually wrong architecture
rows = load_500_gb_dataset()
transform_everything(rows)
```

Instead:

```text
Scheduler
   ↓
launch transformation task
   ↓
worker / external compute
   ↓
data processing
```

---

# 8. Scheduler Responsibilities

| Responsibility | Explanation |
|---|---|
| Scheduling | Determines when workflow work becomes eligible |
| Dependency evaluation | Determines whether prerequisites are satisfied |
| Concurrency | Prevents unrestricted execution |
| Dispatch coordination | Moves eligible work toward execution |
| State coordination | Uses orchestration state to understand current progress |
| Recovery coordination | Responds to task/run state changes |

The scheduler is therefore a **control-plane component**.

It is concerned with:

```text
What should happen?
When can it happen?
Is it allowed to happen?
Where should execution be dispatched?
```

The worker is concerned with:

```text
Actually do the work.
```

---

# 9. DAG Processor

The DAG Processor is a critical Airflow 3.x architectural concept.

Its responsibility is to process DAG source code into workflow definitions that Airflow can use.

A simplified lifecycle is:

```text
DAG Python file
      ↓
Python imports
      ↓
DAG objects / definitions created
      ↓
DAG definition processed
      ↓
Airflow can reason about the workflow
```

## 9.1 Why separate parsing from scheduling?

Consider a deployment with many DAG files.

If scheduling logic had to repeatedly perform expensive source-code processing itself, the scheduler could become overloaded.

Separating parsing gives the architecture a clearer boundary:

```text
DAG Processor
    ↓
understand source

Scheduler
    ↓
make scheduling decisions
```

This separation is especially important as the number and complexity of DAGs increase.

---

# 10. DAG Parsing

DAG parsing is one of the most important operational concepts for Airflow engineers.

A DAG is source code.

That means Airflow has to process Python code to understand the workflow definition.

## 10.1 Why top-level DAG code must be fast

Consider:

```python
import requests

response = requests.get(
    "https://api.example.com/config"
)

CONFIG = response.json()
```

This code executes while the Python module is being imported.

That means DAG processing can now depend on:

```text
network availability
API latency
API authentication
API rate limits
API failures
response size
```

This is dangerous.

### Possible consequences

```text
slow external API
      ↓
slow DAG processing
      ↓
DAG availability delayed
      ↓
scheduling decisions delayed
```

Repeated parsing can also generate repeated external traffic.

## 10.2 Better principle

Prefer lightweight DAG-definition code:

```python
CONFIG = {
    "source": "orders"
}
```

Then perform external operations during task execution when appropriate.

Conceptually:

```text
DAG parsing
    ↓
describe the work

Task execution
    ↓
perform the work
```

---

# 11. Parse-Time Network Calls

Avoid architecture such as:

```python
# Bad pattern for DAG module import
config = requests.get(
    "https://config-service.internal/config"
).json()
```

Why?

Because DAG processing now depends on another service.

Potential failure chain:

```text
Config service unavailable
        ↓
DAG import fails or slows
        ↓
DAG processing is affected
        ↓
Scheduler has less usable workflow information
```

A task can often safely contain an external operation because task execution is the intended place for workload-side effects.

The exact configuration mechanism depends on the Airflow version and provider environment.

---

# 12. Parse-Time Database Calls

Avoid:

```python
# Bad conceptual pattern
rows = database.execute(
    "SELECT configuration FROM config"
)
```

at module import time.

This introduces:

```text
DAG parsing
   ↓
database connection
   ↓
database latency/failure
```

into the control plane.

It also creates unnecessary database traffic when DAG source is repeatedly processed.

A better architecture is to keep the DAG definition lightweight and retrieve operational data as part of task execution where the requirement actually belongs there.

---

# 13. Heavy Imports

Consider:

```python
import massive_ml_library
```

at module level.

A heavyweight import may increase:

- CPU usage;
- memory consumption;
- import time;
- parser latency;
- parser throughput pressure.

The principle is:

> **DAG definition code should be lightweight. Expensive work belongs in task execution.**

This does not mean every import is forbidden.

The engineering question is:

```text
Does this import materially increase DAG processing cost?
```

If yes, consider whether it is necessary during DAG definition.

---

# 14. Top-Level Computation

This is also problematic:

```python
result = expensive_calculation()
```

at DAG import time.

The intended architecture is:

```python
from airflow.sdk import task

@task
def expensive_calculation():
    ...
```

The example is intentionally conceptual.

The distinction is:

```text
Import time
    ↓
define the workflow

Task execution time
    ↓
perform expensive work
```

This is one of the most important Airflow habits to develop.

---

# 15. DAG Folders

A common deployment model contains a:

```text
dags/
```

location.

Conceptually:

```text
deployment source
      ↓
DAG source files
      ↓
DAG processing
```

The exact source-delivery mechanism can vary.

The important architectural questions are:

- Where does DAG source live?
- How is it delivered to the Airflow environment?
- Which component processes it?
- How are source changes deployed?
- How can an operator identify the exact version of workflow code involved?

Do not assume every production platform uses one local directory in exactly the same way.

---

# 16. DAG Bundles

Airflow 3 introduces newer DAG source-delivery concepts, including **DAG bundles**.

The architectural idea is important even when implementation details vary:

> Airflow needs a reliable way to make DAG source available to the components responsible for processing workflow definitions.

Compare two conceptual models.

### Traditional directory-oriented model

```text
DAG files
   ↓
shared / mounted DAG directory
   ↓
DAG processing
```

### Bundle-oriented source delivery

```text
DAG source package / bundle
          ↓
Airflow source-delivery mechanism
          ↓
DAG processing
```

The key engineering concern is not the folder name.

It is **source delivery, consistency, traceability, and reproducibility**.

Do not invent provider-specific bundle configuration from memory. Use the documentation for the installed Airflow 3.x release.

---

# 17. Airflow 3 DAG Versioning

Version awareness matters because DAG source can change while historical workflow runs remain important.

Suppose:

```text
Monday:
    transform_v1

Wednesday:
    transform_v2
```

A production engineer needs to understand:

```text
Which workflow definition was active?
What changed?
Which historical runs used which definition?
Can the behavior be reproduced?
```

DAG versioning concepts support:

- reproducibility;
- deployment traceability;
- debugging;
- auditability;
- historical interpretation.

Do not confuse:

```text
DAG source versioning
```

with:

```text
task result versioning
```

They are related but different concerns.

---

# 18. API Server

In Airflow 3.x, the **API Server** is the current architectural component for supported operational API/UI access.

Conceptually:

```text
Operator
    ↓
UI / REST API
    ↓
API Server
    ↓
Airflow services / supported interfaces
```

The API Server provides operational access such as:

- UI interaction;
- API requests;
- inspecting workflow state;
- triggering operational actions through supported interfaces;
- inspecting task/run information;
- supported log access.

The UI and API are different interfaces to the operational platform even though they are served through the API Server architecture.

---

# 19. Airflow 2.x Webserver vs Airflow 3.x API Server

| Airflow 2.x / legacy terminology | Airflow 3.x current focus |
|---|---|
| `webserver` | API Server |
| webserver-centric operational architecture | API Server architecture |
| older task-side patterns | newer task SDK / supported API model |

This is a conceptual comparison.

Do not conclude that every older API disappeared identically across every release.

The practical lesson is:

> **Always verify the documentation version before copying Airflow code from a tutorial.**

---

# 20. Triggerer

The Triggerer exists to support efficient asynchronous waiting.

Consider a task that must wait for:

```text
file
API event
external condition
resource
time-based condition
```

A naive model is:

```text
Worker
   ↓
wait two hours
```

The worker is occupied while doing little useful work.

A deferred architecture is conceptually:

```text
Task
  ↓
defer
  ↓
Triggerer waits asynchronously
  ↓
condition occurs
  ↓
task resumes
```

This improves worker-slot efficiency for workloads dominated by waiting.

## 20.1 What the Triggerer does

It is designed for:

- asynchronous waiting;
- deferred tasks;
- efficient monitoring of waiting conditions.

It is not a replacement for the worker.

Do not confuse:

```text
Triggerer
    = waits efficiently
```

with:

```text
Worker
    = performs task work
```

Detailed sensor and deferrable-operator implementation belongs later in the orchestration curriculum.

---

# 21. Executor

The executor is the abstraction between:

```text
scheduler
```

and:

```text
execution environment
```

Conceptually:

```text
Scheduler
    ↓
Executor
    ↓
Execution environment
```

The executor helps determine how eligible task execution is dispatched.

Why have this abstraction?

Because Airflow can use different execution models without changing the fundamental workflow definition.

Examples include:

```text
local execution
distributed worker execution
Kubernetes-oriented execution
```

Executor choice therefore influences:

- deployment topology;
- scaling;
- isolation;
- infrastructure;
- operational complexity;
- cost.

---

# 22. Local Execution

The simplest conceptual model is:

```text
Scheduler
    ↓
Local execution model
    ↓
same machine / local processes
```

Advantages:

- simple;
- easy to understand;
- useful for learning;
- useful for small environments;
- low infrastructure overhead.

Trade-offs:

- limited horizontal scale;
- shared machine resources;
- less isolation;
- weaker fit for large distributed workloads.

Use local execution to learn the architecture before adding distributed infrastructure.

---

# 23. Celery-Style Distributed Execution

A distributed worker model can look like:

```text
                 ┌── Worker 1
Scheduler
    ↓            ├── Worker 2
Executor
    ↓            └── Worker 3
distributed task delivery
```

The important idea is:

> Eligible tasks can be distributed across multiple worker processes or machines.

Benefits include:

- parallel execution;
- horizontal worker scaling;
- separation of control plane and worker capacity.

Trade-offs include:

- more infrastructure;
- worker lifecycle management;
- messaging/distribution dependencies;
- network considerations;
- monitoring complexity.

This section is conceptual; full Celery configuration is outside the scope of this architecture lesson.

---

# 24. Kubernetes-Based Execution

A Kubernetes-oriented model is:

```text
Airflow
   ↓
Kubernetes
   ↓
task execution environment
```

Potential advantages:

- containerized execution;
- isolation;
- elastic capacity;
- integration with an existing Kubernetes platform.

Trade-offs:

- Kubernetes operational complexity;
- networking;
- image management;
- secrets;
- scheduling interactions;
- observability;
- cost.

Kubernetes should be selected because its capabilities solve a real deployment requirement, not because “Kubernetes is always better.”

---

# 25. Executor Comparison

| Model | Simple idea | Advantages | Trade-offs |
|---|---|---|---|
| Local | Execute locally | Simple, low infrastructure | Limited scale |
| Celery-style | Distributed workers | Flexible worker scaling | More infrastructure |
| Kubernetes | Containerized distributed execution | Isolation and elastic execution | Kubernetes complexity |

Selection depends on:

```text
workload
team expertise
existing infrastructure
scale
isolation requirements
cost
operational maturity
```

There is no universally correct executor.

---

# 26. Workers

A worker is an execution environment that performs task work.

Conceptually:

```text
Task instance
    ↓
Worker / execution environment
    ↓
Python process / container / external job
    ↓
result + state + logs
```

A worker consumes resources such as:

- CPU;
- memory;
- disk;
- network;
- external connections.

For example:

```text
Airflow task
    ↓
worker
    ↓
run Python extraction
    ↓
call API
    ↓
write object storage
```

The worker is where the task workload actually happens.

---

# 27. Worker Failure

Workers are infrastructure and can fail.

Examples:

```text
process crash
network loss
out-of-memory termination
container termination
machine failure
resource exhaustion
```

The architecture must therefore separate:

```text
task state
```

from:

```text
worker process lifetime
```

A worker disappearing does not mean the orchestration platform should lose all knowledge of the task.

Airflow's orchestration state allows the platform to reason about what happened and support recovery mechanisms.

Detailed retry and failure-policy design belongs to a later topic.

---

# 28. Metadata Database

The metadata database is one of the most important Airflow components.

Its role is to store **operational orchestration metadata**.

Conceptually:

```text
DAG/run metadata
task instance state
timestamps
dependencies / scheduling metadata
execution history
configuration metadata
connections/variables metadata depending on setup
```

PostgreSQL is the primary production-oriented example for this learning path.

## 28.1 What the metadata database is not

It is not:

```text
a data warehouse
an object store
a Spark data lake
a pipeline dataset store
```

Do not put large business datasets into the Airflow metadata database.

Instead:

```text
Airflow metadata DB
    ↓
orchestration state

Object storage / warehouse / database
    ↓
business data
```

This separation is fundamental.

---

# 29. Why PostgreSQL?

A production-oriented local architecture should teach with PostgreSQL rather than relying only on SQLite.

The important reasons include:

- concurrent access;
- transactional behavior;
- multi-process architecture;
- more production-like deployment characteristics;
- stronger representation of a real metadata service.

SQLite can be useful for constrained experiments, but PostgreSQL is the appropriate target for production-oriented learning.

Conceptually:

```text
Learning shortcut
    SQLite

Production-oriented architecture
    PostgreSQL
```

---

# 30. Metadata Database Load

The metadata database can become a bottleneck.

Load can grow with:

```text
more DAGs
+
more task instances
+
more state changes
+
more scheduler activity
+
more concurrent components
=
more metadata DB pressure
```

Symptoms can include:

```text
slow UI
slow API responses
delayed scheduling
connection exhaustion
database latency
```

The engineering response requires examining:

- CPU;
- memory;
- storage;
- indexes;
- connections;
- query patterns;
- retention;
- workload volume.

Do not manually mutate Airflow metadata tables as a normal operational practice.

---

# 31. Airflow 3 Task Execution Model

A major architectural distinction is that Airflow 3.x moves task-side interaction toward a **task SDK / supported API model** rather than treating direct metadata-database manipulation by task code as the preferred architecture.

Conceptually:

```text
Task
  ↓
Airflow task SDK / supported API path
  ↓
Airflow services / API Server
```

rather than:

```text
Task
  ↓
directly manipulate metadata database
```

The architectural value of this separation is:

- clearer boundaries;
- less coupling;
- safer interfaces;
- controlled access;
- API-driven architecture.

Do not invent low-level protocol details.

The key rule is:

> **Application/task code should use supported Airflow interfaces rather than treating the internal metadata database as an application API.**

---

# 32. Complete DAG-to-Task Lifecycle

Consider a small Airflow 3.x DAG:

```python
from airflow.sdk import dag, task

@dag
def orders_pipeline():

    @task
    def extract():
        return "orders"

    @task
    def transform(data):
        return f"transformed-{data}"

    @task
    def publish(data):
        print(data)

    raw = extract()
    transformed = transform(raw)
    publish(transformed)

orders_pipeline()
```

This example is intentionally small.

The purpose is not to teach the complete TaskFlow API. The purpose is to trace the architecture.

## Step 1 — DAG source exists

The Python file is delivered to the Airflow environment.

```text
DAG source
```

## Step 2 — DAG Processor discovers and parses it

The DAG Processor processes the Python module.

```text
Python source
    ↓
imports
    ↓
DAG definition
```

## Step 3 — Airflow recognizes the workflow definition

Airflow now has a workflow definition it can reason about.

Conceptually:

```text
extract
   ↓
transform
   ↓
publish
```

## Step 4 — Scheduler determines a DAG run should occur

Scheduling rules make a workflow run eligible.

## Step 5 — Task instances are created/managed

The logical workflow becomes concrete task instances associated with the run.

Conceptually:

```text
DAG run
 ├── extract task instance
 ├── transform task instance
 └── publish task instance
```

## Step 6 — Dependencies are evaluated

`transform` cannot run until its upstream requirement is satisfied.

```text
extract
   ↓
transform
   ↓
publish
```

## Step 7 — Runnable tasks are selected

The scheduler identifies work that is eligible and permitted to execute.

## Step 8 — Executor participates in dispatch

The executor coordinates how the task reaches the execution environment.

## Step 9 — Worker executes the task

A worker or other execution environment performs:

```text
extract()
```

## Step 10 — Logs are produced

The task emits:

```text
stdout
stderr
application logs
Airflow task logs
```

These may be stored locally and/or remotely.

## Step 11 — Task state is reported

The orchestration layer learns whether the task completed successfully or failed.

## Step 12 — Metadata is updated

Operational state is recorded in the metadata system.

## Step 13 — Scheduler evaluates downstream dependencies

After `extract` becomes successful:

```text
transform
```

may become eligible.

## Step 14 — Downstream work proceeds

The same control flow repeats:

```text
scheduler
   ↓
executor
   ↓
worker
   ↓
task
   ↓
logs + state
   ↓
metadata
```

---

# 33. End-to-End Architecture Diagram

```text
                         DAG SOURCE CODE
                              │
                              ▼
                    ┌───────────────────┐
                    │   DAG Processor   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     Scheduler     │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
             Metadata DB            Executor
                    ▲                   │
                    │                   ▼
                    │                Workers
                    │                   │
                    │                   ▼
                    │              Task Process
                    │                   │
                    └───────────┬───────┘
                                │
                                ▼
                              Logs


                    ┌───────────────────┐
                    │    API Server     │
                    │     UI + REST     │
                    └─────────┬─────────┘
                              │
                              ▼
                         Metadata DB


                    ┌───────────────────┐
                    │     Triggerer     │
                    │  async waiting    │
                    └───────────────────┘
```

### Read every arrow carefully

```text
DAG source → DAG Processor
```

means:

> workflow source must be processed into definitions Airflow understands.

```text
DAG Processor → Scheduler
```

means:

> scheduling operates using processed workflow information.

```text
Scheduler → Executor
```

means:

> eligible work is moved toward execution.

```text
Executor → Workers
```

means:

> execution is dispatched according to the selected execution model.

```text
Workers → Task Process
```

means:

> the execution environment performs the actual task workload.

```text
Task Process → Logs
```

means:

> task execution produces operational evidence.

```text
Components ↔ Metadata DB
```

means:

> orchestration services depend on persistent operational state.

```text
API Server → Metadata DB / supported services
```

means:

> operators and API clients access Airflow through supported operational interfaces.

```text
Triggerer
```

means:

> waiting workloads can be handled asynchronously rather than occupying workers unnecessarily.

---

# 34. Providers

Airflow providers extend Airflow with integrations to external systems.

Examples include:

```text
PostgreSQL
AWS
GCP
Azure
Kubernetes
HTTP
SFTP
Slack
```

Conceptually:

```text
Airflow Core
     +
Provider package
     ↓
External system integration
```

Providers can supply integrations such as:

- operators;
- hooks;
- authentication mechanisms;
- external-system interfaces.

Provider versions matter.

Therefore, version-aware troubleshooting should include:

```text
Airflow version
provider version
Python version
```

Do not assume a tutorial written for one provider release is automatically correct for another.

---

# 35. Logging

Task execution produces logs.

A simplified flow is:

```text
Task starts
    ↓
stdout / stderr / logging
    ↓
task logs
```

Logs are essential for:

- debugging;
- incident response;
- retry diagnosis;
- root-cause analysis;
- operational support.

A task state such as:

```text
FAILED
```

tells you **that** something failed.

The task log often helps explain **why**.

---

# 36. Local vs Remote Logging

Local logging:

```text
Worker
  ↓
local filesystem
```

can be sufficient for a development environment.

But consider:

```text
Worker executes task
        ↓
worker disappears
```

If operational logs exist only on ephemeral worker storage, retrieving them can become difficult.

Remote logging changes the architecture:

```text
Worker
  ↓
remote log storage
  ↓
operator / UI
```

Remote logging provides durable operational evidence outside the worker's local lifecycle.

---

# 37. MinIO as a Local Remote-Logging Lab

MinIO is useful for local learning because it can provide S3-compatible object storage behavior without requiring a cloud account.

Conceptually:

```text
Airflow
   ↓
Task worker
   ↓
MinIO bucket
   ↓
Remote logs
```

The exact Airflow/provider configuration is version-dependent.

Do not copy an environment-variable example blindly from an Airflow 2.x tutorial.

For the installed Airflow 3.x release:

1. identify the Airflow version;
2. identify the relevant provider version;
3. read the current remote-logging documentation;
4. configure the supported object-storage integration;
5. run a task;
6. verify that logs are retrievable after the task completes.

The architectural lesson is more important than memorizing configuration keys.

---

# 38. Local Airflow Architecture

A learning environment can conceptually contain:

```text
Docker Compose
│
├── Airflow API Server
├── Scheduler
├── DAG Processor
├── Triggerer
├── Worker / execution service
├── PostgreSQL
└── MinIO
```

Each service has a different purpose.

| Service | Learning purpose |
|---|---|
| API Server | UI/API access |
| Scheduler | Scheduling decisions |
| DAG Processor | DAG parsing |
| Triggerer | Deferred/asynchronous waiting |
| Worker | Task execution |
| PostgreSQL | Metadata persistence |
| MinIO | Remote log storage |

The exact official Compose topology may change between Airflow releases.

Therefore:

> **Use the official Airflow 3.x Compose configuration for the installed release rather than copying an Airflow 2.x Compose file.**

---

# 39. `airflow standalone`

For learning and experimentation, Airflow provides:

```bash
airflow standalone
```

This is useful because it can demonstrate a working Airflow environment with less setup.

It is valuable for:

- first experiments;
- understanding basic components;
- learning the UI/API;
- running a minimal DAG.

But:

> `airflow standalone` is a learning/development convenience, not a production architecture.

Production-oriented learning should also teach a deliberate PostgreSQL-backed topology and explicit service boundaries.

---

# 40. Docker Compose Architecture Lab

The learning environment for this topic is:

```text
Airflow 3.x
+
Docker Compose
+
PostgreSQL
+
MinIO
```

The goal is not merely to “make Airflow run.”

The goal is to identify the architecture.

## Lab objectives

You should be able to:

1. start Airflow;
2. verify API Server/UI access;
3. verify scheduler operation;
4. verify DAG processing;
5. verify PostgreSQL;
6. create a minimal DAG;
7. run the DAG;
8. inspect task state;
9. inspect task logs;
10. identify which components participated.

Use the official documentation for the exact Compose commands and configuration for the installed Airflow 3.x release.

---

# 41. Build a Minimal Airflow 3 DAG

A small architecture-tracing DAG can use current Airflow 3.x SDK conventions:

```python
from airflow.sdk import dag, task


@dag
def orders_pipeline():

    @task
    def extract():
        return "orders"

    @task
    def transform(data):
        return f"transformed-{data}"

    @task
    def publish(data):
        print(data)

    raw = extract()
    transformed = transform(raw)
    publish(transformed)


orders_pipeline()
```

This is intentionally small.

It demonstrates:

```text
extract
   ↓
transform
   ↓
publish
```

It is **not** a complete TaskFlow tutorial.

---

# 42. Trace the Minimal DAG

When the DAG file is saved, ask these questions.

### Question 1 — What discovers the source?

The DAG source must become available to the DAG processing mechanism.

### Question 2 — What parses it?

The DAG Processor processes the Python source.

### Question 3 — What does parsing produce?

A workflow definition Airflow can reason about.

### Question 4 — When does the scheduler become involved?

When Airflow needs to determine workflow/task eligibility.

### Question 5 — Where does the run appear?

The orchestration state associated with the workflow run is maintained by Airflow's metadata architecture.

### Question 6 — When does a task become runnable?

After its dependencies and scheduling/concurrency constraints permit execution.

### Question 7 — How is it dispatched?

Through the selected executor model.

### Question 8 — Where does it execute?

On the selected worker/execution environment.

### Question 9 — Where are logs generated?

During task execution.

### Question 10 — Where is task state recorded?

Through Airflow's supported orchestration architecture and metadata services.

### Question 11 — How does downstream execution begin?

The scheduler evaluates the new state and downstream eligibility.

This is the architecture you should be able to explain without memorizing implementation trivia.

---

# 43. Inspect the Metadata Database

The metadata database is useful for learning because it makes orchestration state concrete.

Use PostgreSQL in the learning environment.

The safe learning workflow is:

```text
connect
   ↓
inspect schemas
   ↓
inspect tables
   ↓
read metadata
   ↓
compare before/after task execution
```

Use read-only inspection queries.

Do **not** manually mutate Airflow metadata tables as a normal operating procedure.

A good experiment is:

```text
Before DAG run
    ↓
record relevant metadata observations

Run DAG
    ↓
observe task state changes

After DAG run
    ↓
compare metadata
```

Exact table names and schemas can change between releases.

Therefore, inspect the schema of the installed Airflow 3.x version instead of hard-coding assumptions from an older tutorial.

---

# 44. Measure DAG Parse Performance

Parsing performance should be observable.

A deliberately slow example:

```python
import time

time.sleep(5)
```

at module level is useful as a controlled experiment.

It demonstrates:

```text
top-level delay
    ↓
DAG parsing delay
```

Do not leave such code in a production DAG.

## Experiment

Create two conceptual versions.

### Version A — slow

```python
import time

time.sleep(5)

# DAG definition follows
```

### Version B — lightweight

```python
# DAG definition contains only lightweight construction.
```

Compare:

```text
slow parse time
vs
optimized parse time
```

Then ask:

```text
What happens if there are 1 DAG?
What happens if there are 100 DAGs?
What happens if there are 1,000 DAGs?
```

The point is to understand how small parse-time inefficiencies multiply across a platform.

---

# 45. Parse-Time Anti-Patterns

| Anti-pattern | Why it is dangerous | Safer conceptual alternative |
|---|---|---|
| API request at import time | Network latency/failure affects parsing | Perform external work during task execution |
| DB query at import time | DB dependency during parsing | Query from task execution when appropriate |
| Heavy ML import | Higher parser CPU/memory cost | Keep DAG definition lightweight |
| Large computation | CPU wasted during parsing | Execute computation as a task |
| Large filesystem scan | Slow source processing | Move expensive discovery into task execution where appropriate |
| Secrets retrieval at parse time | Availability/security coupling | Use supported runtime secret/config mechanisms |
| Dynamic expensive configuration | Unpredictable parse cost | Keep definition deterministic and lightweight |

---

# 46. Scaling Airflow

Start with:

```text
One Airflow deployment
```

Then increase:

```text
number of DAGs
number of task instances
number of runs
number of workers
number of scheduling decisions
number of users/API clients
```

Different components become bottlenecks at different points.

The major scaling dimensions are:

```text
DAG parsing
Scheduler
Metadata database
Executor
Workers
API Server
Logs
Triggerer
```

This leads to a central production lesson:

> **Airflow is not one process that simply gets “bigger.” It is a system whose components have different scaling characteristics.**

---

# 47. DAG Parsing Scaling

Thousands of DAGs can create significant parsing pressure.

Important factors include:

- number of DAG files/source bundles;
- DAG complexity;
- import cost;
- top-level operations;
- filesystem/source delivery behavior;
- parse frequency;
- external calls during parsing.

A logically correct DAG can still be operationally poor if it is expensive to parse.

Think:

```text
N DAGs
×
parse cost per DAG
×
parse frequency
=
parser workload
```

This is why lightweight DAG definitions are a production concern, not merely a style preference.

---

# 48. Scheduler Scaling

As scheduling workload increases:

```text
more DAGs
+
more runs
+
more task instances
+
more state transitions
```

the scheduler has more coordination work.

Airflow can support multiple schedulers in architectures where additional scheduler capacity/availability is required.

Conceptually:

```text
Scheduler 1 ─┐
Scheduler 2 ─┼── Metadata DB
Scheduler 3 ─┘
```

The metadata database becomes particularly important because multiple scheduling components need a consistent orchestration-state system.

Do not infer undocumented locking or internal coordination details from this conceptual diagram.

---

# 49. Metadata Database Scaling

More workflow activity generally produces more metadata activity:

```text
more DAGs
+
more task instances
+
more state changes
+
more schedulers/workers
=
more metadata DB load
```

Consider:

- connection capacity;
- CPU;
- memory;
- storage;
- indexes;
- query patterns;
- retention;
- transaction behavior.

Symptoms of pressure may include:

```text
slow scheduler
slow UI/API
connection exhaustion
high database latency
delayed state visibility
```

The metadata database deserves production-level capacity planning.

---

# 50. Worker Scaling

Worker capacity should follow workload characteristics.

Conceptually:

```text
Few independent tasks
      ↓
small worker capacity

Many independent tasks
      ↓
more worker capacity
```

Worker scaling can be:

```text
horizontal
```

by adding execution capacity, or:

```text
vertical
```

by increasing resources available to an execution environment.

Relevant resources include:

- CPU;
- memory;
- network;
- disk;
- concurrency capacity.

Queues, pools, and other execution controls can also influence how capacity is consumed; detailed configuration belongs to later topics.

---

# 51. API Server Scaling

The API Server can become an independent scaling concern.

Consider:

```text
many UI users
+
API clients
+
monitoring systems
+
automation
+
frequent status requests
```

This workload is different from task execution.

Therefore:

```text
worker scaling
```

does not automatically solve:

```text
API Server load
```

The same principle applies to every Airflow component:

> Scale the component that is actually under pressure.

---

# 52. Triggerer Scaling

If many tasks use asynchronous/deferred waiting, the Triggerer can become an important capacity dimension.

Monitor conceptually:

```text
deferred task volume
triggerer health
trigger processing performance
```

The Triggerer should not be confused with workers.

```text
Worker
    performs task work

Triggerer
    efficiently waits for deferred conditions
```

---

# 53. Architecture Failure Modes

Production architecture becomes easier to understand when you study failure.

---

## Failure 1 — DAG Parser Is Slow

### Symptoms

```text
DAG appears late
DAG changes are recognized slowly
scheduling is delayed
```

### Likely causes

```text
API call at import time
DB call at import time
heavy imports
large computation
large filesystem work
```

### Investigation

```text
source code
   ↓
parse timing
   ↓
parser logs
   ↓
external dependencies
```

### Better architecture

Keep DAG definitions lightweight.

---

## Failure 2 — Metadata Database Is Overloaded

### Symptoms

```text
slow UI
slow API
delayed scheduling
connection errors
high database latency
```

### Investigation

```text
DB CPU
DB memory
connections
storage
queries
scheduler behavior
```

### Architecture lesson

The metadata database is part of the control plane.

It must be sized as production infrastructure.

---

## Failure 3 — Worker Unavailable

### Symptoms

```text
task does not execute as expected
execution capacity decreases
task remains pending/blocked
```

### Investigation

```text
executor
   ↓
worker availability
   ↓
worker logs
   ↓
resource capacity
```

The exact observed state depends on the execution model and failure mode.

---

## Failure 4 — Remote Logs Unavailable

### Symptoms

```text
task may have executed
but logs cannot be retrieved normally
```

### Investigation

```text
task state
worker
remote storage
provider/integration
network
credentials
```

### Architecture lesson

Execution success and log-storage availability are related but distinct concerns.

---

## Failure 5 — API Server Unavailable

### Symptoms

```text
UI/API access degraded
operators cannot use normal operational interfaces
```

Other components may continue performing some control-plane functions depending on the deployment and failure state.

Do not assume:

```text
API Server down = every Airflow process instantly stops
```

The actual failure boundary depends on the architecture.

---

# 54. Debugging Airflow Architecture

Use a layered approach.

```text
DAG missing?
    ↓
Check DAG source / bundle
    ↓
Check DAG processing
    ↓
Check parser errors
    ↓
Check scheduler
    ↓
Check metadata DB
    ↓
Check task state
    ↓
Check executor
    ↓
Check worker
    ↓
Check task logs
```

This prevents random troubleshooting.

Instead of asking:

> “Why is Airflow broken?”

ask:

> “Which architectural boundary failed?”

---

# 55. Debugging Playbook

Use:

```text
Symptom
   ↓
Likely component
   ↓
Evidence
   ↓
Check
   ↓
Diagnosis
   ↓
Remediation
```

## DAG missing

Check:

```text
DAG source delivery
DAG bundle/source
DAG Processor
parse errors
version/documentation mismatch
```

## DAG parses slowly

Check:

```text
top-level API calls
top-level DB calls
heavy imports
top-level computation
large file scans
```

## Task stuck before execution

Check:

```text
task state
dependencies
concurrency/capacity
scheduler
executor
worker availability
```

## Task never starts

Trace:

```text
scheduler
   ↓
executor
   ↓
execution environment
```

## Worker unavailable

Check:

```text
worker health
resources
network
container/process lifecycle
executor behavior
```

## Task failed

Check:

```text
task state
task logs
worker
external dependency
input/output conditions
```

## Logs missing

Check:

```text
worker logs
local storage
remote logging configuration
object storage
provider
network/authentication
```

## Scheduler slow

Check:

```text
DAG parse pressure
metadata DB
number of DAGs/runs/tasks
scheduler resource usage
```

## Metadata DB overloaded

Check:

```text
connections
CPU
memory
storage
query latency
workload volume
```

## API Server unavailable

Check:

```text
service health
network
authentication
resource utilization
deployment topology
```

## Triggerer problem

Check:

```text
Triggerer health
deferred workload volume
logs
resource usage
```

---

# 56. Architecture Observability

A production Airflow platform should observe each major component.

## Scheduler

Monitor conceptually:

- scheduling latency;
- health;
- loop performance;
- resource usage.

## DAG Processor

Monitor:

- parse duration;
- parse failures;
- import errors;
- source-processing health.

## Metadata Database

Monitor:

- connection count;
- query latency;
- CPU;
- memory;
- storage;
- query load.

## Workers

Monitor:

- CPU;
- memory;
- task duration;
- failure rate;
- execution capacity.

## API Server

Monitor:

- request latency;
- availability;
- error rate;
- resource usage.

## Triggerer

Monitor:

- health;
- deferred workload volume;
- processing performance.

Do not confuse this architecture lesson with a complete observability curriculum. The objective here is to know **what each component needs to expose for troubleshooting**.

---

# 57. Recognizing Outdated Airflow Tutorials

You may encounter older examples such as:

```python
from airflow import DAG
```

or commands and concepts involving:

```text
airflow webserver
execution_date
Dataset
SubDAG
direct metadata DB access
```

These may be legitimate **Airflow 2.x / legacy** material.

Do not automatically assume they describe the current Airflow 3.x architecture.

Before using an online tutorial, verify:

```text
Airflow version
documentation version
provider version
Python version
```

A practical workflow is:

```text
Find tutorial
   ↓
Identify version
   ↓
Compare with installed version
   ↓
Read current documentation
   ↓
Adapt only after confirming compatibility
```

---

# 58. Airflow 2.x / Legacy Architecture vs Airflow 3.x

The following is intentionally conceptual.

### Older Airflow 2.x style

```text
DAGs
 ↓
Scheduler
 ↓
Executor
 ↓
Workers

Webserver
 ↓
Metadata DB
```

### Airflow 3.x architectural focus

```text
DAG Source
 ↓
DAG Processor
 ↓
Scheduler
 ↓
Executor
 ↓
Workers

API Server
 ↓
supported API / UI access

Triggerer
 ↓
deferred/asynchronous waiting

Metadata DB
 ↓
operational state
```

Important evolution themes include:

```text
separated DAG processing
API Server architecture
task SDK / supported API model
Assets terminology
scheduler-managed operational workflows
```

This is not a complete migration guide.

The purpose is to prevent version confusion.

---

# 59. Assets Terminology

Older Airflow material may use:

```text
Dataset
```

Airflow 3.x uses the newer:

```text
Asset
```

terminology/model.

The conceptual purpose is to express relationships between workflows and data-producing/consuming events or entities.

The important learning habit is:

> When a tutorial uses older Dataset terminology, check the Airflow version before applying the example.

Detailed data-aware scheduling and Asset implementation belong to a later topic.

---

# 60. Scheduler-Managed Backfills

Airflow 3.x architecture also places greater emphasis on scheduler-managed workflow execution behavior, including backfill coordination.

At the architecture level, understand the distinction:

```text
historical workflow work
       ↓
Airflow scheduling/control plane
       ↓
task eligibility and execution
```

Do not turn this topic into a detailed backfill tutorial.

Backfills, catch-up, and partitioned runs are covered later.

---

# 61. Airflow 3 Architectural Principles

The architecture can be summarized as:

```text
API-driven architecture
Separated DAG parsing
Separated scheduling
Separated execution
Asynchronous waiting
Distributed execution
Metadata-backed state
Version-aware DAG management
Provider-based integrations
Remote logging
```

### API-driven architecture

Operational interactions use supported APIs rather than treating internal storage as a public interface.

### Separated DAG parsing

Source processing is separated from scheduling responsibilities.

### Separated scheduling

The scheduler decides what should happen.

### Separated execution

Workers/execution environments perform the work.

### Asynchronous waiting

The Triggerer can handle deferred waiting efficiently.

### Distributed execution

Task workloads can execute beyond one local process/machine.

### Metadata-backed state

The platform persists operational state.

### Version-aware DAG management

Workflow source changes need traceability and reproducibility.

### Provider-based integrations

External systems are connected through provider packages.

### Remote logging

Logs can survive individual worker lifecycles.

---

# 62. Production Deployment Models

## 62.1 Local development

```text
airflow standalone
```

Best for:

```text
learning
experimentation
quick local tests
```

Operational complexity:

```text
low
```

Production suitability:

```text
not the target
```

## 62.2 Docker Compose

```text
Docker Compose
+
PostgreSQL
+
Airflow services
+
optional MinIO
```

Useful for:

```text
local architecture labs
development
team experimentation
```

It can expose real component boundaries without requiring a Kubernetes cluster.

## 62.3 Kubernetes

```text
Airflow
   ↓
Kubernetes
   ↓
execution environments
```

Useful when the organization already operates Kubernetes and requires:

- containerized workloads;
- isolation;
- elastic execution;
- platform-level scheduling.

Operational complexity is higher.

## 62.4 Managed Airflow

Managed Airflow shifts some infrastructure responsibilities to a cloud/platform provider.

Potential responsibilities affected include:

```text
control-plane operations
upgrades
scaling
availability
security integration
```

Trade-offs include:

```text
cost
vendor coupling
platform constraints
reduced infrastructure ownership
```

Do not assume managed Airflow is universally appropriate.

---

# 63. Kubernetes Deployment Concept

A production Kubernetes-oriented architecture may conceptually contain:

```text
                ┌─────────────────┐
                │   API Server    │
                └─────────────────┘

                ┌─────────────────┐
                │    Scheduler    │
                └─────────────────┘

                ┌─────────────────┐
                │  DAG Processor  │
                └─────────────────┘

                       │
                       ▼

                ┌─────────────────┐
                │   Execution     │
                │   environments  │
                └─────────────────┘

                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        PostgreSQL          Object storage
        metadata            / remote logs
```

Also consider:

```text
networking
secrets
authentication
authorization
persistent storage
container images
resource limits
monitoring
```

The official Airflow Helm chart is a production deployment option.

This lesson introduces the architecture; it does not teach Kubernetes administration or Helm installation syntax in depth.

---

# 64. Managed Airflow

Managed Airflow can be attractive when a Data Engineering team wants to reduce infrastructure ownership.

Potential advantages:

- reduced platform maintenance;
- provider-managed control-plane operations;
- integration with cloud infrastructure;
- easier alignment with managed services.

Potential trade-offs:

- service cost;
- provider-specific constraints;
- vendor coupling;
- upgrade policies;
- networking requirements;
- IAM/security integration;
- reduced control over infrastructure internals.

The right question is:

> Which operational responsibilities should the organization own?

not:

> Which platform is universally best?

---

# 65. Security Architecture

Airflow often has access to many systems.

Therefore, security must be treated as an architectural concern.

Cover at least:

- API authentication;
- authorization;
- secrets;
- network access;
- least privilege;
- database protection;
- worker isolation;
- logging sensitivity.

A useful principle is:

> **The orchestration layer can become a high-impact security boundary because it may be able to start work against many downstream systems.**

For example:

```text
Airflow
   ↓
AWS
PostgreSQL
SFTP
Kubernetes
APIs
Object storage
```

A compromised orchestration layer could potentially reach multiple systems.

Therefore:

```text
least privilege
+
secure secrets
+
network controls
+
strong authentication
+
auditable access
```

are architectural requirements.

---

# 66. What Airflow Should Not Do

Airflow should generally not become:

```text
data warehouse
ETL compute engine
Spark replacement
large in-memory data processor
persistent application database
message broker
object storage
```

Instead, Airflow should coordinate systems such as:

```text
PostgreSQL
dbt
Spark
S3 / MinIO
APIs
SFTP
Kubernetes
Python applications
```

Think:

```text
Airflow
    = conductor

External systems
    = musicians
```

The conductor coordinates.

The conductor should not attempt to play every instrument at once.

---

# 67. Hands-On Lab — Airflow Architecture Lab

## Lab environment

Use:

```text
Airflow 3.x
PostgreSQL
Docker Compose
MinIO
```

Use the official documentation for exact version-specific setup commands.

## Part 1 — Start Airflow

Goal:

```text
Airflow services running
PostgreSQL running
```

Record:

```text
Airflow version
Python version
provider versions
```

## Part 2 — Verify components

Identify:

```text
API Server
Scheduler
DAG Processor
Triggerer
worker/execution service
PostgreSQL
```

Create a table:

| Component | Running? | Evidence |
|---|---:|---|
| API Server | | |
| Scheduler | | |
| DAG Processor | | |
| Triggerer | | |
| Worker/execution service | | |
| PostgreSQL | | |

## Part 3 — Create a minimal DAG

Use the small `orders_pipeline` DAG from this lesson.

## Part 4 — Trace the architecture

Document:

```text
source
 ↓
DAG Processor
 ↓
Scheduler
 ↓
Executor
 ↓
Worker
 ↓
task
 ↓
logs/state
 ↓
metadata
```

## Part 5 — Inspect task state

Observe:

```text
queued/runnable behavior
running
success/failure
```

Use the UI/API rather than manually modifying metadata.

## Part 6 — Inspect PostgreSQL

Use read-only queries.

Document:

```text
What metadata exists?
What changes after a run?
Which state information can you observe?
```

## Part 7 — Inspect logs

Find:

```text
task log
execution timestamp
task output
failure information if applicable
```

## Part 8 — Remote logging

Configure/understand remote logging to MinIO using the current installed Airflow/provider documentation.

Verify:

```text
task runs
    ↓
log generated
    ↓
remote object created
    ↓
log remains retrievable
```

## Part 9 — Measure parsing

Create an intentionally slow top-level operation.

Measure the difference.

## Part 10 — Fix the slow DAG

Move expensive work out of import-time code.

## Part 11 — Failure injection

Perform controlled failures.

## Part 12 — Document the architecture

Produce a diagram showing:

```text
DAG source
DAG Processor
Scheduler
Executor
Worker
Triggerer
API Server
Metadata DB
Remote logs
External systems
```

---

# 68. Failure Injection Experiments

Failure experiments turn an abstract architecture into an operational mental model.

## Experiment 1 — Slow top-level code

Introduce:

```python
import time
time.sleep(5)
```

at module level.

Observe:

```text
DAG parsing behavior
```

Then remove it.

## Experiment 2 — Task failure

Make a task fail intentionally.

Trace:

```text
worker
  ↓
task state
  ↓
metadata
  ↓
scheduler
  ↓
downstream eligibility
```

Document what you observe.

## Experiment 3 — Remote log storage unavailable

Make remote log storage unavailable in a controlled local environment.

Observe:

```text
task execution
log availability
UI behavior
worker logs
```

Do not assume that log-storage failure means task execution itself failed.

## Experiment 4 — Stop a worker

Stop the execution environment during a controlled experiment.

Observe:

```text
task state
executor behavior
scheduler observations
recovery behavior
```

## Experiment 5 — Metadata before/after

Inspect relevant metadata before and after a task run.

Document:

```text
what changed
when it changed
which component caused the observable transition
```

---

# 69. Architecture Diagram Assignment

Draw the following:

```text
DAG Source
    ↓
DAG Processor
    ↓
Scheduler
    ↓
Executor
    ↓
Workers
    ↓
Task Work

Triggerer

API Server

Metadata DB

Remote Logs

External Systems
```

Then draw arrows showing:

```text
control flow
execution flow
state flow
log flow
operational access
```

## Reference solution

```text
                     DAG SOURCE
                         │
                         ▼
                 ┌───────────────┐
                 │ DAG Processor │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   Scheduler   │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   Executor    │
                 └───────┬───────┘
                         │
                         ▼
                    ┌─────────┐
                    │ Workers │
                    └────┬────┘
                         │
                         ▼
                    Task Work
                         │
                         ▼
                       Logs
                         │
                         ▼
                  Remote Storage


                 ┌────────────────┐
                 │   API Server   │
                 └───────┬────────┘
                         │
                         ▼
                    Metadata DB

                 ┌────────────────┐
                 │   Triggerer    │
                 └────────────────┘
```

---

# 70. Architecture Design Exercise 1 — Small Team

## Requirements

```text
20 DAGs
PostgreSQL
Docker
simple batch processing
```

Design:

```text
DAG source delivery
DAG processing
scheduler
executor
workers
metadata DB
logs
API access
```

### Questions

1. Which execution model would you consider?
2. Why?
3. What infrastructure is required?
4. Where do logs go?
5. What happens if the worker fails?
6. What is the likely first scaling concern?

There is no universal answer.

Your answer should explicitly state assumptions.

---

# 71. Architecture Design Exercise 2 — Medium Platform

## Requirements

```text
200 DAGs
multiple workers
remote logs
multiple teams
```

Design an architecture that considers:

```text
DAG source delivery
DAG Processor capacity
Scheduler capacity
worker scaling
metadata DB
remote logs
API Server
security boundaries
```

Questions:

1. Where are likely bottlenecks?
2. How would you observe them?
3. How would you separate team access?
4. How would you preserve logs?
5. What would trigger horizontal scaling?

---

# 72. Architecture Design Exercise 3 — Large Platform

## Requirements

```text
1,000+ DAGs
multiple schedulers
distributed workers
high metadata volume
```

Design:

```text
source delivery
DAG processing
scheduler topology
metadata DB
executor
worker fleet
API Server
remote logging
observability
```

Questions:

1. How would you reduce DAG parse pressure?
2. How would you monitor scheduler performance?
3. How would you size the metadata database?
4. How would you scale workers?
5. How would you diagnose a sudden scheduling delay?

---

# 73. Architecture Design Exercise 4 — Kubernetes Platform

## Requirements

```text
Kubernetes is already the company standard
dynamic task workloads
isolated execution
```

Design an architecture using:

```text
Airflow
Kubernetes
PostgreSQL
remote object storage
```

Discuss:

- execution isolation;
- scaling;
- networking;
- secrets;
- logs;
- operational ownership;
- failure modes.

Do not assume Kubernetes automatically solves every scaling problem.

---

# 74. Architecture Design Exercise 5 — Managed Platform

## Requirements

```text
small Data Engineering team
limited infrastructure expertise
high availability requirements
```

Evaluate whether managed Airflow fits the requirements.

Your analysis must include:

```text
operational responsibility
cost
security
availability
vendor coupling
customization
team expertise
```

Do not provide a universal winner.

The goal is architecture reasoning.

---

# 75. Common Airflow Architecture Mistakes

## 1. Heavy work at DAG parse time

### Why it happens

The developer confuses:

```text
define the workflow
```

with:

```text
execute the workflow
```

### Why dangerous

It increases parser workload and can introduce external dependencies.

### Better approach

Keep definitions lightweight.

---

## 2. Network calls at module import time

### Why it happens

Configuration is fetched while constructing the DAG.

### Why dangerous

DAG processing becomes dependent on network services.

### Better approach

Move runtime work into task execution or supported configuration mechanisms.

---

## 3. Database calls at parse time

### Why dangerous

Parsing becomes dependent on database availability and latency.

### Better approach

Keep the control-plane source definition lightweight.

---

## 4. Treating the metadata DB as a data warehouse

### Why dangerous

The metadata database is optimized for orchestration state, not large business datasets.

### Better approach

Store data in the appropriate warehouse/object store/database.

---

## 5. Running huge computations in scheduler processes

### Why dangerous

The scheduler is a coordination component.

### Better approach

Dispatch heavy work to the appropriate execution environment.

---

## 6. Assuming workers are always available

### Why dangerous

Workers can fail or run out of resources.

### Better approach

Design for observable, recoverable execution capacity.

---

## 7. Ignoring remote logs

### Why dangerous

Ephemeral workers can disappear.

### Better approach

Use durable remote logging where production requirements justify it.

---

## 8. Ignoring metadata DB scaling

### Why dangerous

Control-plane performance can degrade even when workers have plenty of capacity.

### Better approach

Monitor and capacity-plan the metadata database.

---

## 9. Using outdated Airflow 2 tutorials without checking the version

### Why dangerous

Architecture and APIs evolve.

### Better approach

Verify version compatibility before copying code.

---

## 10. Confusing API Server with older webserver terminology

### Why dangerous

It produces an incorrect mental model of Airflow 3.

### Better approach

Learn the current Airflow 3 architecture and label older material as legacy/reference.

---

## 11. Assuming every task should run on the same worker

### Why dangerous

Different workloads have different resource requirements.

### Better approach

Choose an execution model appropriate to workload and infrastructure.

---

## 12. Ignoring executor selection

### Why dangerous

Executor architecture affects scalability and deployment.

### Better approach

Treat execution strategy as an explicit architecture decision.

---

## 13. Ignoring provider versions

### Why dangerous

Provider APIs and integrations can be version-sensitive.

### Better approach

Check provider documentation for the installed version.

---

## 14. Treating `airflow standalone` as production architecture

### Why dangerous

It hides many deliberate production topology decisions.

### Better approach

Use it for learning, then study explicit PostgreSQL-backed production topology.

---

## 15. Designing Airflow without clear ownership

### Why dangerous

An Airflow platform touches:

```text
code
infrastructure
databases
secrets
cloud systems
networking
monitoring
```

### Better approach

Define ownership across:

```text
Data Engineering
Platform Engineering
Security
Infrastructure
```

where appropriate.

---

# 76. Interview Questions — Basic

## 1. What is Apache Airflow?

**Answer:** Airflow is a workflow orchestration platform that coordinates tasks, dependencies, scheduling, execution, state, and operational visibility.

## 2. What is the scheduler?

**Answer:** The scheduler determines which workflow/task work is eligible to proceed and coordinates dispatch toward execution.

## 3. What is a DAG Processor?

**Answer:** It processes DAG source code into workflow definitions that Airflow can use for orchestration.

## 4. What is a worker?

**Answer:** A worker or execution environment performs the actual task workload.

## 5. What is an executor?

**Answer:** The executor provides the execution-dispatch abstraction between scheduling decisions and the underlying execution environment.

## 6. What is the metadata database?

**Answer:** It stores operational orchestration state such as workflow/run/task metadata and execution history.

## 7. What is the API Server?

**Answer:** In Airflow 3.x it is the current architectural service providing supported UI and REST/API operational access.

## 8. What is the Triggerer?

**Answer:** It handles asynchronous/deferred waiting so workers do not have to remain occupied while waiting for external conditions.

## 9. What are Airflow providers?

**Answer:** Provider packages extend Airflow with integrations to external systems such as databases, cloud services, Kubernetes, HTTP, and SFTP.

## 10. Why does Airflow use multiple components?

**Answer:** Separation of responsibilities allows parsing, scheduling, execution, API access, asynchronous waiting, and metadata persistence to scale and fail more independently.

---

# 77. Interview Questions — Intermediate

## 1. What happens when Airflow discovers a DAG?

**Answer:** The DAG source becomes available to the DAG processing mechanism, which parses the Python source into a workflow definition that Airflow can use.

## 2. Why should top-level DAG code be lightweight?

**Answer:** DAG source is processed repeatedly. Expensive top-level work increases parsing latency and can affect the responsiveness of the orchestration control plane.

## 3. Why are API calls at DAG parse time dangerous?

**Answer:** They introduce external network availability and latency into DAG processing and may generate repeated traffic.

## 4. What does the executor do?

**Answer:** It coordinates how eligible task work is dispatched toward the underlying execution environment.

## 5. How does a worker participate in execution?

**Answer:** The worker receives or launches the task workload and performs the actual task computation.

## 6. Why is PostgreSQL preferred over SQLite for production-oriented deployments?

**Answer:** PostgreSQL better represents a concurrent, multi-process production metadata service and provides stronger production-oriented database characteristics.

## 7. What is remote logging?

**Answer:** Remote logging stores task logs outside the worker's local filesystem so logs remain operationally accessible when workers are ephemeral or replaced.

## 8. Why can the metadata database become a bottleneck?

**Answer:** Large numbers of DAGs, task instances, state changes, schedulers, and workers can increase database connections, queries, transactions, and storage pressure.

## 9. What does the Triggerer solve?

**Answer:** It enables efficient asynchronous waiting for deferred work instead of occupying worker capacity during long waits.

## 10. What is the difference between local and distributed execution?

**Answer:** Local execution keeps task execution close to one machine/process environment, while distributed execution spreads task workloads across multiple execution environments for greater capacity and isolation.

---

# 78. Interview Questions — Hard

## 1. Trace a task from DAG parsing to completion.

**Answer structure:**

```text
DAG source
→ DAG Processor
→ scheduler
→ DAG run/task instance
→ dependency evaluation
→ executor
→ worker
→ task execution
→ logs/state
→ metadata
→ downstream scheduling
```

The key is to explain what each boundary contributes.

## 2. How would you debug a DAG that appears late?

**Answer structure:**

```text
source delivery
→ DAG Processor
→ parse duration
→ import errors
→ scheduler health
→ metadata DB
```

First determine whether the delay is source discovery, parsing, scheduling, or metadata related.

## 3. How would you debug tasks stuck in queued state?

**Answer structure:**

```text
task state
→ scheduler
→ executor
→ capacity/concurrency
→ worker availability
→ worker logs
```

Do not immediately assume the task code is broken.

## 4. How would you diagnose scheduler slowness?

Investigate:

- DAG parsing pressure;
- metadata DB latency;
- number of DAGs/runs/tasks;
- scheduler resource usage;
- state-change volume.

## 5. How would you diagnose metadata DB overload?

Investigate:

```text
connections
CPU
memory
storage
query latency
query volume
scheduler behavior
```

Then correlate DB evidence with Airflow symptoms.

## 6. How would you scale worker capacity?

Start from workload characteristics.

Consider:

```text
CPU
memory
task concurrency
execution model
horizontal scaling
Kubernetes
worker lifecycle
```

## 7. How would you reduce DAG parsing latency?

Look for:

```text
network calls
DB calls
heavy imports
large computations
filesystem scans
complex top-level code
```

Move expensive runtime work into task execution where appropriate.

## 8. When would you choose Kubernetes-based execution?

When the workload benefits from containerized isolation, elastic execution, and integration with an existing Kubernetes platform, and the organization can support the additional operational complexity.

## 9. What architectural problems does remote logging solve?

It separates operational log retention from individual worker lifetimes, making logs easier to retrieve after worker replacement or failure.

## 10. Why should the orchestrator remain separate from heavy compute?

Because orchestration is a control-plane concern. Combining scheduling coordination with heavy data processing can create resource contention, reduce reliability, and make scaling more difficult.

---

# 79. Interview Questions — Advanced

## 1. Design Airflow for hundreds or thousands of DAGs.

A strong answer should cover:

```text
DAG source delivery
DAG Processor capacity
parse-time discipline
scheduler capacity
multiple schedulers where appropriate
metadata DB scaling
distributed workers
remote logs
API Server scaling
observability
security
```

## 2. Design a highly available scheduler architecture.

Discuss:

```text
multiple schedulers
shared metadata DB
scheduler health
resource capacity
failure detection
operational monitoring
```

Avoid inventing internal locking details unless verified for the exact Airflow release.

## 3. Design a scalable metadata database architecture.

Discuss:

```text
PostgreSQL
CPU
memory
storage
connections
indexes
query patterns
retention
monitoring
backup/recovery
```

The metadata DB remains a control-plane dependency.

## 4. Design distributed workers.

Discuss:

```text
executor
worker fleet
resource classes
CPU/memory
network
failure
scaling
remote logs
security
```

## 5. Design remote logging.

Discuss:

```text
worker
  ↓
durable object storage
  ↓
operator/UI
```

Include:

```text
authentication
authorization
networking
retention
availability
```

## 6. Design Airflow on Kubernetes.

Discuss:

```text
API Server
Scheduler
DAG Processor
Triggerer
execution environments
PostgreSQL
object storage
networking
secrets
monitoring
```

The exact deployment should follow the official Helm chart/documentation for the installed Airflow release.

## 7. Design managed Airflow architecture.

Discuss:

```text
provider-managed components
team-owned DAGs
provider integrations
security
networking
cost
vendor coupling
operational responsibilities
```

## 8. Diagnose an architecture where DAG parsing consumes excessive CPU.

Reason from:

```text
DAG count
parse frequency
heavy imports
top-level computation
external calls
DAG complexity
source delivery
```

Then measure before changing architecture.

## 9. Explain Airflow 2 → Airflow 3 architectural evolution.

Cover:

```text
DAG Processor
API Server
task SDK/API model
Assets terminology
newer orchestration boundaries
legacy webserver terminology
version-aware learning
```

## 10. Design an Airflow platform for a production Data Engineering organization.

A complete answer should include:

```text
Problem
Reasoning
Architecture
Trade-offs
Failure modes
Operational considerations
Security
Observability
Scaling
Ownership
```

---

# 80. Production Architecture Checklist

Before calling an Airflow platform production-ready, ask:

## Source

- [ ] Where does DAG source come from?
- [ ] Is source delivery reproducible?
- [ ] Is version information available?

## DAG processing

- [ ] Is DAG parsing fast?
- [ ] Are top-level network calls avoided?
- [ ] Are top-level DB calls avoided?
- [ ] Are heavy imports controlled?
- [ ] Is expensive computation excluded from parsing?

## Scheduler

- [ ] Is scheduler health monitored?
- [ ] Is scheduling latency observable?
- [ ] Is scheduler capacity sufficient?

## Executor

- [ ] Is the execution model appropriate?
- [ ] Is worker capacity aligned with workload?
- [ ] Are isolation requirements addressed?

## Workers

- [ ] Is worker failure observable?
- [ ] Is resource exhaustion monitored?
- [ ] Can execution capacity scale?

## Triggerer

- [ ] Is deferred workload capacity monitored?
- [ ] Is Triggerer health observable?

## Metadata database

- [ ] PostgreSQL or appropriate production-grade database?
- [ ] Connection capacity sized?
- [ ] CPU/memory/storage monitored?
- [ ] Backup/recovery considered?
- [ ] Metadata not used as a business-data store?

## API Server

- [ ] Authentication configured?
- [ ] Authorization configured?
- [ ] Availability monitored?
- [ ] API load considered?

## Logs

- [ ] Task logs accessible?
- [ ] Remote logs considered?
- [ ] Log retention defined?
- [ ] Sensitive information controlled?

## Security

- [ ] Least privilege?
- [ ] Secrets protected?
- [ ] Network access controlled?
- [ ] Worker isolation appropriate?
- [ ] Auditability available?

## Operations

- [ ] Failure modes documented?
- [ ] Debugging playbook available?
- [ ] Component ownership defined?
- [ ] Version compatibility tracked?

---

# 81. Architecture Decision Framework

When designing Airflow, reason in this order:

```text
1. What workflows exist?
        ↓
2. How much scheduling activity exists?
        ↓
3. How expensive is DAG parsing?
        ↓
4. What execution workloads exist?
        ↓
5. How much worker capacity is required?
        ↓
6. What execution model fits?
        ↓
7. How much metadata activity exists?
        ↓
8. How should logs be stored?
        ↓
9. What availability is required?
        ↓
10. What infrastructure does the team operate?
```

This prevents technology-first architecture.

---

# 82. Final Architecture Mental Model

```text
                  ┌──────────────────┐
                  │    DAG Source    │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  DAG Processor   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │    Scheduler     │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │     Executor     │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │     Workers      │
                  └────────┬─────────┘
                           │
                           ▼
                       Task Work


          ┌────────────────────────────────┐
          │       Metadata Database        │
          │        Operational State        │
          └────────────────────────────────┘


          ┌────────────────────────────────┐
          │           API Server           │
          │           UI + REST            │
          └────────────────────────────────┘


          ┌────────────────────────────────┐
          │           Triggerer            │
          │       Async Deferred Work      │
          └────────────────────────────────┘
```

Remember each component's job:

```text
DAG Processor
    parses workflow definitions.

Scheduler
    decides what should run.

Executor
    determines how execution is dispatched.

Worker
    performs task work.

Triggerer
    handles asynchronous waiting.

API Server
    provides supported UI/API access.

Metadata DB
    stores orchestration state.

Remote logging
    preserves operational task logs.

Providers
    connect Airflow to external systems.
```

The complete lifecycle is:

```text
DAG source
    ↓
DAG Processor
    ↓
parsed workflow definition
    ↓
Scheduler
    ↓
DAG run / task eligibility
    ↓
Executor
    ↓
Worker / execution environment
    ↓
Task execution
    ↓
Logs + task state
    ↓
Metadata Database
    ↓
Scheduler
    ↓
downstream task eligibility
```

That is the architecture you should be able to draw from memory.

---

# 83. Final Knowledge Checkpoint

You should be able to explain each item without notes.

## Architecture

- [ ] What Apache Airflow is
- [ ] Why Airflow has multiple components
- [ ] Scheduler
- [ ] DAG Processor
- [ ] API Server
- [ ] Triggerer
- [ ] Executor
- [ ] Workers
- [ ] Metadata Database
- [ ] Providers
- [ ] Logging
- [ ] Remote logging

## DAG lifecycle

- [ ] DAG discovery
- [ ] DAG parsing
- [ ] DAG processing
- [ ] Scheduling
- [ ] DAG run
- [ ] Task instance
- [ ] Dependency evaluation
- [ ] Executor dispatch
- [ ] Worker execution
- [ ] Logs
- [ ] State updates
- [ ] Downstream scheduling

## Performance

- [ ] Parse-time performance
- [ ] Top-level network calls
- [ ] Top-level database calls
- [ ] Heavy imports
- [ ] Top-level computation
- [ ] Scheduler scaling
- [ ] Metadata DB scaling
- [ ] Worker scaling
- [ ] API Server scaling
- [ ] DAG parsing scaling

## Execution

- [ ] Local execution
- [ ] Celery-style distributed execution
- [ ] Kubernetes execution
- [ ] Executor trade-offs

## Airflow 3

- [ ] API Server
- [ ] DAG Processor
- [ ] DAG bundles
- [ ] DAG versioning
- [ ] Task SDK/API architecture
- [ ] Assets terminology awareness
- [ ] Airflow 2 legacy recognition
- [ ] Scheduler-managed backfills at a conceptual level

## Deployment

- [ ] `airflow standalone`
- [ ] Docker Compose
- [ ] PostgreSQL
- [ ] MinIO
- [ ] Kubernetes
- [ ] Helm concept
- [ ] Managed Airflow

## Practical learning

- [ ] Local lab
- [ ] Minimal DAG
- [ ] Architecture tracing
- [ ] Metadata DB inspection
- [ ] Parse-time measurement
- [ ] Remote logging
- [ ] Failure injection
- [ ] Architecture diagram
- [ ] Debugging playbook

## Engineering depth

- [ ] Failure modes
- [ ] Scaling
- [ ] Security basics
- [ ] Operational concerns
- [ ] Common mistakes
- [ ] Interview questions
- [ ] Architecture questions
- [ ] Production checklist

---

# 84. Final Takeaway

The most important mental transformation is this:

```text
Beginner model:

"DAG file → Airflow runs it."


Production model:

DAG source
    ↓
DAG Processor
    ↓
Scheduler
    ↓
task eligibility
    ↓
Executor
    ↓
Worker / execution environment
    ↓
task execution
    ↓
logs + state
    ↓
Metadata Database
    ↓
Scheduler evaluates downstream work
```

Airflow is a **distributed orchestration system composed of specialized components**.

The:

```text
DAG Processor
```

understands workflow definitions.

The:

```text
Scheduler
```

decides what should happen.

The:

```text
Executor
```

coordinates task dispatch.

The:

```text
Worker
```

performs task work.

The:

```text
Triggerer
```

handles asynchronous waiting.

The:

```text
API Server
```

provides supported operational UI/API access.

The:

```text
Metadata Database
```

stores orchestration state.

The:

```text
Remote logging system
```

preserves operational evidence beyond individual worker lifetimes.

And:

```text
Providers
```

connect Airflow to external systems.

Once you understand these boundaries, Airflow stops looking like a collection of commands and starts looking like what it really is:

> **a control plane that coordinates distributed data workflows.**

---

# 85. Scope Boundaries

This file is strictly focused on:

```text
03-apache-airflow-architecture.md
```

It intentionally does **not** become the complete implementation guide for later topics.

## Topic 01 is a prerequisite

Do not reteach the complete DAG/dependency/scheduling curriculum.

Use those concepts as foundations.

## Topic 02 is a prerequisite

Do not reteach the complete cron-vs-orchestrator decision framework.

Use it only as architectural context.

## Topic 04 belongs later

Do not deeply teach:

- operators;
- TaskFlow API;
- dynamic task mapping;
- task groups;
- branching;
- trigger rules.

## Topic 05 belongs later

Do not deeply teach:

- connections;
- variables;
- hooks;
- XComs.

## Topic 06 belongs later

Do not deeply teach:

- sensors;
- deferrable operator implementation;
- Assets implementation;
- data-aware scheduling implementation.

## Topic 07 belongs later

Do not deeply teach:

- retries;
- deadlines;
- failure callbacks.

## Topic 08 belongs later

Do not deeply teach:

- catch-up;
- backfills;
- partitioned runs.

## Topics 09–10

Do not teach full Dagster or Prefect implementations.

## Topic 11

Do not teach complete DAG testing/CI methodology.

The focus here remains:

> **How Apache Airflow 3.x works internally and architecturally.**
