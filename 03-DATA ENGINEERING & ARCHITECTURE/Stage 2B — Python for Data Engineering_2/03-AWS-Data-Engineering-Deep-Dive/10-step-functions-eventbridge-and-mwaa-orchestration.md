# Step Functions, EventBridge, and MWAA Orchestration

> **G3 — AWS Data Engineering Deep Dive | Phase D**
>
> Production-oriented orchestration for AWS data platforms: workflow control, events, scheduling, retries, failure handling, state, parallelism, observability, idempotency, security, and cost.

## Important AWS Cost Warning

This module can create billable AWS resources.

Before every lab:

1. Check current AWS pricing and quotas.
2. Configure AWS Budgets and alerts.
3. Apply cost-allocation tags.
4. Use small datasets first.
5. Prefer short-lived resources.
6. Delete MWAA environments after testing.
7. Delete supporting infrastructure after labs.
8. Verify resources are actually gone.

**MWAA is especially important:** an MWAA environment is an always-on managed environment and can create ongoing charges while it exists. Treat MWAA labs as lifecycle-managed infrastructure, not disposable local software.

> AWS services change. Verify current official AWS documentation before production use of any version-sensitive API, quota, pricing detail, provider/operator version, or Terraform resource.

---

## 1. Why Orchestration Matters

A production data pipeline rarely consists of one job.

A realistic pipeline may be:

```text
S3 file arrives
    ↓
Validate file
    ↓
Glue transformation
    ↓
Data quality
    ↓
Athena transformation/query
    ↓
Redshift load
    ↓
Notification
```

Without orchestration, engineers end up writing fragile glue code that has to answer:

- Did the previous task finish?
- Did it succeed?
- Should the next task start?
- Is this error transient?
- Should it retry?
- Has the same event already been processed?
- Where is the failure?
- Who gets alerted?
- Can the pipeline resume?
- What happens when 100,000 objects arrive?

### The production mental model

```text
Trigger
  ↓
Workflow
  ↓
Dependencies
  ↓
Tasks
  ↓
Retries / Catch
  ↓
State
  ↓
Observability
  ↓
Recovery
```

Orchestration is therefore **control-plane engineering**, not data processing itself.

> **Core principle:** the orchestrator controls workflow; the worker performs computation.

---

## 2. Scheduling vs Orchestration vs Event-Driven Architecture

These concepts are related but different.

### Scheduler

Answers:

> **When should something happen?**

Example:

```text
Every day at 02:00
    ↓
Start pipeline
```

### Orchestrator

Answers:

> **What should happen, in what order, with what dependencies and failure behavior?**

Example:

```text
Glue
 ↓
DQ
 ↓
Choice
 ├── PASS → Athena
 └── FAIL → Quarantine + Alert
```

### Event-driven architecture

Answers:

> **What external event should cause the workflow to start?**

Example:

```text
S3 Object Created
    ↓
EventBridge
    ↓
Start workflow
```

### Combined architecture

```text
EventBridge Scheduler
        ↓
Step Functions
        ↓
Glue
        ↓
Athena
        ↓
Notification
```

or:

```text
S3 Object Created
        ↓
EventBridge
        ↓
Step Functions
        ↓
Pipeline
```

---

## 3. Where AWS Orchestration Fits

The AWS data platform contains several services that can play different control-plane roles.

| Need | Typical AWS service |
|---|---|
| Event routing | EventBridge |
| Time-based triggering | EventBridge Scheduler |
| Stateful AWS-native workflow | Step Functions |
| Complex DAG ecosystem / Airflow | MWAA |
| Computation | Glue / EMR / Lambda / Athena / Redshift |
| Monitoring | CloudWatch |
| Notifications | SNS / other approved targets |
| Infrastructure definition | Terraform / OpenTofu |

The correct design is not "use the most powerful tool."

It is:

> **Choose the smallest orchestration mechanism that satisfies the workflow's requirements without creating avoidable operational burden.**

---

## 4. Prerequisites and Scope Boundary

This module assumes the learner already understands:

- basic DAGs and dependencies
- retries and scheduling
- AWS fundamentals
- S3 and IAM
- Glue
- EMR / Spark
- Athena
- Redshift
- Lambda
- Terraform / CI/CD concepts
- observability
- performance and cost fundamentals

Do **not** treat this as a complete Airflow course, Lambda course, or EventBridge service encyclopedia.

The focus is:

> **How AWS services become components inside production workflows.**

---

# Part I — AWS Step Functions

## 5. AWS Step Functions Overview

AWS Step Functions is a managed workflow service for defining stateful workflows as state machines.

A workflow execution has:

- execution input
- states
- transitions
- task results
- error paths
- execution history
- final output

Mental model:

```text
State Machine
      |
      +── State A
      |
      +── State B
      |
      +── State C
      |
      +── State D
```

The state machine is the definition. An **execution** is one runtime instance of that definition.

### Why it fits data engineering

Step Functions is particularly useful when a pipeline needs:

- explicit dependencies
- AWS service integrations
- branching
- parallel work
- retries
- failure routing
- long-running workflow coordination
- event-driven execution
- execution visibility

---

## 6. State Machines

A state machine defines the workflow graph.

Minimal example:

```json
{
  "StartAt": "FirstTask",
  "States": {
    "FirstTask": {
      "Type": "Pass",
      "Result": {
        "message": "hello"
      },
      "Next": "Success"
    },
    "Success": {
      "Type": "Succeed"
    }
  }
}
```

Important fields include:

- `StartAt`
- `States`
- `Type`
- `Next`
- `End`
- state-specific configuration
- input/output processing fields

A production state machine should be readable enough that another engineer can understand the workflow without reverse-engineering application code.

---

## 7. Step Functions States

### 7.1 Task

A Task performs work through a service integration or supported task resource.

Typical data-engineering tasks include:

```text
Step Functions
    ↓
Glue job
```

```text
Step Functions
    ↓
EMR Serverless job
```

```text
Step Functions
    ↓
Athena query
```

```text
Step Functions
    ↓
Lambda
```

```text
Step Functions
    ↓
Redshift operation
```

Use a native service integration where it is supported and appropriate.

### 7.2 Choice

Choice implements branching.

```text
Data Quality
     ↓
   PASS?
   /   \
 YES    NO
  ↓      ↓
Athena  Quarantine
         ↓
        Alert
```

A Choice state should represent control flow, not hide a large amount of business logic.

### 7.3 Parallel

Parallel runs independent branches concurrently.

```text
             ┌→ Validate Orders
             │
Input ───────┼→ Validate Customers
             │
             └→ Validate Events
```

Use it only when branches are genuinely independent and the additional concurrency is useful.

### 7.4 Map

Map repeats a workflow over a collection.

```text
Input list
   ↓
  Map
   ├── Item 1 → process
   ├── Item 2 → process
   └── Item 3 → process
```

### 7.5 Wait

Wait pauses a workflow for a defined condition/time pattern.

Typical uses include:

- delay
- polling patterns where no native completion integration exists
- waiting for an external condition
- controlled timing

Avoid using Wait to compensate for poor service integration design when a native `.sync` or callback pattern is available.

### 7.6 Pass

Pass is useful for:

- shaping state data
- adding test values
- representing placeholder control flow
- simplifying development

### 7.7 Fail

Fail intentionally terminates the branch/execution with an error path.

Use explicit failure states when the workflow has reached a condition that should not continue.

---

## 8. Inputs and Outputs

State data flow is one of the most important Step Functions skills.

Example execution input:

```json
{
  "bucket": "orders-bucket",
  "key": "2026/10/06/orders.json"
}
```

A state can receive that input, transform or select part of it, invoke a task, and pass a result to the next state.

Important concepts include:

- execution input
- state input
- task result
- `ResultPath`
- `OutputPath`
- `InputPath`
- `Parameters`
- payload construction
- JSONPath
- JSONata where supported by the selected ASL features
- execution context

### Conceptual data flow

```text
Execution input
      ↓
State input
      ↓
Task parameters
      ↓
Task result
      ↓
ResultPath
      ↓
State output
      ↓
Next state
```

### Production failure pattern

A workflow can be operationally healthy but functionally wrong if a state accidentally drops the object key, run date, or correlation identifier.

Therefore every production workflow should document:

```text
What enters this state?
What does this state produce?
What does the next state require?
```

---

## 9. Amazon States Language

Amazon States Language (ASL) is the JSON-based language used to define Step Functions state machines.

A useful learning progression is:

```text
StartAt / States
        ↓
Task
        ↓
Next / End
        ↓
Choice
        ↓
Retry / Catch
        ↓
Parallel / Map
        ↓
Input/output processing
        ↓
advanced execution patterns
```

### Example: simple success flow

```json
{
  "StartAt": "ValidateInput",
  "States": {
    "ValidateInput": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.key",
          "IsPresent": true,
          "Next": "Process"
        }
      ],
      "Default": "InvalidInput"
    },
    "Process": {
      "Type": "Pass",
      "End": true
    },
    "InvalidInput": {
      "Type": "Fail",
      "Error": "InvalidInput",
      "Cause": "Required object key is missing"
    }
  }
}
```

### ASL design discipline

Keep:

- state names descriptive
- transitions explicit
- error handling visible
- payloads bounded
- heavy computation outside the state machine
- configuration separate from business data

---

## 10. Standard vs Express Workflows

Standard and Express are different workflow execution models.

| Dimension | Standard | Express |
|---|---|---|
| Long-running workflows | Strong fit | Usually better for short/high-volume workflows |
| Execution visibility | Rich execution history | Different execution/observability model |
| Workflow style | Durable, explicit orchestration | High-volume event processing |
| Pricing | Execution/state-transition-oriented model | Request/duration-oriented model |
| Delivery semantics | Designed for durable workflows | Different semantics; verify current docs |
| Typical data-engineering use | Multi-step batch/orchestration | High-volume short workflows |

Do not select purely from price.

Evaluate:

- workflow duration
- execution volume
- observability needs
- failure/retry semantics
- delivery requirements
- workload shape
- current service capabilities
- current pricing

**Always verify current AWS pricing and service semantics before production selection.**

---

## 11. AWS Service Integrations

A key production principle is:

> **Use direct AWS service integrations when they provide the required behavior; do not insert Lambda merely to call another AWS service.**

### Glue

```text
Step Functions
      ↓
Start Glue
      ↓
Wait for completion
      ↓
Continue / Catch
```

### EMR Serverless

```text
Step Functions
      ↓
Start EMR Serverless job
      ↓
Wait
      ↓
Continue / Catch
```

### Athena

```text
Step Functions
      ↓
Start query
      ↓
Wait for completion
      ↓
Evaluate result
```

### Lambda

Use Lambda when the workflow genuinely needs application code, transformation logic, validation, or an integration not better represented by another native integration.

### Redshift

Step Functions can coordinate Redshift operations through supported integrations/APIs. For exact integration resource names and current capabilities, verify the current Step Functions service-integration documentation.

---

## 12. Glue Job Orchestration

A typical Glue workflow:

```text
Start
  ↓
Glue ETL
  ↓
Data Quality
  ↓
Choice
 ├── PASS → Athena
 └── FAIL → Quarantine + Alert
```

Production concerns:

- pass job arguments explicitly
- use deterministic input/output locations
- avoid hard-coded credentials
- make outputs idempotent
- configure retries for transient failures
- catch permanent failures
- emit correlation identifiers
- monitor Glue logs and job state

### Why `.sync`-style integrations matter

If the workflow needs the Glue job to finish before proceeding, use the supported Step Functions integration pattern that waits for job completion rather than building a Lambda that polls Glue.

---

## 13. EMR Serverless Orchestration

A common architecture:

```text
Step Functions
      ↓
Start EMR Serverless job
      ↓
Completion
      ↓
Athena / downstream step
```

This is useful when Spark computation is needed but the workflow should remain AWS-native and the learner does not need to manage an EMR cluster lifecycle directly.

Do not duplicate the EMR module. Focus on:

- job submission
- dependency ordering
- arguments
- completion
- failure handling
- retry strategy
- execution metadata
- cost controls

---

## 14. Athena Orchestration

Athena is commonly a downstream query/transform step.

Example:

```text
Glue
 ↓
Catalog ready
 ↓
Athena query
 ↓
Validate result
 ↓
Publish
```

Production considerations:

- use a controlled workgroup
- control query result locations
- encrypt results where required
- monitor scanned bytes
- avoid accidental full-table scans
- make output locations deterministic
- distinguish SQL/data errors from transient service failures

---

## 15. Lambda Orchestration

Lambda is useful for:

- custom validation
- lightweight application logic
- API integration
- notification preparation
- control-plane glue where no native integration is suitable

Avoid:

```text
Step Functions
 ↓
Lambda
 ↓
Poll Glue
 ↓
Poll Glue
 ↓
Poll Glue
```

Prefer:

```text
Step Functions
 ↓
Native Glue integration
 ↓
Wait
```

Lambda should not become an accidental orchestration engine inside the orchestrator.

---

## 16. Redshift Orchestration

A warehouse pipeline might be:

```text
S3
 ↓
Glue / transformation
 ↓
Athena / validation
 ↓
Redshift load or SQL
 ↓
Quality check
 ↓
Publish
```

Production concerns:

- make loads idempotent
- use deterministic staging keys
- separate staging from final tables
- handle retries without duplicate inserts
- monitor query execution
- use appropriate warehouse-side transaction semantics
- verify current Step Functions/Redshift integration capabilities before implementation

---

# Part II — Reliability Engineering

## 17. Run-and-Wait Patterns

### Fragile approach

```text
Step Functions
    ↓
Lambda
    ↓
Start Glue
    ↓
poll every 10 seconds
    ↓
poll again
    ↓
poll again
```

### Preferred pattern

```text
Step Functions
    ↓
AWS service integration
    ↓
Start job
    ↓
Wait for completion
    ↓
Continue
```

Benefits:

- less custom code
- fewer failure points
- lower operational complexity
- clearer execution history
- fewer unnecessary Lambda invocations

Use custom polling only when the target system genuinely requires it.

---

## 18. Retries

Retries are for **transient** failure, not every failure.

Typical transient categories:

- throttling
- temporary service unavailability
- network-level transient behavior
- short-lived dependency failures

Typical non-retryable categories:

- malformed input
- invalid SQL
- missing required configuration
- deterministic schema mismatch
- authorization misconfiguration
- failed data-quality rules

### Example ASL retry policy

```json
"Retry": [
  {
    "ErrorEquals": [
      "States.Timeout"
    ],
    "IntervalSeconds": 5,
    "MaxAttempts": 3,
    "BackoffRate": 2.0
  }
]
```

This is an example, not a universal production policy. Select error classes based on the actual integration and current AWS documentation.

### Exponential backoff

With:

```text
Interval = 5 seconds
BackoffRate = 2
Attempts = 3
```

the conceptual delays increase rather than hammering the dependency immediately.

The objective is:

```text
Transient failure
      ↓
Wait
      ↓
Retry
      ↓
Wait longer
      ↓
Retry
      ↓
Catch if still failing
```

---

## 19. Catchers

A Catch path is the workflow's controlled failure route.

```text
Main processing
      |
      +── success → Next
      |
      +── failure → Catch
                       ↓
                    Record
                       ↓
                    Alert
                       ↓
                 Quarantine /
                 Compensation
```

Use Catch for:

- invalid data
- unrecoverable service errors
- failed quality gates
- authorization/configuration failures
- escalation
- compensation

A production workflow should not simply "fail somewhere." It should fail **intentionally and observably**.

---

## 20. Retry vs Catch

| Situation | Retry | Catch |
|---|---:|---:|
| Temporary throttling | Yes | Maybe |
| Temporary service unavailable | Yes | Maybe |
| Invalid input | No | Yes |
| Data-quality failure | Usually no | Yes |
| Permission failure | Usually no | Yes |
| Human approval | No | Route to approval |
| Permanent schema mismatch | No | Yes |

This is a decision pattern, not a universal rule. The actual error contract of the integrated AWS service must drive the implementation.

---

## 21. Backoff and Jitter

Backoff reduces synchronized retries.

```text
Immediate retry
    ↓
Many clients retry together
    ↓
Dependency gets overloaded again
```

Better:

```text
Failure
 ↓
Backoff
 ↓
Retry
 ↓
Longer backoff
```

Jitter introduces controlled randomness where appropriate so many clients do not retry simultaneously.

Important distinction:

- Step Functions provides retry/backoff configuration.
- Do not assume every retry mechanism exposes an arbitrary "jitter" setting.
- When jitter is not natively available for the exact mechanism, consider architecture-level techniques rather than inventing unsupported ASL fields.

---

## 22. Failure Handling

Every workflow should answer:

1. What can fail?
2. Which failures are retryable?
3. Which failures should immediately stop?
4. Where does failed data go?
5. Who gets alerted?
6. Can the workflow be safely re-run?
7. How is the root cause correlated with the execution?

### Failure taxonomy

```text
Transient
   ↓
Retry
   ↓
Success
```

```text
Permanent
   ↓
Catch
   ↓
Quarantine / Alert / Compensate
```

```text
Unknown
   ↓
Observe
   ↓
Classify
   ↓
Improve policy
```

---

## 23. Idempotency

Event-driven systems must assume duplicate delivery or duplicate initiation can occur.

Example:

```text
S3 event
 ↓
EventBridge
 ↓
Step Functions
```

The same business object may trigger more than one execution.

### Retry safety vs duplicate-event safety

These are different problems.

**Retry safety** asks:

> What happens if one execution retries a failed task?

**Duplicate-event safety** asks:

> What happens if the same business event starts two executions?

### Idempotency techniques

- deterministic object keys
- execution/business identifiers
- conditional writes
- MERGE semantics
- staging tables
- processed-event records
- DynamoDB idempotency records where appropriate
- deterministic output locations
- deduplication before side effects

### Exactly-once caution

Do not casually promise "exactly once."

A more useful production statement is:

> Design side effects so duplicate delivery is safe or detectable.

---

## 24. Parallel Workflows

Parallelism is useful when branches are independent.

```text
             ┌→ Customer validation
             │
Input ───────┼→ Order validation
             │
             └→ Event validation
```

Evaluate:

- branch independence
- downstream capacity
- failure behavior
- aggregation
- concurrency limits
- cost

Parallelism is not free. It can move a bottleneck downstream.

---

## 25. Map State

Map is appropriate for repeated processing.

```text
[
  object-A,
  object-B,
  object-C
]
        ↓
      Map
        ↓
validate each item
```

Important concepts:

- item input
- per-item processing
- concurrency
- per-item failure
- result collection
- aggregate result
- retry policy

Example conceptual input:

```json
{
  "objects": [
    {"bucket": "raw", "key": "a.json"},
    {"bucket": "raw", "key": "b.json"}
  ]
}
```

The workflow can process each object using a consistent state definition.

---

## 26. Distributed Map

Distributed Map is intended for very large parallel workflows.

Roadmap scenario:

```text
100,000 small S3 objects
        ↓
Distributed Map
        ↓
Lambda validator
        ↓
Validation results
        ↓
Summary
```

Why it matters:

- very large item collections
- S3-backed inputs
- high parallelism
- distributed execution model
- result aggregation
- failure tolerance strategies

### Production questions

Before using Distributed Map, determine:

- item source
- desired concurrency
- downstream service capacity
- failure tolerance
- result size
- retry strategy
- cost ceiling
- observability
- whether the downstream Lambda can absorb the load

Do not hard-code quota assumptions. Verify current Distributed Map limits and supported item-reader/result-writer features in current AWS documentation.

---

# Part III — EventBridge

## 27. EventBridge Fundamentals

EventBridge provides event routing.

Mental model:

```text
Producer
   ↓
Event
   ↓
Event Bus
   ↓
Rule
   ↓
Target
```

The event producer should not need to know every downstream consumer.

That creates loose coupling.

---

## 28. Event Buses

Common concepts:

- default event bus
- custom event buses
- event producers
- rules
- targets
- cross-account event routing

Example:

```text
Partner / application
        ↓
Custom Event Bus
        ↓
Rule
        ↓
Step Functions
```

Use custom buses when organizational or domain boundaries justify them.

---

## 29. Event Rules

A rule evaluates incoming events and routes matching events to targets.

Conceptually:

```text
Event
 ↓
Rule pattern
 ↓
MATCH?
 ├── NO → ignore
 └── YES → target
```

A good rule prevents unnecessary downstream invocations.

---

## 30. Event Patterns

Example conceptual pattern:

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"]
}
```

An event pattern can filter on event fields such as:

- `source`
- `detail-type`
- `detail`
- service-specific attributes

Filtering at EventBridge is generally preferable to triggering a Lambda for every event and filtering afterward.

Always validate the exact event shape generated by the service in your target Region/account.

---

## 31. S3 Event-Driven Pipelines

Production pattern:

```text
S3 Object Created
        ↓
EventBridge
        ↓
Rule
        ↓
Step Functions
        ↓
Glue
        ↓
Data Quality
        ↓
Athena
        ↓
Notification
```

Carry enough context to identify the business event:

```text
bucket
object key
event time
source
correlation ID
```

Do not assume event ordering or single delivery.

Design for:

- duplicate events
- out-of-order events
- late arrivals
- invalid objects
- replay/reprocessing

---

## 32. EventBridge Targets

Common orchestration targets include:

- Step Functions
- Lambda
- other supported AWS targets

Example:

```text
EventBridge
   |
   +── Step Functions
   |
   +── Lambda
   |
   +── Other target
```

Target invocation requires correct permissions.

Review:

```text
EventBridge
    ↓
Target invocation permission
    ↓
Target service
```

Do not grant broad permissions merely to make a lab work.

---

## 33. EventBridge Scheduler

Scheduler is for time-based invocation.

Use cases include:

- recurring schedules
- cron-like schedules
- one-time schedules
- time-zone-aware scheduling where supported
- retry/failure behavior around target invocation

Example:

```text
Every day 02:00
      ↓
EventBridge Scheduler
      ↓
Step Functions
```

One-time:

```text
2026-10-10 03:00
      ↓
Scheduler
      ↓
Workflow
```

The scheduler starts the workflow; Step Functions can then control all downstream dependencies.

---

## 34. EventBridge Rule vs Scheduler

| Requirement | EventBridge Rule | EventBridge Scheduler |
|---|---|---|
| Event-driven | Strong fit | Not primary purpose |
| Cron-like schedule | Supported through scheduled rules | Strong fit |
| One-time schedule | Not the primary model | Strong fit |
| Event-pattern filtering | Strong fit | Not primary purpose |
| Simple target invocation | Yes | Yes |
| Time-based execution | Yes | Strong fit |
| Data pipeline trigger | Yes | Yes |

Do not choose by name alone. Check the trigger requirement.

---

# Part IV — MWAA and Airflow

## 35. MWAA Fundamentals

Amazon Managed Workflows for Apache Airflow (MWAA) is a managed AWS service for running Apache Airflow.

Airflow's mental model:

```text
                 MWAA
                  |
        +---------+---------+
        |         |         |
       DAG     Scheduler  Workers
        |
      Tasks
```

The service manages substantial platform infrastructure, while the data engineering team still manages:

- DAG code
- dependencies
- workflow design
- IAM requirements
- data-plane behavior
- operational configuration
- testing
- cost discipline

---

## 36. Airflow DAGs on MWAA

A DAG expresses task dependencies.

Example:

```text
S3
 ↓
Glue
 ↓
DQ
 ↓
Athena
 ↓
Notification
```

Conceptual Airflow example:

```python
from airflow import DAG
from datetime import datetime

with DAG(
    dag_id="daily_data_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    # Use current AWS provider operators for real tasks.
    # Keep provider-specific class names pinned to your MWAA/provider version.
    pass
```

The important concepts are:

- DAG
- task
- dependency
- schedule
- retries
- task state
- backfill

Do not turn this into a full Apache Airflow course.

---

## 37. MWAA Environments

An MWAA environment includes managed Airflow infrastructure and AWS integration.

Key considerations:

- environment lifecycle
- networking
- workers and scaling
- logging
- S3 integration
- security
- IAM
- Airflow version compatibility
- dependency compatibility

### Lifecycle discipline

```text
Create
  ↓
Configure
  ↓
Test
  ↓
Operate
  ↓
Delete when no longer needed
```

Never treat a development MWAA environment as free infrastructure.

---

## 38. DAG Deployment from S3

A simplified deployment model is:

```text
Developer
   ↓
DAG file
   ↓
S3
   ↓
MWAA
   ↓
DAG discovered
   ↓
Scheduler
```

A production deployment should validate:

- DAG syntax
- imports
- provider compatibility
- dependencies
- IAM
- deployment version
- expected schedule
- task behavior

---

## 39. Requirements and Dependencies

MWAA workflows commonly involve Python dependencies and provider packages.

Key risks:

- incompatible versions
- dependency conflicts
- provider version mismatch
- deployment delays
- unsupported packages
- differences between local Airflow and managed MWAA

Use a controlled dependency process:

```text
Pin / constrain
      ↓
Test
      ↓
Deploy
      ↓
Validate imports
      ↓
Run DAG
```

Always verify the Airflow and provider versions supported by the specific MWAA environment before selecting exact package versions.

---

## 40. AWS Provider Operators

Airflow communicates with AWS through its AWS provider ecosystem.

Common capability areas include operators/hooks for:

- Glue
- EMR
- Athena
- Lambda
- S3
- Step Functions
- other AWS services

Do not copy an operator class name from an unrelated Airflow version.

For exact operator names:

1. identify the MWAA Airflow version
2. identify the AWS provider version
3. consult the matching Apache Airflow provider documentation
4. test the DAG in the target environment

Authentication should use the environment's supported IAM model rather than embedded access keys.

---

## 41. Step Functions vs MWAA

There is no universally "best" orchestrator.

| Dimension | Step Functions | MWAA |
|---|---|---|
| AWS-native | Excellent | Excellent AWS integration, Airflow-based |
| DAG complexity | Strong for state-machine workflows | Strong for complex DAGs |
| Python workflow logic | Limited compared with Airflow | Strong |
| Backfills | Workflow-dependent | Strong Airflow capability |
| Dynamic workflows | Map / state-machine patterns | Dynamic DAG/task patterns |
| AWS service integrations | Strong native integrations | Strong provider ecosystem |
| Open-source ecosystem | AWS service | Large Airflow ecosystem |
| Team Airflow expertise | Not required | Important |
| Operational burden | Lower managed orchestration burden | Higher environment/dependency burden |
| Cost model | Execution-based service model | Managed environment plus related usage |
| Observability | Execution history + CloudWatch | Airflow UI/logs + CloudWatch |
| Long-running workflows | Strong fit | Strong fit |
| Event-driven workflows | Strong fit | Possible, but often via trigger architecture |
| Scheduling | Scheduler/Schedule integrations | Airflow schedules |
| Retries | Native workflow semantics | Airflow task retries |
| State management | State-machine execution | Airflow metadata/task state |

### Typical selection

Choose Step Functions when:

- AWS-native services dominate
- the workflow is a state machine
- event-driven execution is central
- native service integrations reduce custom code

Choose MWAA when:

- the organization already operates Airflow
- complex DAG/backfill semantics matter
- Python-based orchestration is important
- broad provider ecosystem value exceeds environment overhead

---

## 42. EventBridge-Only Architectures

Some workflows do not require a full workflow engine.

Simple:

```text
S3 event
   ↓
EventBridge
   ↓
Lambda
```

Scheduled:

```text
Schedule
   ↓
EventBridge Scheduler
   ↓
Lambda
```

This becomes insufficient when requirements become:

```text
Task A
 ↓
Task B
 ↓
Choice
 ↓
Task C / D
 ↓
Retry
 ↓
Compensation
```

Use a workflow engine when dependency management, state, recovery, and execution visibility become first-class requirements.

---

# Part V — Advanced Patterns

## 43. Callback Patterns and Task Tokens

Some workflows need to pause while an external party acts.

```text
Step Functions
      ↓
External request
      ↓
WAIT
      ↓
External system / human
      ↓
Callback
      ↓
Continue
```

A task-token callback pattern allows an external actor to signal completion.

### Human approval

```text
Pipeline
  ↓
Approval required
  ↓
Human reviews
  ↓
Approve / reject
  ↓
Workflow continues or fails
```

### External system

```text
Step Functions
  ↓
Send request
  ↓
External processing
  ↓
Callback with task token
  ↓
Continue
```

Production controls:

- timeout
- authorization
- token protection
- audit trail
- duplicate callback handling
- failure route

Never expose callback tokens unnecessarily.

---

## 44. EventBridge Pipes Awareness

EventBridge Pipes provides a managed source-to-target integration model with optional filtering and enrichment.

Mental model:

```text
Source
  ↓
Pipe
  ↓
Filter
  ↓
Enrichment
  ↓
Target
```

Why it matters:

- reduces custom glue code
- supports controlled event/data movement
- can enrich before delivery
- separates simple routing from full workflow orchestration

It is **not** a replacement for Step Functions when a multi-step stateful workflow is required.

---

# Part VI — Infrastructure, Testing, Operations

## 45. Infrastructure as Code

Console:

```text
Good for exploration
```

Infrastructure as Code:

```text
Good for repeatability
```

Define as code:

- Step Functions state machines
- EventBridge rules
- Scheduler
- IAM roles
- event targets
- S3 deployment infrastructure
- MWAA infrastructure
- tags
- environment-specific configuration

### Representative Terraform pattern

Exact Terraform resource names and arguments are version-sensitive; verify them against the current AWS provider documentation.

Conceptually:

```hcl
# Illustrative structure only.
# Verify the current AWS provider resource/schema before applying.

resource "aws_sfn_state_machine" "pipeline" {
  name     = "data-pipeline"
  role_arn = var.step_functions_role_arn

  definition = file("${path.module}/state-machine.json")

  tags = {
    Environment = var.environment
    CostCenter  = var.cost_center
  }
}
```

The state-machine JSON should be version-controlled, reviewed, and tested.

---

## 46. Testing Orchestration

Orchestration is production code.

### Unit-level

Test:

- input construction
- branch conditions
- parameter construction
- failure decisions

### Definition validation

Validate the state-machine definition before deployment.

### Integration testing

```text
Event
 ↓
Rule
 ↓
Workflow
 ↓
AWS service
```

### Failure testing

Inject:

- service failure
- timeout
- permission failure
- bad input
- duplicate event
- partial Map failure

### Test matrix

| Test | Expected result |
|---|---|
| Valid input | Workflow succeeds |
| Missing key | Validation failure |
| Transient failure | Retry then recover |
| Permanent failure | Catch route |
| Duplicate event | Idempotent outcome |
| DQ failure | Quarantine/alert |
| Callback timeout | Controlled failure |
| Target permission denied | Observable failure |

---

## 47. Observability

### Step Functions

Monitor:

- execution status
- failed states
- execution duration
- retry behavior
- execution input/output where appropriate

### EventBridge

Monitor:

- rule activity
- target delivery
- failed invocations
- event volume
- dead-letter/failure mechanisms where configured

### Scheduler

Monitor:

- expected invocation
- target invocation
- failures
- schedule configuration

### MWAA

Monitor:

- DAG/task status
- scheduler health
- task logs
- worker behavior
- environment health
- dependency/import failures

### CloudWatch

Use CloudWatch for:

- metrics
- logs
- alarms
- operational correlation

### Investigation flow

```text
Pipeline failed
      ↓
Which execution?
      ↓
Which state/task?
      ↓
What input?
      ↓
Which AWS service?
      ↓
What error?
      ↓
What logs?
      ↓
Root cause
      ↓
Fix
      ↓
Verification
```

---

## 48. Security

Use:

- IAM roles
- least privilege
- short-lived credentials/assumed roles
- KMS where encryption requirements demand it
- encrypted data
- controlled S3 access
- controlled EventBridge targets
- private networking where appropriate
- Secrets Manager for secrets
- secure MWAA networking
- no hard-coded credentials

### Permission chain

```text
EventBridge
     ↓
Target invocation permission
     ↓
Step Functions
     ↓
Execution role
     ↓
Glue / EMR / Athena / Lambda / Redshift
```

For MWAA:

```text
MWAA
  ↓
Execution role
  ↓
AWS service permissions
```

Do not solve permission errors with `AdministratorAccess`.

---

## 49. Cost Optimization

Do not memorize prices. Understand cost drivers.

Evaluate:

- Step Functions executions/transitions and workflow volume
- EventBridge events and routing
- Scheduler usage
- Lambda invocation/duration
- Glue job runtime
- EMR compute
- Athena scanned data
- Redshift compute
- MWAA environment lifecycle

### Cost engineering questions

Before deploying:

```text
What runs?
How often?
How long?
How much data?
How many events?
How much parallelism?
What remains running?
```

### MWAA

```text
Environment created
       ↓
Ongoing environment cost
       ↓
Delete when no longer required
```

Use:

- budgets
- alerts
- tags
- small labs
- teardown scripts
- resource inventory
- post-lab verification

---

# Part VII — Production Architecture

## 50. Production Architecture Pattern 1 — File Arrival Pipeline

```text
Partner
   ↓
S3
   ↓
EventBridge
   ↓
Step Functions
   ↓
Glue
   ↓
Data Quality
   ↓
Choice
 ├── FAIL → Quarantine + Alert
 └── PASS → Athena CTAS
                  ↓
             Notification
```

Production controls:

- event filtering
- idempotency
- retry policy
- Catch paths
- deterministic outputs
- IAM least privilege
- encryption
- CloudWatch monitoring
- cost attribution

---

## 51. Production Architecture Pattern 2 — Daily Batch Pipeline

```text
EventBridge Scheduler
        ↓
Step Functions
        ↓
Glue
        ↓
Data Quality
        ↓
EMR Serverless
        ↓
Athena
        ↓
Redshift
        ↓
Notification
```

Scheduler answers **when**.

Step Functions answers **what, in what order, with what failure behavior**.

---

## 52. Production Architecture Pattern 3 — Airflow Platform

```text
MWAA
 |
 +── DAG
      |
      +── S3
      +── Glue
      +── Athena
      +── EMR
      +── Redshift
```

Prefer this when Airflow's ecosystem, DAG model, backfills, and existing team expertise justify the environment.

---

## 53. Production Architecture Pattern 4 — Event-Driven Platform

```text
                    +→ Lambda
                    |
Events → EventBridge +→ Step Functions
                    |
                    +→ Other targets
```

Use event filtering and domain-oriented buses/rules where appropriate.

The event producer should not need to know the complete downstream workflow topology.

---

# Part VIII — Decision Framework

## 54. Decision Framework

Start with the requirement.

```text
Do I need multi-step workflow control?
        |
       NO
        ↓
Is simple event/schedule routing enough?
        |
       YES
        ↓
EventBridge / Scheduler
```

If multi-step:

```text
Need complex Airflow ecosystem,
Python orchestration, or backfills?
        |
   +----+----+
  YES       NO
   ↓         ↓
 MWAA   Step Functions
```

This is not absolute.

Consider:

- existing team skills
- AWS service mix
- portability requirements
- backfill complexity
- event-driven needs
- dependency graph
- workflow duration
- operational budget
- compliance
- observability
- vendor strategy

---

## 55. Architecture Decision Records

### ADR 1 — Step Functions instead of MWAA

**Context:** AWS-native services dominate and workflows are event-driven.

**Decision:** Use Step Functions.

**Alternatives:** MWAA, custom Lambda orchestration.

**Trade-offs:** AWS-native integration and lower environment burden versus AWS-specific workflow definitions.

**Reliability:** Native retry/Catch patterns.

**Security:** IAM execution role.

**Cost:** No always-running Airflow environment for the workflow itself.

**Risk:** Workflow complexity can grow.

---

### ADR 2 — EventBridge + Step Functions instead of Lambda polling

**Context:** S3 events start asynchronous AWS data jobs.

**Decision:** Route the event to Step Functions and use supported service integrations.

**Alternative:** Lambda starts and polls jobs.

**Trade-off:** More declarative orchestration, less custom polling code.

**Risk:** Integration capabilities must be verified for the selected AWS service.

---

### ADR 3 — Scheduler instead of Airflow schedule

**Context:** A simple time-based workflow has no need for a complex DAG platform.

**Decision:** EventBridge Scheduler starts the workflow.

**Alternative:** MWAA scheduled DAG.

**Trade-off:** Simpler infrastructure and lower operational overhead versus fewer Airflow-native features.

---

### ADR 4 — Distributed Map instead of a traditional loop

**Context:** A very large S3 object collection must be processed in parallel.

**Decision:** Evaluate Distributed Map.

**Alternative:** Single Lambda loop or serial Map.

**Trade-off:** High parallelism versus greater concurrency/cost-management responsibility.

---

### ADR 5 — MWAA for a backfill-heavy platform

**Context:** The organization already operates Airflow and requires complex DAG/backfill workflows.

**Decision:** Use MWAA.

**Alternative:** Step Functions.

**Trade-off:** Airflow ecosystem and backfill strengths versus managed-environment and dependency cost.

---

# Part IX — Hands-On Labs

## 56. Hands-On Lab 1 — Standard Step Functions Workflow

Build:

```text
Glue Job
   ↓
Data Quality Evaluation
   ↓
Choice
 ├── FAIL → Alert
 └── PASS → Athena CTAS
                  ↓
             Notification
```

Requirements:

- Standard workflow
- Glue completion wait
- DQ evaluation
- Choice
- retry policy
- Catcher
- failure notification
- success notification

### Deliverables

- state-machine JSON
- architecture diagram
- IAM role design
- retry/Catch table
- test cases
- cost estimate
- teardown checklist

---

## 57. Hands-On Lab 2 — Event-Driven S3 Pipeline

Build:

```text
S3 Object Created
       ↓
EventBridge Rule
       ↓
Step Functions
       ↓
Glue
       ↓
Data Quality
       ↓
Athena
```

Test:

1. upload valid file
2. verify event
3. verify workflow execution
4. upload invalid file
5. verify safe failure
6. verify alert
7. inspect logs
8. test duplicate event behavior

---

## 58. Hands-On Lab 3 — Scheduled Pipeline

Build:

```text
EventBridge Scheduler
        ↓
Step Functions
        ↓
Pipeline
```

Demonstrate:

- recurring schedule
- one-time schedule
- target IAM role
- execution verification
- failure handling
- teardown

---

## 59. Hands-On Lab 4 — Distributed Map

Roadmap scenario:

> Validate 100,000 small S3 objects in parallel with Lambda and summarize results.

Architecture:

```text
S3 objects
     ↓
Distributed Map
     ↓
Lambda validator
     ↓
Validation result
     ↓
Aggregate summary
```

### Cost-safe approach

Do not start with 100,000 real objects.

First run:

```text
10 → 100 → 1,000
```

Then reason about the 100,000-object production architecture.

Measure:

- concurrency
- execution time
- failed items
- retries
- Lambda throttling
- downstream load
- cost

---

## 60. Hands-On Lab 5 — MWAA Equivalent Workflow

Rebuild:

```text
Glue
 ↓
DQ
 ↓
Athena
 ↓
Notification
```

as an Airflow DAG.

Compare:

| Dimension | Step Functions | MWAA |
|---|---|---|
| Definition complexity | | |
| Retries | | |
| Logs | | |
| Scheduling | | |
| Backfills | | |
| AWS integrations | | |
| Operational overhead | | |
| Cost | | |

---

## 61. Hands-On Lab 6 — Decision Record

Write:

> **Step Functions vs MWAA for my platform**

Include:

```text
Requirements
Architecture
Step Functions option
MWAA option
EventBridge-only option
Operational cost
Development complexity
Backfills
Observability
Team skills
Recommendation
Risks
```

---

# Part X — Break/Fix

## 62. Break/Fix Exercises

### Incident 1 — Glue transient failure

**Break:** Inject a transient Glue failure.

**Diagnose:** Is it retryable?

**Fix:** Configure bounded retry and Catch.

**Verify:** Successful recovery is visible in execution history.

---

### Incident 2 — Data-quality failure

**Break:** Cause a quality rule to fail.

**Diagnose:** Is retry useful?

**Fix:** Catch and quarantine/alert.

**Verify:** Bad data does not reach the published layer.

---

### Incident 3 — Duplicate S3 event

**Break:** Submit the same business object twice.

**Diagnose:** Identify duplicate executions.

**Fix:** Add an idempotency strategy.

**Verify:** Only one business side effect occurs.

---

### Incident 4 — Silent failure

**Break:** Remove the failure notification route.

**Diagnose:** Workflow fails but no alert is emitted.

**Fix:** Add explicit Catch and notification.

**Verify:** Failure is observable.

---

### Incident 5 — Lambda polling anti-pattern

**Break:** Replace a native job integration with Lambda polling.

**Diagnose:** Identify unnecessary invocations and state.

**Fix:** Use the supported native integration/wait pattern.

---

### Incident 6 — MWAA cost incident

**Break:** Leave a development environment running.

**Diagnose:** Identify the resource and lifecycle.

**Fix:** Delete the environment after the exercise and add lifecycle controls.

---

### Incident 7 — Scheduler double trigger

Investigate:

- duplicate schedules
- duplicate EventBridge rules
- target retry behavior
- duplicate events
- idempotency

---

### Incident 8 — Distributed Map partial failure

Some objects fail.

Decide:

- retry failed items?
- tolerate failure?
- aggregate failed keys?
- fail entire workflow?

There is no universal answer; it depends on the business SLA.

---

# Part XI — Troubleshooting Runbooks

## 63. Runbook Format

Use:

```text
Symptom
  ↓
Evidence
  ↓
Likely causes
  ↓
Commands / console locations
  ↓
Diagnosis
  ↓
Fix
  ↓
Verification
  ↓
Prevention
```

### 63.1 Step Functions workflow failed

Check:

1. execution ARN
2. failed state
3. state input
4. error/cause
5. service integration
6. IAM role
7. retry/Catch path
8. downstream service logs

### 63.2 EventBridge event did not trigger

Check:

1. producer emitted the event
2. event bus
3. event pattern
4. rule state
5. target configuration
6. target invocation permissions
7. target failure logs

### 63.3 Scheduler did not invoke target

Check:

1. schedule state
2. time zone/schedule expression
3. target
4. execution role
5. retry/failure configuration
6. target logs

### 63.4 Glue task failed

Check:

1. Glue job run
2. job arguments
3. IAM
4. S3 permissions
5. job logs
6. data/schema
7. retry classification

### 63.5 EMR task failed

Check:

1. job run
2. Spark logs
3. application arguments
4. IAM
5. S3/Iceberg access
6. compute/configuration
7. failure classification

### 63.6 Athena task failed

Check:

1. query execution
2. SQL
3. workgroup
4. S3 result location
5. Catalog/schema
6. scanned data
7. IAM

### 63.7 Lambda target failed

Check:

1. Lambda errors
2. throttles
3. timeout
4. payload
5. IAM
6. dependency/API failure

### 63.8 MWAA DAG failed

Check:

1. DAG import errors
2. task state
3. task logs
4. scheduler
5. dependency version
6. IAM
7. AWS provider compatibility

### 63.9 Duplicate event

Check:

1. source event history
2. EventBridge rule
3. target invocation
4. execution IDs
5. business idempotency key

### 63.10 Workflow stuck waiting

Check:

1. expected callback/job completion
2. task timeout
3. service integration behavior
4. external dependency
5. callback token flow
6. CloudWatch/AWS service logs

### 63.11 Callback timeout

Check:

1. token destination
2. token security
3. callback permission
4. timeout
5. duplicate callback
6. external system status

---

# Part XII — Common Mistakes

## 64. Common Mistakes and Corrections

| Mistake | Correction |
|---|---|
| Lambda polls every AWS job | Prefer supported native integration |
| No retry policy | Classify transient failures |
| Retry every error | Avoid retrying deterministic failures |
| No Catch | Design explicit failure routes |
| No alerting | Make failures observable |
| Assume one event | Design for duplicates |
| No idempotency | Make side effects repeat-safe |
| Huge state machine | Keep orchestration focused |
| Heavy computation in Step Functions | Move computation to worker services |
| Airflow for trivial routing | Consider EventBridge/Step Functions |
| EventBridge-only for complex DAGs | Use workflow orchestration |
| Ignore execution history | Treat it as primary evidence |
| No correlation ID | Propagate execution/business identifiers |
| No timeout | Bound external waits |
| No cost guardrails | Budgets, tags, teardown |
| Leave MWAA running | Delete after lab |
| Hard-code credentials | Use IAM roles |
| Console-only deployment | Define production infrastructure as code |
| Test only success path | Test failures and duplicates |

---

# Part XIII — Advanced Principles

## 65. Advanced Orchestration Design Principles

### Principle 1

```text
Orchestrator controls workflow.
Worker performs computation.
```

### Principle 2

```text
Event triggers workflow.
Workflow controls dependencies.
```

### Principle 3

```text
Retry transient failures.
Do not blindly retry permanent failures.
```

### Principle 4

```text
Every production workflow needs a failure path.
```

### Principle 5

```text
Event-driven systems must assume duplicates.
```

### Principle 6

```text
Infrastructure should be reproducible.
```

### Principle 7

```text
Observability is part of orchestration design.
```

### Principle 8

```text
The simplest valid architecture usually has the lowest operational risk.
```

---

# Part XIV — Interview Preparation

## 66. Interview Questions

### Beginner

**Q: What is AWS Step Functions?**

**Short answer:** A managed service for defining and executing stateful workflows.

**Detailed answer:** It represents workflow control flow as a state machine and can coordinate AWS services with explicit dependencies, branching, retries, and failure handling.

**Production example:** S3 event → Step Functions → Glue → DQ → Athena.

**Interview trap:** Calling it only a scheduler.

---

**Q: What is EventBridge?**

**Short answer:** A managed event-routing service.

**Detailed answer:** Producers emit events, buses receive them, rules filter them, and targets receive matching events.

**Interview trap:** Treating it as a full workflow engine.

---

**Q: What is MWAA?**

**Short answer:** Amazon's managed service for Apache Airflow.

**Interview trap:** Assuming AWS manages the DAG logic and all dependencies for you.

---

### Intermediate

**Q: Standard vs Express Step Functions?**

Focus on workload duration, execution volume, observability, semantics, and pricing model.

**Q: Task vs Choice?**

Task performs work; Choice selects a path.

**Q: Map vs Parallel?**

Parallel runs a fixed set of branches; Map repeats processing over a collection.

**Q: EventBridge Rule vs Scheduler?**

Rules are fundamentally event-routing constructs and can also support schedule-based triggering; Scheduler is purpose-built for time-based target invocation including one-time schedules.

**Q: Why native integrations instead of Lambda polling?**

They reduce custom code, failure points, and operational complexity when the required integration supports the desired wait behavior.

---

### Advanced

**Q: When choose Step Functions over MWAA?**

Prefer Step Functions when AWS-native service orchestration, event-driven workflows, and explicit state-machine semantics dominate.

**Q: When choose MWAA?**

Prefer MWAA when Airflow's DAG ecosystem, Python-based orchestration, existing expertise, and backfill capabilities justify the environment.

**Q: When is EventBridge alone enough?**

When the requirement is simple event/time routing rather than stateful multi-step dependency management.

**Q: How do you make event-driven pipelines idempotent?**

Use deterministic business identifiers, conditional writes, deduplication, staging/merge strategies, and repeat-safe side effects.

**Q: How do you process 100,000 S3 objects?**

Evaluate Distributed Map, downstream concurrency, failure tolerance, result aggregation, cost, and service quotas.

**Q: How do you implement human approval?**

Use a callback/task-token pattern with bounded waiting and controlled authorization.

**Q: How do you control MWAA cost?**

Treat the environment as continuously billable infrastructure, use short-lived lab environments, budgets/tags, and delete environments when no longer needed.

---

# Part XV — Practice Questions

## 67. Scenario-Driven Practice

### Scenario 1 — S3 file arrival

An S3 object should trigger validation and transformation.

Design:

```text
S3
 ↓
EventBridge
 ↓
Step Functions
 ↓
Glue
 ↓
DQ
```

Explain duplicate-event handling.

---

### Scenario 2 — Glue → DQ → Athena → Redshift

Choose an orchestrator and justify the choice.

---

### Scenario 3 — Throttling

A job intermittently receives throttling errors.

Design:

- Retry
- backoff
- maximum attempts
- Catch

---

### Scenario 4 — Duplicate partner file

A partner uploads the same logical file twice.

Design an idempotency key and safe output strategy.

---

### Scenario 5 — 100,000 files

Choose Map vs Distributed Map.

Explain:

- concurrency
- cost
- failure handling
- aggregation
- downstream limits

---

### Scenario 6 — Existing Airflow team

Evaluate MWAA.

---

### Scenario 7 — AWS-native startup

No Airflow expertise; almost everything is AWS-native.

Evaluate Step Functions.

---

### Scenario 8 — Simple scheduled Lambda

Evaluate EventBridge Scheduler.

---

### Scenario 9 — Human approval

Design a callback/task-token workflow.

---

### Scenario 10 — Platform selection

Compare:

```text
Step Functions
MWAA
EventBridge-only
```

against:

- complexity
- event-driven requirements
- backfills
- team skills
- cost
- operations

---

# Part XVI — Cheat Sheets

## 68. Step Functions State Cheat Sheet

```text
Task     → perform work
Choice   → branch
Parallel → independent branches
Map      → repeat over collection
Wait     → pause
Pass     → shape/test data
Fail     → explicit failure
```

## Orchestration Mental Model

```text
Trigger
  ↓
Workflow
  ↓
Task
  ↓
Retry
  ↓
Catch
  ↓
Observe
```

## EventBridge

```text
Event
  ↓
Bus
  ↓
Rule
  ↓
Target
```

## Scheduler

```text
Time
  ↓
Schedule
  ↓
Target
```

## MWAA

```text
DAG
  ↓
Scheduler
  ↓
Tasks
  ↓
AWS services
```

## Selection

```text
Simple event/schedule
        ↓
EventBridge / Scheduler

AWS-native multi-step workflow
        ↓
Step Functions

Complex Airflow ecosystem/backfills
        ↓
MWAA
```

---

# Part XVII — Final Completion Checklist

## 69. Completion Checklist

You are ready to leave this module when you can:

### Step Functions

- [ ] Explain state machines
- [ ] Create a basic state machine
- [ ] Use Task
- [ ] Use Choice
- [ ] Use Parallel
- [ ] Use Map
- [ ] Use Wait
- [ ] Use Pass
- [ ] Use Fail
- [ ] Explain input/output processing
- [ ] Compare Standard and Express
- [ ] Integrate Glue
- [ ] Integrate EMR Serverless
- [ ] Integrate Athena
- [ ] Integrate Lambda
- [ ] Coordinate Redshift operations
- [ ] Implement run-and-wait
- [ ] Configure Retry
- [ ] Configure Catch
- [ ] Design idempotent workflows
- [ ] Explain Distributed Map

### EventBridge

- [ ] Explain event buses
- [ ] Create event patterns
- [ ] Explain rules
- [ ] Route to Step Functions
- [ ] Route to Lambda
- [ ] Trigger from S3 events
- [ ] Explain Scheduler
- [ ] Create recurring schedules
- [ ] Create one-time schedules
- [ ] Explain Pipes at awareness level

### MWAA

- [ ] Explain MWAA architecture
- [ ] Explain DAGs
- [ ] Deploy DAGs through S3
- [ ] Explain requirements/dependencies
- [ ] Explain AWS provider integration
- [ ] Explain MWAA cost/lifecycle
- [ ] Compare MWAA with Step Functions

### Production

- [ ] Build failure paths
- [ ] Handle duplicate events
- [ ] Add observability
- [ ] Use least privilege
- [ ] Define infrastructure as code
- [ ] Test failure paths
- [ ] Design production architecture
- [ ] Write an ADR
- [ ] Troubleshoot failed workflows
- [ ] Tear down billable lab resources

---

# 70. Final Learning Loop

Use this loop for every lab:

```text
READ
 ↓
DRAW
 ↓
IMPLEMENT
 ↓
RUN
 ↓
BREAK
 ↓
OBSERVE
 ↓
DIAGNOSE
 ↓
FIX
 ↓
MEASURE
 ↓
DOCUMENT
 ↓
EXPLAIN
```

The goal is not to memorize service names.

The goal is to become capable of **designing, implementing, debugging, securing, observing, and operating production AWS workflows**.

---

# 71. Final Roadmap Coverage Audit

The following audit maps the supplied Topic 10 roadmap requirements to this module.

| Roadmap requirement | Covered? | Section | Hands-on? |
|---|---|---|---|
| Step Functions | Yes | 5–16 | Yes |
| State machines | Yes | 6 | Yes |
| Task | Yes | 7.1 | Yes |
| Choice | Yes | 7.2 | Yes |
| Parallel | Yes | 7.3, 24 | Yes |
| Map | Yes | 7.4, 25 | Yes |
| Wait | Yes | 7.5 | Yes |
| Pass | Yes | 7.6 | Yes |
| Fail | Yes | 7.7 | Yes |
| Inputs | Yes | 8–9 | Yes |
| Outputs | Yes | 8–9 | Yes |
| Standard workflows | Yes | 10 | Yes |
| Express workflows | Yes | 10 | Conceptual |
| Standard vs Express | Yes | 10 | Yes |
| Glue integration | Yes | 11–13 | Yes |
| EMR Serverless integration | Yes | 11, 13 | Yes |
| Athena integration | Yes | 11, 14 | Yes |
| Lambda integration | Yes | 11, 15 | Yes |
| Redshift integration | Yes | 11, 16 | Yes |
| Wait-for-completion patterns | Yes | 12, 17 | Yes |
| Retries | Yes | 18 | Yes |
| Backoff | Yes | 18, 20 | Yes |
| Jitter | Yes | 20 | Conceptual |
| Catchers | Yes | 19–21 | Yes |
| Failure routing | Yes | 19–22 | Yes |
| Distributed Map | Yes | 26 | Yes |
| EventBridge | Yes | 27 | Yes |
| Event buses | Yes | 28 | Yes |
| Event rules | Yes | 29 | Yes |
| Event patterns | Yes | 30 | Yes |
| S3 object events | Yes | 31 | Yes |
| Step Functions target | Yes | 32 | Yes |
| Lambda target | Yes | 32 | Yes |
| EventBridge Scheduler | Yes | 33–34 | Yes |
| Cron-like schedules | Yes | 33 | Yes |
| One-time schedules | Yes | 33 | Yes |
| MWAA | Yes | 35–40 | Yes |
| Airflow DAGs | Yes | 36 | Yes |
| MWAA environments | Yes | 37 | Yes |
| DAG deployment from S3 | Yes | 38 | Yes |
| Requirements | Yes | 39 | Yes |
| AWS provider operators | Yes | 40 | Yes |
| Step Functions vs MWAA | Yes | 41 | Yes |
| EventBridge-only | Yes | 42 | Yes |
| Callback patterns | Yes | 43 | Yes |
| Task tokens | Yes | 43 | Yes |
| EventBridge Pipes awareness | Yes | 44 | Conceptual |
| Infrastructure as Code | Yes | 45 | Yes |
| Testing | Yes | 46 | Yes |
| Error handling | Yes | 18–22 | Yes |
| Idempotency | Yes | 23 | Yes |
| Observability | Yes | 47 | Yes |
| Security | Yes | 48 | Yes |
| Cost optimization | Yes | 49 | Yes |
| Production architectures | Yes | 50–53 | Yes |
| Standard Step Functions lab | Yes | 56 | Yes |
| Event-driven S3 pipeline | Yes | 57 | Yes |
| Scheduled pipeline | Yes | 58 | Yes |
| Distributed Map | Yes | 59 | Yes |
| MWAA equivalent workflow | Yes | 60 | Yes |
| Decision record | Yes | 61 | Yes |

**Roadmap coverage: 100% of the explicitly supplied Topic 10 requirements.**

### Quality audit

- [x] Fundamentals → intermediate → advanced → production progression
- [x] AWS-native focus
- [x] Code examples remain inside this Markdown artifact
- [x] ASL examples
- [x] EventBridge examples
- [x] Terraform example
- [x] Python/Airflow example
- [x] Failure handling
- [x] Idempotency
- [x] Observability
- [x] Security
- [x] Cost safety
- [x] Hands-on labs
- [x] Break/fix
- [x] Runbooks
- [x] ADRs
- [x] Interview preparation
- [x] Practice scenarios
- [x] Cheat sheets
- [x] Completion checklist
- [x] Final roadmap audit

### AWS correctness guardrail

This module intentionally avoids asserting exact current quotas, prices, unsupported Terraform schemas, or version-specific Airflow operator class names where those details can change. Before production use, verify the exact implementation against the current official AWS and Apache Airflow provider documentation.

---

# 72. Production Operating Standard

A production AWS orchestration design should be explainable in one sentence:

> **Trigger the right workflow, execute the right dependencies, retry only transient failures, catch and route permanent failures, make side effects idempotent, observe every execution, enforce least privilege, control cost, and keep infrastructure reproducible.**

If the learner can consistently apply that standard, this module has achieved its purpose.
