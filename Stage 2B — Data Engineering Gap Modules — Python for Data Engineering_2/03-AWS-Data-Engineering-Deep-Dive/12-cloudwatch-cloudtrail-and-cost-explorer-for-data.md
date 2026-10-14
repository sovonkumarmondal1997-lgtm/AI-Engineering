# Topic 12 — CloudWatch, CloudTrail, and Cost Explorer for Data

> **Production Data Engineering module:** observe the platform, investigate failures, audit actions, attribute cost, and operate AWS data workloads safely.

**Stage:** 2B — AWS Data Engineering Deep Dive  
**Phase:** E — Operating, Securing, and Unifying  
**Topic:** 12 — CloudWatch, CloudTrail, and Cost Explorer for data  
**Prerequisites:** Topics 01–11 and practical familiarity with S3, Glue, Athena, Redshift, Kinesis, Firehose, MSK, EMR, Step Functions, Lambda, and DMS.  
**Primary goal:** learn to answer five operational questions with evidence rather than guesswork.

```text
1. Is my pipeline healthy?
   → CloudWatch Metrics + Alarms + Dashboards

2. What failed and why?
   → CloudWatch Logs + Logs Insights + EventBridge + service logs

3. Who changed or accessed something?
   → CloudTrail + S3 audit + Athena / CloudTrail Lake

4. How much is this pipeline costing?
   → Cost Explorer + tags + Budgets + Billing Data Exports

5. Why did our AWS bill suddenly increase?
   → Cost Explorer + anomaly detection + CloudWatch + CloudTrail + billing data
```

> **Learning loop:** Read → Draw the architecture → Estimate cost → Write Terraform → Deploy with least privilege → Run a realistic workload → Break it → Observe metrics/logs/trail → Measure cost → Tear down → Write it down.

---

## 1. What This Module Is Really Teaching

A production data platform is not complete when the pipeline successfully writes data.

It is complete when engineers can answer:

- Is it healthy?
- Is it meeting its latency and reliability objectives?
- What happened during an incident?
- Which component is responsible?
- Who changed the system?
- Who accessed sensitive data?
- How much does the workload cost?
- Can the team prove what happened?
- Can the team detect abnormal spending?
- Can the team recover without blindly restarting services?

The central distinction is:

```text
Observability
= understanding system behavior

Auditability
= proving identity + action + resource + time + evidence

FinOps
= measuring + attributing + analyzing + controlling cost
```

AWS CloudWatch, CloudTrail, EventBridge, and AWS Cost Management services answer different questions. They should be composed rather than treated as interchangeable tools.

---

# Phase 1 — CloudWatch Fundamentals

## 2. CloudWatch Mental Model

A simple mental model:

```text
CloudWatch Metrics
= Is the system healthy?

CloudWatch Logs
= What happened?

CloudWatch Alarms
= When should I react?

CloudWatch Dashboards
= What should I see quickly?

EventBridge
= What event should trigger an action?
```

CloudWatch is the primary telemetry plane for runtime behavior.

A metric is a stream of measurements over time.

A log is a record of an event or message.

An alarm evaluates a metric or supported metric expression against conditions and can initiate an action.

A dashboard presents operational information in a form optimized for rapid interpretation.

### Why Data Engineers need CloudWatch

A data engineer may operate:

```text
S3
  ↓
Glue
  ↓
Kinesis / Firehose
  ↓
EMR
  ↓
Redshift / Athena
  ↓
Step Functions
```

A failure in one component can surface as a symptom in another.

For example:

```text
Kinesis consumer slows
        ↓
IteratorAgeMilliseconds rises
        ↓
downstream processing becomes stale
        ↓
business pipeline latency increases
```

The engineer needs telemetry at several layers rather than one generic "pipeline failed" signal.

---

## 3. CloudWatch Metric Anatomy

A metric should be understood as:

```text
Namespace
+ Metric name
+ Dimensions
+ Timestamp
+ Value
+ Unit
+ Statistic
+ Period
```

### Namespace

A namespace groups related metrics.

Examples include service namespaces such as:

```text
AWS/Glue
AWS/Kinesis
AWS/Firehose
AWS/Redshift
AWS/Lambda
AWS/States
```

Exact service-specific metric availability and dimensions should be verified against current AWS documentation.

### Metric name

The metric describes the measured signal.

Examples relevant to data engineering include:

```text
IteratorAgeMilliseconds
ThrottledRecords
DeliveryToS3.DataFreshness
Errors
Duration
```

Do not memorize names in isolation. First identify the operational question.

### Dimensions

Dimensions identify the resource or slice represented by the metric.

Conceptually:

```text
Metric:
IteratorAgeMilliseconds

Dimension:
StreamName = orders-stream
```

The same metric name can represent many independent time series.

### Statistic

Common statistics include:

```text
Average
Minimum
Maximum
Sum
SampleCount
```

The correct statistic depends on the signal.

For lag:

```text
Maximum or appropriately aggregated lag
```

may be more operationally useful than an average that hides a badly delayed partition.

For counts:

```text
Sum
```

may be appropriate.

Always confirm the semantics of the metric before selecting a statistic.

### Period

The period is the aggregation interval.

For example:

```text
60 seconds
300 seconds
```

A short period can detect fast incidents but may be noisier.

A longer period smooths transient behavior but can delay detection.

### Standard vs custom metrics

Standard AWS service metrics are emitted by AWS services.

Custom metrics are emitted by applications or your platform.

Custom metrics should be deliberately designed.

Bad pattern:

```text
metric{user_id=123}
metric{user_id=124}
metric{user_id=125}
...
```

Potentially better:

```text
metric{pipeline=orders, environment=prod}
```

The goal is useful operational aggregation without uncontrolled dimensionality.

---

## 4. Choosing Metrics Like a Data Engineer

Start with the question.

| Operational question | Useful telemetry |
|---|---|
| Is the pipeline running? | execution/state metrics |
| Is streaming falling behind? | iterator age / lag |
| Is ingestion throttled? | throttling metrics |
| Is delivery failing? | delivery failure metrics |
| Is compute saturated? | utilization/capacity metrics |
| Is warehouse workload degrading? | queue/runtime/workload metrics |
| Are workflows failing? | execution failure/state metrics |
| Why did one run fail? | logs + execution metadata |

A production metric should have:

```text
Signal
→ owner
→ threshold/SLO relationship
→ action
→ runbook
```

A dashboard full of metrics without an operational action is telemetry, not operational design.

---

# Phase 2 — AWS Data Engineering Metrics

## 5. Glue Monitoring

For AWS Glue, monitor the signals that matter to the workload:

- execution success/failure
- runtime
- throughput where available
- retries
- resource pressure where available
- job-specific error logs

A useful Glue operating view:

```text
Glue job
   │
   ├── execution state
   ├── duration
   ├── logs
   └── downstream freshness
```

A successful Glue execution does not automatically mean the business pipeline is healthy.

Example:

```text
Glue = SUCCEEDED
but
downstream table freshness = 3 hours late
```

The platform is operationally unhealthy even though the job status is green.

### Production rule

Monitor both:

```text
component health
+
data-product health
```

---

## 6. EMR Monitoring

For EMR workloads, observe:

- cluster/application state
- application runtime
- Spark application behavior
- executor/driver symptoms
- resource pressure
- failed steps
- logs
- downstream freshness

Use CloudWatch for service/platform telemetry and Spark/EMR logs for execution detail.

A useful incident sequence is:

```text
CloudWatch
→ cluster/application health
→ step status
→ logs
→ Spark UI / application evidence
→ root cause
```

Do not assume CloudWatch alone explains a Spark performance problem.

---

## 7. Kinesis Data Streams Monitoring

For streaming pipelines, lag is one of the most important operational signals.

### IteratorAgeMilliseconds

Conceptually:

```text
IteratorAgeMilliseconds
=
How old is the data being consumed?
```

If iterator age grows continuously:

```text
producer rate
>
consumer processing capacity
```

or a downstream bottleneck is preventing the consumer from keeping up.

Possible causes:

- consumer CPU saturation
- slow downstream database
- throttling
- insufficient consumer parallelism
- hot shard
- network issue
- checkpoint/processing problem
- downstream retry storm

### Throttling

Throttling is not merely an error count.

It can indicate:

```text
requested throughput
>
available service capacity
```

Investigate:

```text
producer behavior
+
shard capacity
+
consumer behavior
+
retry behavior
```

### Production rule

Do not alert only on:

```text
"consumer is alive"
```

Also alert on:

```text
"consumer is keeping up"
```

---

## 8. Firehose Monitoring

For Amazon Data Firehose, monitor appropriate delivery and freshness signals for the destination.

Operational questions:

```text
Is data arriving?
Is data being delivered?
Is delivery failing?
Is delivery becoming stale?
Is transformation failing?
```

Use service-specific current metric documentation to select exact metric names and dimensions for the destination.

A generic model:

```text
Producer
  ↓
Firehose
  ├── buffering
  ├── transformation
  └── delivery
        ↓
Destination
```

A successful producer does not prove destination delivery is healthy.

---

## 9. Redshift Monitoring

Redshift monitoring should answer:

```text
Are queries completing?
Are queries waiting?
Is workload pressure increasing?
Is concurrency becoming a bottleneck?
Is performance degrading?
```

Signals may include:

- query runtime
- queue time
- workload pressure
- concurrency
- storage/capacity signals
- query errors

Exact metric names and dimensions vary by Redshift deployment and current AWS capabilities; verify the current Redshift monitoring documentation before encoding alarms.

### Example reasoning

```text
Query latency ↑
        ↓
Queue time ↑
        ↓
Concurrency / workload pressure?
        ↓
Resource contention?
        ↓
Workload-management evidence
```

Do not immediately scale the warehouse before establishing whether the problem is queueing, inefficient SQL, data distribution, or an external dependency.

---

## 10. Athena Monitoring

Athena is serverless, so monitoring should emphasize:

- query execution state
- query failures
- query duration
- bytes scanned
- workgroup-level governance
- workload/cost indicators
- data freshness where Athena is part of a pipeline

A useful mental model:

```text
Athena problem
= performance + correctness + scan volume + cost
```

For cost-conscious operations:

```text
Parquet
+ partitioning
+ projection where appropriate
+ workgroups
+ query discipline
```

are often more important than simply increasing concurrency.

---

## 11. Step Functions Monitoring

For workflows, monitor:

- failed executions
- execution counts
- execution duration
- retries
- state-level failures where useful

A workflow-level signal is:

```text
Step Functions
  ↓
Execution failed
```

A root-cause signal may be:

```text
Task state
  ↓
Glue / Lambda / EMR / Athena / Redshift
  ↓
service-specific logs
```

The orchestration layer tells you that the workflow failed. The task's service telemetry usually explains why.

---

# Phase 3 — CloudWatch Logs

## 12. Logs Mental Model

```text
Metrics
= "Something is wrong."

Logs
= "Here is evidence about what happened."
```

A CloudWatch log group contains log streams.

A log stream represents a sequence of log events from a source.

A log event has a timestamp and message.

Conceptually:

```text
Log Group
├── Stream A
│   ├── event
│   ├── event
│   └── event
└── Stream B
    ├── event
    └── event
```

### Important properties

Understand:

- log groups
- log streams
- log events
- timestamps
- ingestion
- retention
- filtering
- querying
- structured logs
- JSON logs
- correlation IDs
- run IDs

---

## 13. Structured Logging

Prefer structured logs for production pipelines.

Example:

```json
{
  "timestamp": "2026-10-06T12:10:22Z",
  "level": "ERROR",
  "service": "orders-loader",
  "pipeline": "orders",
  "run_id": "run-20261006-1210",
  "component": "merge",
  "table": "gold.orders",
  "error_code": "TARGET_TIMEOUT",
  "message": "Target operation exceeded timeout"
}
```

This makes incident investigation much easier.

Useful fields:

```text
timestamp
level
service
pipeline
run_id
execution_id
component
dataset
table
error_code
message
```

Never log:

```text
passwords
API keys
access tokens
secrets
unnecessary PII
```

Observability data can itself become sensitive data.

---

## 14. Log Retention

Do not automatically keep every log forever.

Use a policy:

```text
Debug logs
→ shorter retention

Operational logs
→ retention based on incident needs

Security/audit logs
→ retention based on compliance and governance

Long-term evidence
→ appropriate archival/storage strategy
```

Before selecting retention, ask:

```text
What is the operational value?
What is the compliance requirement?
What is the storage cost?
Can the log be archived?
Who needs access?
```

Retention is an engineering decision, not a default setting.

---

# Phase 4 — CloudWatch Logs Insights

## 15. What Problem Does Logs Insights Solve?

When an incident produces thousands of log events, reading them one by one is inefficient.

Logs Insights allows you to query log data interactively.

The mental model:

```text
Log group
   ↓
Time window
   ↓
Filter
   ↓
Parse
   ↓
Aggregate
   ↓
Rank
   ↓
Investigate
```

---

## 16. First Logs Insights Query

```text
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

Line by line:

```text
fields
```

selects fields to display.

```text
filter
```

reduces the event set.

```text
sort
```

orders results.

```text
limit
```

prevents an uncontrolled result set.

Always restrict the time window during an incident.

---

## 17. Count Errors

```text
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as error_count
```

This answers:

```text
How many matching error events occurred?
```

---

## 18. Errors Per Minute

```text
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as errors by bin(5m)
| sort bin(5m) asc
```

This helps build an incident timeline.

Mental model:

```text
errors
  ↑
  │        ███
  │      ██████
  │  ██ ███████
  └────────────────→ time
```

---

## 19. Failures by Job

For structured logs:

```text
fields @timestamp, job, run_id, error_code
| filter level = "ERROR"
| stats count() as failures by job
| sort failures desc
```

The exact field names depend on your emitted JSON schema.

---

## 20. Investigate One Run

```text
fields @timestamp, level, pipeline, run_id, component, message
| filter run_id = "run-20261006-1210"
| sort @timestamp asc
```

This is one of the most useful operational patterns.

A run ID turns an unstructured incident into a traceable timeline.

---

## 21. Parse Semi-Structured Logs

If logs contain text such as:

```text
pipeline=orders run_id=abc123 component=merge duration_ms=1832
```

you can use `parse` to extract fields.

Conceptual pattern:

```text
fields @timestamp, @message
| parse @message "pipeline=* run_id=* component=* duration_ms=*" as pipeline, run_id, component, duration_ms
| filter pipeline = "orders"
| sort @timestamp desc
```

Verify current Logs Insights syntax and parser behavior in AWS documentation before production use.

---

## 22. Slowest Operations

For structured numeric fields:

```text
fields @timestamp, pipeline, component, duration_ms
| filter ispresent(duration_ms)
| sort duration_ms desc
| limit 20
```

The goal is not the query itself.

The goal is learning to convert:

```text
"pipeline is slow"
```

into:

```text
"component X dominates observed runtime during incident window Y"
```

---

# Phase 5 — CloudWatch Alarms

## 23. Alarm Mental Model

```text
Metric
  ↓
Threshold / expression
  ↓
Evaluation periods
  ↓
Alarm state
  ↓
Action
```

Common states:

```text
OK
ALARM
INSUFFICIENT_DATA
```

An alarm is not the same as a notification.

The alarm evaluates.

The configured action sends or triggers something.

---

## 24. Alarm Design

Important concepts:

- threshold
- period
- evaluation periods
- datapoints to alarm
- missing data treatment
- alarm state
- notification action
- escalation

Example:

```text
Kinesis iterator age
        >
5 minutes
for
3 of 5 periods
        ↓
ALARM
        ↓
SNS / operational notification
```

The exact threshold should come from the pipeline SLO, not an arbitrary number.

---

## 25. Missing Data

Missing data is a design choice.

Possible behaviors include:

```text
Treat as breaching
Treat as not breaching
Ignore
Use alarm configuration defaults
```

Do not choose blindly.

Ask:

```text
Does absence of telemetry mean healthy?
Does absence of telemetry mean broken?
Can the metric legitimately be sparse?
```

For an expected continuous signal, missing data can itself be operationally meaningful.

---

## 26. Alarm Examples

Good candidates include:

```text
Glue failure
Kinesis iterator age
Kinesis throttling
Firehose delivery failure
Redshift workload pressure / queueing
Step Functions failed executions
Lambda errors/duration
```

The exact metric/dimension combination must be checked against the current AWS service documentation.

---

# Phase 6 — Dashboards

## 27. Dashboard Mental Model

A dashboard should help an operator answer:

```text
What is healthy?
What is degraded?
What is failing?
What is lagging?
What requires immediate action?
```

Useful widget types include:

- time series
- single value
- metric widgets
- text
- cross-service widgets

---

## 28. Data Engineering Pipeline Dashboard

Design an example dashboard:

```text
PIPELINE HEALTH
├── Glue job success/failure
├── Glue runtime
├── Kinesis iterator age
├── Kinesis throttling
├── Firehose delivery failures
├── Redshift workload / queue indicators
├── Athena workload indicators
├── Step Functions failures
└── Lambda errors / duration
```

A production dashboard should have hierarchy.

### Operator view

```text
Current failures
Current lag
Current latency
Current retries
Immediate action
```

### Platform engineer view

```text
Service health
Capacity
Saturation
Error rates
Platform-wide trends
```

### Engineering manager view

```text
Reliability
SLA/SLO
Major incidents
Cost
Trend
```

One dashboard should not attempt to serve all audiences equally.

---

# Phase 7 — EventBridge + CloudWatch

## 29. CloudWatch vs EventBridge

Keep the roles distinct.

| Tool | Primary question |
|---|---|
| CloudWatch Metrics | How is the system behaving? |
| CloudWatch Logs | What happened in execution? |
| CloudWatch Alarms | When should I react? |
| EventBridge | Which event should trigger an action? |

CloudWatch is telemetry-centric.

EventBridge is event-routing-centric.

AWS Glue emits job state-change events to EventBridge, including `SUCCEEDED`, `FAILED`, `TIMEOUT`, and `STOPPED` states. These can target services such as SNS, SQS, Lambda, Step Functions, and others. Verify current event schemas before implementing production rules.

Source: AWS Glue EventBridge automation documentation.

---

## 30. Glue Failure Event Pattern

A conceptual EventBridge pattern:

```json
{
  "source": ["aws.glue"],
  "detail-type": ["Glue Job State Change"],
  "detail": {
    "state": ["FAILED"]
  }
}
```

Use a rule:

```text
Glue Job Failed
      ↓
EventBridge Rule
      ↓
SNS / SQS / Lambda / Step Functions
```

This is event-driven operational handling.

Do not use a polling loop when the service already emits an appropriate event.

---

## 31. EventBridge Production Concerns

Understand:

- event source
- detail-type
- event pattern
- event bus
- rule
- target
- retries
- dead-letter handling
- permissions
- idempotency

A remediation target must tolerate duplicate delivery.

For example:

```text
EventBridge event
       ↓
Lambda remediation
       ↓
check whether remediation already occurred
       ↓
act only if required
```

Event-driven does not automatically mean exactly-once.

---

# Phase 8 — CloudTrail Fundamentals

## 32. CloudTrail Mental Model

The simplest distinction:

```text
CloudWatch
= How is my system behaving?

CloudTrail
= Who did what in AWS?
```

CloudTrail records AWS account activity, including API activity made through the console, SDKs, CLI, and other AWS services.

A CloudTrail event can contain evidence such as:

```text
identity
timestamp
source IP
AWS service
API action
resource
request parameters
response elements
```

CloudTrail event records are not an ordered stack trace of all API calls; use them as audit evidence, not as an assumption of exact causal execution order.

---

## 33. Management Events

Management events represent control-plane operations.

Examples:

```text
CreateBucket
PutBucketPolicy
CreateJob
UpdateFunctionConfiguration
CreateRole
DeleteTable
AttachRolePolicy
CreateSubnet
```

They answer questions such as:

```text
Who changed this resource?
When?
From which identity?
Which API action was invoked?
```

By default, CloudTrail trails and event data stores log management events; data and other event categories require deliberate configuration and may incur additional charges.

---

## 34. Data Events

Data events are resource-level operations.

For S3, examples include:

```text
GetObject
PutObject
DeleteObject
```

They answer:

```text
Who accessed this object?
What operation occurred?
When?
Which object?
From which source?
```

Data events can be high-volume.

Therefore:

```text
Audit selectively.
Capture high-value access.
Avoid blindly logging everything.
```

This is both a security and cost-engineering principle.

---

# Phase 9 — CloudTrail Trails to S3

## 35. Trail Architecture

A common audit architecture is:

```text
AWS API Activity
       ↓
CloudTrail
       ↓
Trail
       ↓
S3
       ↓
Glue Catalog
       ↓
Athena
       ↓
Audit SQL
```

CloudTrail trails can deliver events to S3 and can optionally integrate with CloudWatch Logs and EventBridge.

A multi-Region trail records events in all enabled AWS Regions for the account.

Source: AWS CloudTrail trail documentation.

---

## 36. Audit Storage Design

A production audit bucket should have:

- restrictive bucket policy
- encryption
- controlled write access
- controlled read access
- retention/lifecycle policy
- centralized ownership where appropriate
- monitoring
- separation of duties
- protection against accidental deletion

Audit storage should not be treated like an ordinary analytics bucket.

---

# Phase 10 — CloudTrail + Athena Audit Lab

## 37. Lab: Audit the Gold Prefix

Goal:

```text
Enable S3 data-event auditing for a high-value gold prefix
and identify who accessed it.
```

Architecture:

```text
S3 gold data
      ↓
CloudTrail data events
      ↓
S3 trail destination
      ↓
Athena
      ↓
Audit query
```

Questions to answer:

```text
Who?
What?
When?
Which resource?
From where?
Which user agent?
```

CloudTrail event records expose identity, action, resource, time, and related context through fields whose exact presence depends on the event type.

---

## 38. Athena Audit Query Pattern

CloudTrail log structures can be queried with Athena. AWS provides current CloudTrail/Athena guidance and table definitions; use the current AWS schema rather than hard-coding an outdated table.

Conceptual query:

```sql
SELECT
    eventtime,
    useridentity.type,
    useridentity.arn,
    eventname,
    sourceipaddress,
    useragent,
    requestparameters
FROM cloudtrail_logs
WHERE eventsource = 's3.amazonaws.com'
  AND eventname IN ('GetObject', 'PutObject', 'DeleteObject')
  AND eventtime >= current_timestamp - INTERVAL '7' DAY
ORDER BY eventtime DESC;
```

For an S3 prefix investigation, filter the appropriate S3 object/resource field after validating the current CloudTrail table schema.

Do not assume that a logical table read maps one-to-one to one S3 `GetObject` event. Higher-level services may read multiple underlying objects and may use service principals.

---

# Phase 11 — Cost Explorer for Data Engineers

## 39. Financial Observability

Technical observability asks:

```text
Is the system healthy?
```

Financial observability asks:

```text
Is the system economically healthy?
```

Cost Explorer supports interactive analysis of AWS cost and usage dimensions.

Useful analysis dimensions can include:

```text
service
account
Region
usage type
time period
cost allocation tag
```

Exact available dimensions and granularity should be verified against the current Billing and Cost Management documentation.

---

## 40. Practical Cost Questions

Use Cost Explorer to investigate:

```text
How much did Glue cost?

How much did Athena cost?

How much did Redshift cost?

How much did Kinesis cost?

How much did EMR cost?

How much did CloudWatch cost?

How much did CloudTrail cost?
```

Then move from service-level cost toward workload-level allocation.

---

# Phase 12 — Cost Allocation Tags

## 41. Tagging Standard

A practical data-platform standard:

```text
Environment=prod
Team=data-platform
Pipeline=orders
Owner=data-engineering
CostCenter=DE-001
Application=orders-platform
ManagedBy=terraform
```

Tagging only works when it is:

```text
consistent
+
activated where required
+
applied to billable resources
+
maintained by IaC
```

Not every AWS charge is directly attributable to a resource tag.

Shared costs may require allocation rules.

AWS Cost Management supports cost allocation tags and cost categories for organizing costs. Current AWS capabilities should be checked before treating a tag as a universally available billing dimension.

---

## 42. Terraform Tagging Pattern

A simplified Terraform pattern:

```hcl
terraform {
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "dev"
      Team        = "data-platform"
      ManagedBy   = "terraform"
    }
  }
}
```

Add resource-specific tags:

```hcl
resource "aws_s3_bucket" "orders" {
  bucket = var.bucket_name

  tags = {
    Pipeline   = "orders"
    Owner      = "data-engineering"
    CostCenter = "DE-001"
  }
}
```

Verify current AWS provider behavior for the resources you deploy.

---

# Phase 13 — AWS Budgets

## 43. Budget Mental Model

```text
Budget
=
"Am I approaching a known spending limit?"
```

A budget can monitor actual and/or forecasted cost or usage against a defined threshold.

Example:

```text
Pipeline: orders
Monthly budget: $100

Warning:
70%

Critical:
90%
```

Treat budgets as preventive controls.

A budget alert is useful because it can trigger action before the billing cycle ends.

AWS Budgets can be combined with SNS and other notification mechanisms. Exact capabilities should be verified in current AWS Billing documentation.

---

# Phase 14 — Pipeline-Level Cost Attribution

## 44. From Account Cost to Unit Economics

A mature FinOps progression is:

```text
AWS account cost
      ↓
service cost
      ↓
team cost
      ↓
pipeline cost
      ↓
dataset cost
      ↓
unit economics
```

Examples:

```text
cost per pipeline
cost per dataset
cost per million records
cost per TB processed
cost per successful workflow
cost per customer
cost per business transaction
```

---

## 45. Shared-Cost Problem

Consider:

```text
Shared Glue job
Shared S3 bucket
Shared KMS
Shared NAT
Shared Redshift
Shared Athena workgroup
```

These resources may support multiple pipelines.

Therefore:

> Cost attribution is often an allocation problem, not simply a billing lookup.

Possible allocation bases:

```text
bytes processed
records processed
query execution time
job runtime
workload share
storage consumed
tagged resource ownership
business transaction volume
```

Document the allocation rule.

A useful unit economics record is:

```text
Metric
Definition
Source
Allocation rule
Period
Owner
Known limitations
```

---

# Phase 15 — Billing Data Exports + Athena

## 46. Why Billing Exports?

Cost Explorer is excellent for interactive exploration.

Detailed billing exports are useful when you need:

```text
SQL
joins
repeatable analytics
custom allocation
unit economics
historical analysis
automation
```

Architecture:

```text
AWS billing data
      ↓
Billing Data Export
      ↓
S3
      ↓
Glue Catalog
      ↓
Athena
      ↓
Cost analytics
```

AWS billing export schemas evolve. Do **not** hard-code exact column names from memory. Inspect the current AWS Billing Data Exports schema in the account before creating production SQL.

---

## 47. Cost Analytics Query Pattern

After discovering the current schema:

```sql
SELECT
    service,
    SUM(unblended_cost) AS cost
FROM billing_export
WHERE usage_date >= DATE '2026-10-01'
  AND usage_date <  DATE '2026-11-01'
GROUP BY service
ORDER BY cost DESC;
```

Treat this as a **pattern**, not a guaranteed schema.

Your implementation should first verify:

```text
table name
column names
data types
date semantics
currency fields
tag fields
partition columns
```

---

## 48. Unit Economics

Suppose:

```text
Monthly allocated pipeline cost = $1,200
Successful runs = 240
```

Then:

```text
cost per successful run
= $1,200 / 240
= $5
```

If:

```text
records processed = 120 million
```

Then:

```text
cost per million records
= $1,200 / 120
= $10
```

Always distinguish:

```text
observed direct cost
allocated shared cost
estimated unit cost
```

Do not present an allocation as an exact AWS billing fact.

---

# Phase 16 — Cost Anomaly Detection

## 49. Budget vs Anomaly Detection

Mental model:

```text
Budget
= Am I approaching a known spending limit?

Cost anomaly detection
= Is spending behaving unusually?
```

Examples:

```text
runaway Glue jobs
excessive Athena scans
forgotten EMR cluster
unexpected Kinesis capacity
CloudWatch log ingestion spike
excessive CloudTrail data events
unexpected NAT traffic
```

Do not assume anomaly detection catches every incident or operates at an exact threshold you have not verified.

Use it as another signal in a cost investigation.

---

# Phase 17 — CloudWatch Cost Control

## 50. Log Cost

CloudWatch cost can grow because of:

```text
log ingestion
log storage
verbose logging
long retention
large payloads
high event volume
```

Controls:

```text
shorter debug retention
structured logs
appropriate log levels
sampling for high-volume diagnostics
aggregation
archival where justified
```

Do not sample:

```text
required security evidence
critical failure signals
required compliance records
```

---

## 51. Metric Cost and Cardinality

High-cardinality metric dimensions can create a large number of unique time series.

Bad:

```text
metric{user_id=...}
```

Better:

```text
metric{pipeline=..., environment=...}
```

Ask:

```text
Do I need this dimension?
Will an operator act on it?
Can I aggregate it?
Can the application expose the same information through logs?
```

Emit fewer, higher-value metrics.

---

# Phase 18 — CloudTrail Lake Awareness

## 52. CloudTrail Lake

CloudTrail Lake provides event data stores and SQL-based investigation capabilities.

Conceptually:

```text
Traditional trail
→ events
→ S3
→ Athena

CloudTrail Lake
→ event data store
→ query within CloudTrail Lake
```

Current AWS documentation notes an important availability change: CloudTrail Lake will no longer be open to new customers starting **May 31, 2026**; existing customers can continue using it. This module therefore treats CloudTrail Lake as roadmap-required awareness, not as a recommendation to start a new deployment without checking current account eligibility and AWS guidance.

For new designs, verify current AWS availability and alternatives before choosing CloudTrail Lake.

---

## 53. CloudTrail S3 + Athena vs CloudTrail Lake

| Question | CloudTrail → S3 → Athena | CloudTrail Lake |
|---|---|---|
| Open lake architecture | Strong | Managed event store |
| Reuse in data lake | Strong | Different model |
| SQL investigation | Strong | Strong |
| Existing S3 audit platform | Natural fit | Additional service model |
| Cross-account investigation | Can be engineered | Strong managed experience where available |
| New-customer availability | Generally available pattern | Verify current availability |
| Cost model | Trail + S3 + Athena | Lake ingestion/storage/query pricing |

Do not choose solely from feature count. Choose from:

```text
availability
security
retention
query needs
existing architecture
cost
operational ownership
```

---

# Phase 19 — Organization-Wide Trails

## 54. Enterprise Multi-Account Audit

A mature AWS organization may have:

```text
AWS Organization
│
├── Security Account
├── Log Archive Account
├── Data Platform Account
├── Production Account
└── Development Account
```

Central audit model:

```text
Organization
     ↓
CloudTrail
     ↓
Central audit storage
     ↓
Athena / approved investigation tooling
```

The goal is:

```text
central evidence
+
separation of duties
+
controlled access
+
consistent retention
```

Organization-level architecture should be designed with AWS Organizations and security-account governance in mind.

---

# Phase 20 — End-to-End Observability Architecture

## 55. Reference Architecture

```text
                  ┌────────────────────┐
                  │    Data Sources    │
                  └─────────┬──────────┘
                            ↓
                    Ingestion Layer
                            ↓
              ┌──────────────────────────┐
              │      AWS Data Platform   │
              │ Glue / Kinesis / Firehose│
              │ EMR / Redshift / Athena  │
              └────────────┬─────────────┘
                           │
             ┌─────────────┼──────────────┐
             ↓             ↓              ↓
        CloudWatch      CloudTrail     Cost Tools
        Metrics/Logs    Audit Events    Billing
             │             │              │
             ↓             ↓              ↓
        Dashboards      S3/Lake        Cost Explorer
        Alarms          + Athena        Budgets
             │             │              │
             └─────────────┼──────────────┘
                           ↓
                    Data Platform Ops
                           │
                ┌──────────┴──────────┐
                ↓                     ↓
            Incident             FinOps / Audit
            Response             Governance
```

Each plane answers a different question.

---

# Phase 21 — Hands-On Project: `infra/observability/`

## 56. Project Objective

Create an observability exercise under:

```text
infra/observability/
```

The Markdown file contains the specification; the learner creates the project files during the lab.

The project must be:

```text
IaC
least privilege
observable
cost-controlled
breakable
recoverable
documented
```

Do not create these project files as part of this module artifact.

---

## 57. Exercise 1 — Glue Monitoring

Implement monitoring for:

```text
Glue job failure
Glue runtime
Glue execution status
```

Deliver:

```text
metric/alarm design
dashboard widget
notification path
runbook
```

Break the job intentionally.

Observe:

```text
alarm
event
logs
execution metadata
```

---

## 58. Exercise 2 — Kinesis Monitoring

Create alarms or equivalent monitoring for:

```text
IteratorAgeMilliseconds
throttling
throughput / lag-related health
```

Experiment:

```text
healthy consumer
→ slow consumer
→ rising iterator age
→ alert
→ recovery
```

Document:

```text
symptom
evidence
root cause
remediation
verification
```

---

## 59. Exercise 3 — Firehose Monitoring

Monitor:

```text
delivery failures
delivery latency/freshness
destination health
```

Verify the exact current metrics for the chosen destination before creating alarms.

---

## 60. Exercise 4 — Redshift Monitoring

Monitor an appropriate workload-health signal:

```text
queue time
workload pressure
query performance
```

Do not hard-code a metric without checking current Redshift documentation and deployment mode.

Create:

```text
dashboard
alarm
runbook
```

---

## 61. Exercise 5 — Step Functions

Monitor:

```text
failed executions
execution counts
workflow health
```

Connect a workflow failure to the investigation path:

```text
Step Functions
→ failed execution
→ task
→ task-service logs
→ root cause
```

---

## 62. Exercise 6 — Unified Notification

Implement:

```text
AWS service
    ↓
CloudWatch / EventBridge
    ↓
Alarm / Rule
    ↓
SNS or approved notification target
```

Document:

```text
signal
owner
severity
notification channel
escalation
runbook
```

---

# Phase 22 — CloudWatch Dashboard Lab

## 63. Dashboard Build

Build:

```text
Pipeline Health
├── Glue
├── Kinesis
├── Firehose
├── Redshift
├── Athena
├── Step Functions
└── Lambda where relevant
```

Require the operator to answer:

```text
What is healthy?
What is degraded?
What is failing?
What is lagging?
What requires immediate action?
```

Do not grade the dashboard by the number of widgets.

Grade it by how quickly an operator can form a correct hypothesis.

---

# Phase 23 — Logs Insights Incident Lab

## 64. Incident A — Glue Failure

Determine:

```text
When did it fail?
Which job?
Which run?
What error?
What dependency failed?
```

Deliver:

```text
incident timeline
root-cause hypothesis
evidence
next action
```

---

## 65. Incident B — Streaming Lag

Investigate:

```text
iterator age
throttling
consumer lag
timeline
downstream latency
```

Do not restart the consumer until you have collected evidence.

---

## 66. Incident C — Application Failure

Use structured logs containing:

```text
run_id
timestamp
level
component
error
```

Construct a chronological incident timeline.

---

# Phase 24 — CloudTrail S3 Audit Lab

## 67. Audit Exercise

Build:

```text
S3 gold data
      ↓
CloudTrail data events
      ↓
S3 audit trail
      ↓
Athena
      ↓
Audit SQL
```

Answer:

```text
Who accessed the data?
What operation occurred?
When?
Which object?
From which source?
```

Then repeat the design decision:

> Why should you not enable high-volume S3 data events across every bucket without a specific audit requirement?

Expected answer:

```text
volume
+
cost
+
noise
+
retention burden
```

---

# Phase 25 — Cost Reporting Lab

## 68. Cost Explorer Exercise

Create a monthly cost analysis using:

```text
Cost allocation tags
        ↓
Cost Explorer
        ↓
team / environment / pipeline breakdown
```

Produce:

```text
service cost
team cost
environment cost
pipeline allocation
```

Document which values are:

```text
directly observed
allocated
estimated
```

---

## 69. Billing Analytics Extension

Extend the exercise conceptually:

```text
Billing Data Export
       ↓
S3
       ↓
Glue Catalog
       ↓
Athena
       ↓
SQL
       ↓
Unit economics
```

Calculate:

```text
cost per pipeline
cost per million records
cost per TB processed
cost per successful run
```

---

# Phase 26 — Break/Fix Scenarios

## 70. Scenario 1 — No CloudWatch Logs

Symptom:

```text
Expected logs do not appear.
```

Investigate:

```text
wrong log group
wrong Region
missing permissions
service configuration
wrong log stream
execution did not actually start
```

---

## 71. Scenario 2 — Alarm Never Fires

Investigate:

```text
wrong metric
wrong namespace
wrong dimensions
wrong threshold
wrong period
evaluation periods
missing-data treatment
metric not emitted
```

Use:

```text
metric → dimensions → datapoints → alarm configuration
```

---

## 72. Scenario 3 — Kinesis Consumer Looks Healthy but Data Is Delayed

Investigate:

```text
IteratorAgeMilliseconds
throttling
consumer capacity
downstream bottleneck
hot shard
retry behavior
```

A process can be alive while the data product is stale.

---

## 73. Scenario 4 — Glue Job Fails but Dashboard Looks Normal

Investigate:

```text
dashboard metrics
→ execution-specific logs
→ Logs Insights
→ EventBridge event
→ timeline
```

This teaches the difference between:

```text
coarse health telemetry
vs
execution evidence
```

---

## 74. Scenario 5 — Cannot Determine Who Accessed S3 Gold Data

Investigate:

```text
CloudTrail configuration
management vs data events
bucket/prefix selector
trail/event-data-store delivery
Athena schema/query
identity fields
```

Do not assume data events were captured retroactively.

---

## 75. Scenario 6 — AWS Bill Suddenly Increases

Investigation sequence:

```text
Cost Explorer
→ time window
→ service
→ usage type
→ account / Region
→ cost allocation tags
→ deployment/activity history
→ CloudWatch
→ CloudTrail
→ detailed billing export
```

Possible root causes:

```text
new workload
runaway job
large Athena scans
forgotten compute
log ingestion
CloudTrail data-event volume
network transfer
capacity change
```

---

## 76. Scenario 7 — CloudWatch Cost Increases

Investigate:

```text
log ingestion
log retention
verbose application logging
custom metric volume
metric dimensions
query activity
```

Then reduce cost without destroying required evidence.

---

## 77. Scenario 8 — CloudTrail Cost Increases

Investigate:

```text
data-event volume
resource scope
event selectors
unnecessary object-level auditing
new account/workload
```

Do not simply disable CloudTrail. Narrow the scope based on the audit requirement.

---

# Phase 27 — Production Runbooks

## 78. Runbook Template

Every runbook should use:

```text
1. Symptom
2. Impact
3. Evidence to collect
4. Commands / queries
5. Likely causes
6. Diagnosis
7. Remediation
8. Verification
9. Prevention
```

---

## 79. Required Runbooks

Create runbooks for:

```text
Pipeline failure
Kinesis lag
Glue failure
Firehose delivery failure
Redshift workload degradation
Step Functions failure
Missing logs
Missing CloudTrail events
Unauthorized data access investigation
Unexpected AWS cost increase
CloudWatch cost increase
CloudTrail cost increase
Budget threshold exceeded
```

A runbook is successful when another engineer can execute it safely under pressure.

---

# Phase 28 — AWS CLI Patterns

## 80. CloudWatch Metrics

A discovery pattern:

```bash
aws cloudwatch list-metrics \
  --namespace AWS/Kinesis
```

Use current AWS CLI documentation to select filters and pagination parameters.

---

## 81. CloudWatch Alarm

Conceptual pattern:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name orders-kinesis-lag \
  --namespace AWS/Kinesis \
  --metric-name IteratorAgeMilliseconds \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 300000 \
  --comparison-operator GreaterThanThreshold
```

This is an instructional pattern. Verify the metric dimensions, statistic semantics, current CLI syntax, and alarm action before production deployment.

---

## 82. Logs

```bash
aws logs describe-log-groups
```

Logs Insights queries can be started through the CloudWatch Logs API/CLI. Verify current AWS CLI syntax for the installed AWS CLI version.

---

## 83. CloudTrail

Event-history lookup:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=CreateBucket
```

Important limitation: CloudTrail Event history is limited to management events and a limited historical window; it is not a replacement for configured trails or event data stores.

---

## 84. Cost Explorer

Conceptual:

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-10-01,End=2026-11-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost
```

Verify current API permissions, dimensions, metric names, and date semantics before production automation.

---

## 85. CLI Safety Rule

Never paste credentials into commands.

Prefer:

```text
IAM role
IAM Identity Center
AWS credential provider chain
```

Before running billing or audit commands, verify the active identity:

```bash
aws sts get-caller-identity
```

---

# Phase 29 — Python / boto3

## 86. Query CloudWatch Metrics

```python
import boto3
from datetime import datetime, timedelta, timezone

cloudwatch = boto3.client("cloudwatch")

end = datetime.now(timezone.utc)
start = end - timedelta(hours=1)

response = cloudwatch.get_metric_statistics(
    Namespace="AWS/Kinesis",
    MetricName="IteratorAgeMilliseconds",
    Dimensions=[
        {"Name": "StreamName", "Value": "orders-stream"}
    ],
    StartTime=start,
    EndTime=end,
    Period=60,
    Statistics=["Maximum"],
)

for point in response.get("Datapoints", []):
    print(point)
```

Production considerations:

```text
client
→ request
→ response
→ pagination where applicable
→ retries
→ throttling
→ error handling
```

Use the AWS credential chain; never embed credentials.

---

## 87. Query Cost Explorer

```python
import boto3

ce = boto3.client("ce")

response = ce.get_cost_and_usage(
    TimePeriod={
        "Start": "2026-10-01",
        "End": "2026-11-01",
    },
    Granularity="MONTHLY",
    Metrics=["UnblendedCost"],
)

for result in response["ResultsByTime"]:
    print(result)
```

For production:

```text
paginate where supported
validate date ranges
handle throttling
store results if building a recurring report
```

Do not assume one response contains the complete dataset for every query shape.

---

## 88. CloudTrail Investigation

```python
import boto3

cloudtrail = boto3.client("cloudtrail")

response = cloudtrail.lookup_events(
    LookupAttributes=[
        {
            "AttributeKey": "EventName",
            "AttributeValue": "PutBucketPolicy",
        }
    ],
    MaxResults=50,
)

for event in response.get("Events", []):
    print(event.get("EventName"), event.get("Username"))
```

Use this for focused management-event investigations. For large-scale or cross-account SQL analysis, use the appropriate configured audit architecture.

---

# Phase 30 — Terraform Patterns

## 89. CloudWatch Log Group

```hcl
resource "aws_cloudwatch_log_group" "pipeline" {
  name              = "/data-platform/orders"
  retention_in_days = 30

  tags = {
    Environment = "prod"
    Team        = "data-platform"
    Pipeline    = "orders"
  }
}
```

---

## 90. CloudWatch Alarm

```hcl
resource "aws_cloudwatch_metric_alarm" "kinesis_lag" {
  alarm_name          = "orders-kinesis-lag"
  namespace           = "AWS/Kinesis"
  metric_name         = "IteratorAgeMilliseconds"
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 5
  threshold           = 300000
  comparison_operator = "GreaterThanThreshold"

  dimensions = {
    StreamName = var.stream_name
  }
}
```

Treat this as a pattern. Verify current AWS provider and service metric requirements before applying it.

---

## 91. Terraform Dashboard

Dashboard design should be code-reviewed.

Conceptually:

```hcl
resource "aws_cloudwatch_dashboard" "data_platform" {
  dashboard_name = "data-platform"

  dashboard_body = jsonencode({
    widgets = [
      # metric widgets
      # single-value widgets
      # text widgets
    ]
  })
}
```

Store dashboard definitions in version control.

---

## 92. Terraform + Audit

For CloudTrail/S3 audit infrastructure, explicitly design:

```text
Trail
S3 destination
bucket policy
encryption
lifecycle
least privilege
event selectors
```

Do not copy a generic CloudTrail example into production without reviewing the audit scope.

---

# Phase 31 — Security

## 93. Least Privilege

Separate permissions for:

```text
operators
developers
security investigators
billing/FinOps
audit
automation
```

A data engineer should not automatically receive unrestricted billing or audit access.

---

## 94. Audit Bucket Security

Protect audit storage with:

```text
restricted bucket policy
encryption
controlled KMS access
separation of duties
retention/lifecycle
monitoring
```

Audit evidence must not be casually deletable by the same role that performs the workload.

---

## 95. Sensitive Observability Data

Never blindly log:

```text
passwords
access tokens
API keys
database credentials
secrets
unnecessary PII
```

Redaction belongs in the application/logging layer where possible.

---

# Phase 32 — Cost Engineering

## 96. Cost Checklist

For every major component ask:

```text
What generates cost?
What increases cost?
What can be retained?
What can be sampled?
What can be aggregated?
What can be turned off?
What must be retained for compliance?
```

---

## 97. CloudWatch Cost

Review:

```text
log ingestion
log storage
retention
custom metrics
metric dimensions
query volume
verbose logging
```

---

## 98. CloudTrail Cost

Review:

```text
management-event baseline
data-event scope
resource selectors
event volume
retention
audit requirements
```

Additional event categories can have charges. Verify current AWS pricing before deployment.

---

## 99. Data-Service Cost

Tie observability to:

```text
Athena → data scanned
Kinesis → throughput/capacity
Glue → job runtime/capacity
Redshift → workload/deployment model
EMR → runtime/compute
```

Never insert current prices into a training document without checking the official pricing page.

---

# Phase 33 — Decision Matrices

## 100. CloudWatch Metrics vs Logs

| Question | Metrics | Logs |
|---|---|---|
| Is system healthy? | Strong | Weak |
| Why did it fail? | Weak | Strong |
| Trend analysis | Strong | Moderate |
| Detailed debugging | Weak | Strong |
| Alerting | Strong | Strong |

---

## 101. CloudWatch vs CloudTrail

| Question | CloudWatch | CloudTrail |
|---|---|---|
| System health | Yes | No |
| Runtime errors | Yes | No |
| AWS API activity | Limited | Yes |
| Who changed resource? | No | Yes |
| Who accessed S3 object? | No | Yes, with appropriate data events |
| Audit | Limited | Strong |

---

## 102. Cost Explorer vs Billing Export

| Capability | Cost Explorer | Billing Export + Athena |
|---|---|---|
| Quick analysis | Excellent | Moderate |
| Detailed SQL analysis | Limited | Excellent |
| Historical exploration | Strong | Strong |
| Custom unit economics | Moderate | Excellent |
| Repeatable automation | Moderate | Strong |
| Complex joins | Limited | Excellent |

---

## 103. CloudTrail S3 + Athena vs CloudTrail Lake

| Dimension | Trail + S3 + Athena | CloudTrail Lake |
|---|---|---|
| Data-lake integration | Strong | Different managed model |
| SQL | Athena SQL | CloudTrail Lake SQL |
| Ownership | More components | More managed |
| Existing S3 audit platform | Natural | Additional architecture |
| New-customer availability | Current pattern | Verify eligibility/current AWS status |
| Cost model | Trail/S3/Athena | Ingestion/storage/query |
| Long-term portability | Strong | Service-specific |

---

# Phase 34 — Production Architecture Patterns

## 104. Pattern 1 — Single Pipeline Monitoring

```text
Glue
 ↓
CloudWatch
 ↓
Alarm
 ↓
SNS
 ↓
Operator
```

Use for simple operational alerting.

---

## 105. Pattern 2 — Event-Driven Failure Handling

```text
Glue
 ↓
EventBridge
 ↓
Rule
 ↓
Notification / remediation
```

Use when the service emits a useful state-change event.

---

## 106. Pattern 3 — Enterprise Audit

```text
AWS Organization
 ↓
CloudTrail
 ↓
Central audit storage
 ↓
Athena / approved investigation tooling
 ↓
Audit investigation
```

Use separation of duties and centralized governance.

---

## 107. Pattern 4 — FinOps

```text
AWS resources
 ↓
Tags / account structure / cost categories
 ↓
Cost Explorer / Billing Export
 ↓
Athena analytics
 ↓
Pipeline allocation
 ↓
Budget / anomaly detection
```

---

## 108. Pattern 5 — Full Data Platform Observability

```text
Metrics
   +
Logs
   +
Events
   +
Audit
   +
Costs
   ↓
Dashboards
   +
Alerts
   +
Runbooks
   +
Governance
```

This is the target operating model.

---

# Phase 35 — End-to-End Incident Exercise

## 109. Incident: Orders Pipeline Becomes Delayed

Initial symptom:

```text
Orders data is late.
```

### Step 1 — Observe

```text
CloudWatch dashboard
```

Find:

```text
Kinesis IteratorAgeMilliseconds ↑
```

### Step 2 — Establish timeline

```text
When did lag start?
```

### Step 3 — Inspect related telemetry

```text
throttling
consumer runtime
downstream errors
```

### Step 4 — Query logs

Use Logs Insights to isolate:

```text
run_id
component
error
```

### Step 5 — Check events

Inspect EventBridge events for service-state changes.

### Step 6 — Check CloudTrail

Ask:

```text
Was there a recent configuration or infrastructure change?
```

### Step 7 — Check cost

Use Cost Explorer:

```text
Did a deployment change capacity or create unexpected spend?
```

### Step 8 — Remediate

Fix the verified bottleneck.

### Step 9 — Verify

```text
Iterator age ↓
consumer throughput ↑
freshness restored
alarm returns OK
```

### Step 10 — Learn

Update:

```text
runbook
dashboard
alarm
capacity assumptions
ADR if architecture changed
```

Do not restart components blindly.

Use:

```text
Observe
→ establish timeline
→ identify evidence
→ isolate bottleneck
→ verify root cause
→ remediate
→ verify recovery
→ document
```

---

# Phase 36 — ADR Exercises

## 110. ADR-001 — CloudWatch Dashboard Architecture

Write an ADR covering:

```text
Context
Decision
Alternatives
Trade-offs
Security impact
Cost impact
Operational impact
Consequences
```

Decision question:

> What should be on the operator dashboard versus the platform and management dashboards?

---

## 111. ADR-002 — CloudTrail S3 Data-Event Scope

Decision question:

> Which buckets/prefixes require object-level audit evidence?

Compare:

```text
all buckets
selected buckets
selected prefixes
specific sensitive datasets
```

---

## 112. ADR-003 — Cost Allocation Standard

Define:

```text
Environment
Team
Pipeline
Owner
CostCenter
Application
ManagedBy
```

Document exceptions for shared resources.

---

## 113. ADR-004 — Billing Export + Athena

Decision question:

> When should the platform use detailed billing exports rather than Cost Explorer alone?

---

## 114. ADR-005 — Multi-Account Audit Architecture

Decision question:

> How should CloudTrail evidence be centralized across a 30-account organization?

Include:

```text
security account
log archive account
data platform account
production
development
separation of duties
```

---

# Phase 37 — Practice Questions

## 115. Beginner

1. What is CloudWatch?
2. What is a CloudWatch metric?
3. What is a namespace?
4. What is a metric dimension?
5. What is a log group?
6. What is a log stream?
7. What is a CloudWatch alarm?
8. What is CloudTrail?
9. What is Cost Explorer?
10. What is a cost allocation tag?

### Expected learning

You should explain each without relying on memorized AWS marketing terminology.

---

## 116. Intermediate

11. Metrics vs logs: when do you use each?
12. What does `IteratorAgeMilliseconds` tell you?
13. Why can an alive Kinesis consumer still be unhealthy?
14. How do Logs Insights queries reduce incident investigation time?
15. What is the purpose of a run ID?
16. What is the difference between an alarm and a notification?
17. CloudWatch vs CloudTrail?
18. Management events vs data events?
19. Why can S3 data events become expensive?
20. How do you investigate a Glue failure?
21. How do you design a useful data-platform dashboard?
22. How do EventBridge and CloudWatch complement each other?
23. How do cost allocation tags help pipeline FinOps?
24. Why are shared costs difficult to attribute?
25. What is the difference between a budget and cost anomaly detection?

---

## 117. Advanced

26. Design observability for an AWS lakehouse.
27. How would you audit access to a finance dataset?
28. How would you investigate a sudden AWS bill increase?
29. How would you design centralized CloudTrail for a multi-account organization?
30. How would you reduce CloudWatch costs without losing important evidence?
31. How would you design pipeline-level unit economics?
32. Cost Explorer vs detailed billing exports: when do you use each?
33. CloudTrail S3 + Athena vs CloudTrail Lake: how do you choose?
34. How do metrics, logs, events, audit trails, and cost data work together?
35. How would you detect a Kinesis pipeline that is alive but increasingly stale?
36. How would you design an alarm for a workload with intermittent expected gaps?
37. How would you prevent a remediation Lambda from repeatedly acting on duplicate events?
38. How would you distinguish an application failure from an infrastructure/configuration change?
39. How would you investigate an unexpected CloudWatch bill?
40. How would you design cost allocation for shared Redshift and S3 resources?

---

# Phase 38 — Interview Preparation

## 118. Scenario: Kinesis Pipeline Delayed

> A Kinesis pipeline is delayed. How do you investigate?

Strong answer structure:

```text
1. Establish impact and time window.
2. Inspect iterator age and throttling.
3. Check consumer/downstream health.
4. Inspect logs.
5. Check recent configuration changes in CloudTrail.
6. Check deployment/activity timeline.
7. Identify bottleneck.
8. Remediate.
9. Verify recovery.
10. Update runbook/alarms.
```

---

## 119. Scenario: Intermittent Glue Failure

> A Glue job fails intermittently. What telemetry do you inspect?

Expected:

```text
execution history
CloudWatch metrics
execution logs
Logs Insights
dependency failures
resource/capacity symptoms
recent configuration changes
```

---

## 120. Scenario: 300% AWS Bill Increase

> The AWS bill increased by 300% overnight. Walk through the investigation.

Expected:

```text
Cost Explorer
→ time window
→ service
→ usage type
→ account/Region
→ tags/cost categories
→ detailed billing data
→ CloudWatch telemetry
→ CloudTrail changes
→ root cause
→ remediation
→ prevention
```

---

## 121. Scenario: Who Accessed Finance Data?

> Security asks: "Who accessed this S3 gold dataset last week?"

Expected:

```text
Confirm audit scope existed before the incident.
Identify relevant S3 data events.
Query the configured trail/audit store.
Extract identity, action, object/resource, timestamp, source context.
Validate service-principal cases.
Report evidence and limitations.
```

Do not claim evidence that was not actually collected.

---

## 122. Scenario: CloudWatch Bill High

> Your CloudWatch bill is unexpectedly high. What could cause it?

Discuss:

```text
log ingestion
log retention
verbose logging
custom metric volume
high-cardinality dimensions
query/telemetry volume
```

Then propose:

```text
retention controls
aggregation
sampling where safe
log-level controls
metric redesign
```

---

## 123. Scenario: Multi-Account Observability

> How would you design observability for a multi-account AWS data platform?

Strong answer:

```text
local runtime telemetry
+
centralized dashboards
+
central audit trail
+
security-account governance
+
log archive
+
cost organization
+
least privilege
+
runbooks
```

---

# Phase 39 — Decision-Making Exercises

## 124. Decision 1 — 100 S3 Buckets

Should you enable CloudTrail data events for every bucket?

Answer framework:

```text
Audit requirement
→ sensitive datasets
→ access patterns
→ event volume
→ cost
→ retention
→ investigation value
```

Do not default to "everything."

---

## 125. Decision 2 — Keep All Logs Forever

Should a team retain all CloudWatch logs forever?

Consider:

```text
cost
compliance
incident value
security requirements
retention policy
archival
data sensitivity
```

---

## 126. Decision 3 — Metric Per User ID

A team emits a custom metric for every user ID.

What is wrong?

Consider:

```text
cardinality
cost
operational noise
metric usefulness
aggregation
alternative structured logs
```

---

## 127. Decision 4 — Cost per Pipeline

Need detailed cost-per-pipeline reporting.

Choose:

```text
Cost Explorer
or
Billing Export + Athena
```

Expected reasoning:

```text
Cost Explorer
→ interactive exploration

Billing export + Athena
→ repeatable SQL + custom allocation + unit economics
```

A mature platform may use both.

---

## 128. Decision 5 — 30 AWS Accounts

How should CloudTrail be organized?

Evaluate:

```text
organization-wide coverage
central audit storage
security account
log archive account
least privilege
retention
investigation workflow
cost
```

---

# Phase 40 — Production Learning Loop

## 129. Required Build Loop

For every lab:

```text
Read
  ↓
Draw architecture
  ↓
Estimate cost
  ↓
Write Terraform
  ↓
Deploy with least privilege
  ↓
Run realistic workload
  ↓
Break it intentionally
  ↓
Observe metrics
  ↓
Inspect logs
  ↓
Inspect audit evidence
  ↓
Measure cost
  ↓
Fix
  ↓
Verify
  ↓
Tear down
  ↓
Write runbook
```

This module is complete only when the learner can operate a broken system, not merely create a working one.

---

# Phase 41 — Cost Safety

## 130. AWS Lab Safety Rules

Before deploying:

- Use a learning account.
- Enable MFA.
- Prefer IAM Identity Center or assumed roles.
- Avoid long-lived access keys.
- Configure AWS Budgets.
- Apply cost tags.
- Estimate cost.
- Use Terraform.
- Keep test workloads small.
- Avoid unnecessary always-on services.
- Avoid broad CloudTrail data-event selectors.
- Avoid indefinite CloudWatch log retention.
- Tear down billable resources.
- Verify deletion.
- Check Cost Explorer after labs.

Always verify current AWS pricing and free-tier terms before deploying.

---

# Phase 42 — Current AWS Documentation Rules

## 131. Verify Before Production

AWS changes frequently.

Before using an exact implementation, verify:

```text
service names
metric names
metric dimensions
CLI syntax
API parameters
CloudTrail capabilities
Cost Explorer capabilities
Billing export schema
Terraform resource arguments
pricing
quotas
regional availability
```

Prefer official sources:

- AWS service documentation
- AWS CLI documentation
- AWS SDK/API reference
- AWS Terraform provider documentation
- AWS pricing pages
- AWS Billing and Cost Management documentation

If behavior is version- or Region-dependent, write:

> Verify current AWS documentation for your Region and account before deployment.

---

# Phase 43 — Current AWS Reference Notes

## 132. CloudTrail Evidence Model

AWS currently documents four CloudTrail event categories:

```text
Management
Data
Network activity
Insights
```

For this module, management and data events are the core audit distinction.

Source: AWS CloudTrail "Understanding CloudTrail events."

---

## 133. CloudTrail Trails

CloudTrail trails can deliver events to S3, with optional integration with CloudWatch Logs and EventBridge.

Source: AWS CloudTrail "Working with CloudTrail trails."

---

## 134. CloudTrail + Athena

AWS documents querying CloudTrail logs with Athena. This is a strong fit when the platform already stores audit logs in S3 and needs SQL-based investigation.

Source: Amazon Athena "Query AWS CloudTrail logs."

---

## 135. CloudTrail Lake Availability

AWS currently states that CloudTrail Lake will no longer be open to new customers starting May 31, 2026, while existing customers can continue using it.

This is a critical current-state note. Always verify eligibility and current AWS guidance before designing a new CloudTrail Lake deployment.

Source: AWS CloudTrail "CloudTrail Lake event data stores."

---

## 136. Glue + EventBridge

AWS Glue emits EventBridge job-state events for:

```text
SUCCEEDED
FAILED
TIMEOUT
STOPPED
```

These can be routed to targets such as SNS, SQS, Lambda, and Step Functions.

Source: AWS Glue "Automating AWS Glue with EventBridge."

---

## 137. Cost Allocation

AWS Cost Management supports organizing costs using cost allocation tags and cost categories. Tagging is not a universal answer for every shared AWS charge, so allocation coverage and exceptions must be documented.

Source: AWS Billing and Cost Management documentation.

---

# Phase 44 — Completion Checklist

## 138. CloudWatch

- [ ] Metrics
- [ ] Namespace
- [ ] Metric name
- [ ] Dimensions
- [ ] Statistics
- [ ] Periods
- [ ] Standard vs custom metrics
- [ ] Glue monitoring
- [ ] EMR monitoring
- [ ] Kinesis monitoring
- [ ] `IteratorAgeMilliseconds`
- [ ] Kinesis throttling
- [ ] Firehose monitoring
- [ ] Redshift monitoring
- [ ] Athena monitoring
- [ ] Step Functions monitoring
- [ ] Logs
- [ ] Log groups
- [ ] Log streams
- [ ] Retention
- [ ] Structured logging
- [ ] Correlation IDs
- [ ] Logs Insights
- [ ] Dashboards
- [ ] Alarms
- [ ] Missing-data behavior
- [ ] SNS/notification integration

## EventBridge

- [ ] Events
- [ ] Event source
- [ ] Detail type
- [ ] Event patterns
- [ ] Glue job-state events
- [ ] Rules
- [ ] Targets
- [ ] Retry awareness
- [ ] Dead-letter handling awareness
- [ ] Idempotent remediation

## CloudTrail

- [ ] CloudTrail fundamentals
- [ ] Management events
- [ ] Data events
- [ ] S3 object auditing
- [ ] Trails
- [ ] S3 delivery
- [ ] Encryption
- [ ] Retention
- [ ] Athena querying
- [ ] CloudTrail Lake awareness
- [ ] Organization-wide trails
- [ ] Audit investigations

## Cost

- [ ] Cost Explorer
- [ ] AWS Budgets
- [ ] Cost allocation tags
- [ ] Tag activation
- [ ] Shared-cost allocation
- [ ] Pipeline cost attribution
- [ ] Billing Data Exports
- [ ] Athena cost analytics
- [ ] Unit economics
- [ ] Cost anomaly detection
- [ ] CloudWatch cost control
- [ ] CloudTrail cost control

## Production Operations

- [ ] Dashboard design
- [ ] Alert design
- [ ] Incident investigation
- [ ] Audit runbooks
- [ ] Cost runbooks
- [ ] Security
- [ ] Least privilege
- [ ] Terraform
- [ ] AWS CLI
- [ ] boto3
- [ ] Athena SQL
- [ ] Logs Insights
- [ ] Cost teardown
- [ ] Documentation verification

---

# Phase 45 — Final Operating Standard

## 139. You Are Ready When You Can Do This Without Guessing

Given:

```text
A production AWS data pipeline is delayed.
```

You can:

```text
1. Establish impact.
2. Inspect the dashboard.
3. Identify the failing/degraded signal.
4. Establish a timeline.
5. Query logs.
6. Inspect relevant EventBridge events.
7. Check CloudTrail for changes.
8. Check cost signals when relevant.
9. Form a root-cause hypothesis.
10. Collect evidence.
11. Remediate.
12. Verify recovery.
13. Update the runbook.
14. Decide whether an alarm/dashboard/architecture change is needed.
```

Given:

```text
The AWS bill suddenly increases.
```

You can:

```text
Cost Explorer
→ service
→ account/Region
→ usage
→ tags
→ detailed billing data
→ CloudWatch
→ CloudTrail
→ root cause
→ prevention
```

Given:

```text
Security asks who accessed a sensitive S3 dataset.
```

You can:

```text
audit scope
→ data-event evidence
→ identity
→ action
→ resource
→ time
→ source context
→ query
→ evidence limitations
```

That is production-level observability.

---

# Roadmap Coverage Audit

## 140. Requirement-by-Requirement Audit

| Roadmap Requirement | Covered? | Where |
|---|---:|---|
| CloudWatch metrics | Yes | Sections 2–4 |
| Glue metrics | Yes | Section 5 |
| EMR metrics | Yes | Section 6 |
| Kinesis `IteratorAgeMilliseconds` | Yes | Section 7 |
| Kinesis throttling | Yes | Section 7 |
| Firehose metrics | Yes | Section 8 |
| Redshift metrics | Yes | Section 9 |
| Athena workgroup/workload indicators | Yes | Section 10 |
| Step Functions monitoring | Yes | Section 11 |
| CloudWatch Logs | Yes | Sections 12–14 |
| Log retention | Yes | Section 14 |
| Structured/JSON logs | Yes | Section 13 |
| Correlation IDs/run IDs | Yes | Sections 13, 20 |
| CloudWatch Alarms | Yes | Sections 23–26 |
| Missing-data treatment | Yes | Section 25 |
| Notifications | Yes | Sections 26, 30 |
| Logs Insights | Yes | Sections 15–22 |
| Dashboards | Yes | Sections 27–28, 63 |
| EventBridge job-state events | Yes | Sections 29–31 |
| CloudTrail | Yes | Sections 32–36 |
| Management events | Yes | Section 33 |
| Data events | Yes | Section 34 |
| S3 object access auditing | Yes | Sections 37, 67 |
| CloudTrail → S3 | Yes | Section 35 |
| Athena audit queries | Yes | Sections 37–38 |
| Cost Explorer | Yes | Sections 39–40, 68 |
| AWS Budgets | Yes | Sections 43, 68 |
| Cost allocation tags | Yes | Sections 41–42 |
| Pipeline cost attribution | Yes | Sections 44–45 |
| Billing Data Exports | Yes | Sections 46–48 |
| Athena unit economics | Yes | Sections 47–48, 69 |
| Cost anomaly detection | Yes | Section 49 |
| Log/metric cost control | Yes | Sections 50–51 |
| CloudTrail Lake awareness | Yes | Sections 52–53 |
| Organization-wide trails | Yes | Section 54 |
| Observability hands-on project | Yes | Sections 56–62 |
| CloudWatch dashboard lab | Yes | Section 63 |
| Logs Insights investigation lab | Yes | Sections 64–66 |
| CloudTrail S3 audit lab | Yes | Section 67 |
| Cost attribution lab | Yes | Sections 68–69 |
| Break/Fix scenarios | Yes | Sections 70–77 |
| Production runbooks | Yes | Sections 78–79 |
| AWS CLI | Yes | Sections 80–85 |
| Python/boto3 | Yes | Sections 86–88 |
| Terraform | Yes | Sections 89–92 |
| Security | Yes | Sections 93–95 |
| Cost optimization | Yes | Sections 96–99 |
| Decision matrices | Yes | Sections 100–103 |
| Production architecture patterns | Yes | Sections 104–108 |
| End-to-end incident response | Yes | Section 109 |
| ADR exercises | Yes | Sections 110–114 |
| Practice questions | Yes | Sections 115–117 |
| Interview preparation | Yes | Sections 118–123 |
| Decision-making exercises | Yes | Sections 124–128 |
| Completion checklist | Yes | Section 138 |
| Production operating standard | Yes | Section 139 |
| Final roadmap audit | Yes | Section 140 |

### Coverage Result

**100% of the explicit Topic 12 requirements are covered in this module.**

This percentage refers to the requirements explicitly enumerated in the supplied Topic 12 specification. It does not mean every AWS observability feature is covered; services and capabilities outside the stated scope are intentionally excluded.

---

# Final Quality Check

## 141. Production Quality Gate

- [x] Beginner → fundamentals → intermediate → advanced progression
- [x] AWS Data Engineering context
- [x] Mental models
- [x] Architecture diagrams
- [x] CloudWatch metrics
- [x] CloudWatch logs
- [x] Logs Insights
- [x] CloudWatch alarms
- [x] Dashboards
- [x] EventBridge
- [x] CloudTrail
- [x] Management/data event distinction
- [x] S3 audit
- [x] Athena audit
- [x] Cost Explorer
- [x] Budgets
- [x] Cost allocation
- [x] Billing analytics
- [x] Unit economics
- [x] Cost anomaly awareness
- [x] Cost controls
- [x] CloudTrail Lake awareness
- [x] Organization-wide audit architecture
- [x] CLI examples
- [x] boto3 examples
- [x] Terraform examples
- [x] Athena SQL
- [x] Logs Insights queries
- [x] Hands-on labs
- [x] Break/Fix
- [x] Runbooks
- [x] Security
- [x] Cost safety
- [x] Decision matrices
- [x] ADR exercises
- [x] Interview preparation
- [x] Practice questions
- [x] Completion checklist
- [x] Final roadmap coverage audit
- [x] No fabricated pricing
- [x] No hard-coded claim that billing export schemas are permanent
- [x] Current CloudTrail Lake availability caveat included
- [x] Exact AWS metric/CLI/provider behavior marked for verification where appropriate

---

# 142. Final Principle

A production Data Engineer does not merely build pipelines.

A production Data Engineer can answer:

```text
Is it healthy?
What happened?
Why did it happen?
Who changed it?
Who accessed the data?
How much does it cost?
Is the cost expected?
Can I prove the evidence?
Can I recover safely?
How do I prevent recurrence?
```

The operating model is:

```text
OBSERVE
  ↓
INVESTIGATE
  ↓
AUDIT
  ↓
ATTRIBUTE
  ↓
REMEDIATE
  ↓
VERIFY
  ↓
OPTIMIZE
  ↓
DOCUMENT
```

> **Production Data Engineering = pipeline engineering + observability + auditability + incident response + FinOps.**
