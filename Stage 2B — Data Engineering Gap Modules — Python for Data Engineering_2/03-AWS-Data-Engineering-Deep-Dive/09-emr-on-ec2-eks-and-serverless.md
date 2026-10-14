# EMR on EC2, EKS, and Serverless

> **Module:** Gap Module G3 — AWS Data Engineering Deep Dive  
> **Phase:** D — Streaming, Big Compute, Orchestration, Replication  
> **Topic:** 09 — EMR on EC2, EKS, and Serverless  
> **Learning level:** Beginner → Advanced → Production  
> **Primary outcome:** Choose, deploy, operate, secure, troubleshoot, and cost-control Amazon EMR compute for production Spark workloads.

---

## AWS Cost Warning

> **IMPORTANT AWS COST WARNING**
>
> EMR on EC2, EKS, EC2, EBS, NAT gateways, CloudWatch, S3, and related services can generate real charges.
>
> Before every lab:
>
> 1. Check current AWS pricing for the Region and services you will use.
> 2. Set an AWS Budget and alert.
> 3. Use cost-allocation tags.
> 4. Prefer transient clusters for batch work.
> 5. Configure auto-termination wherever appropriate.
> 6. Set capacity limits where the service supports them.
> 7. Destroy billable resources immediately after the exercise.
> 8. Verify that the resources are actually gone.
>
> **Never use an old price from a tutorial as a current price.** Verify pricing and service limits in the current AWS documentation before deployment.

---

# 1. Why This Topic Matters

Apache Spark gives a distributed processing engine. Amazon EMR gives AWS-specific ways to operate that engine as part of a production data platform.

The important question is therefore not:

> "How do I run Spark on EMR?"

It is:

> **"Which AWS compute operating model should I use for this Spark workload, and why?"**

A production engineer may have several valid choices:

```text
                    Spark workload
                         |
                         v
                 What operating model?
                         |
          +--------------+--------------+
          |              |              |
         Glue       EMR Serverless   EMR on EC2
                                         |
                                      EMR on EKS
```

The choice depends on:

- infrastructure control
- startup sensitivity
- workload duration
- workload variability
- Spark customization
- compute scale
- Kubernetes requirements
- team expertise
- security requirements
- operational burden
- cost target
- need for reusable platform infrastructure

This module therefore treats EMR as a **production compute-platform decision**, not merely as another Spark tutorial.

---

# 2. Where EMR Fits in AWS Data Engineering

A simplified AWS data platform can look like:

```text
Sources
  |
  v
Ingestion
  |
  v
S3 Data Lake
  |
  +-----------------------------+
  |                             |
  v                             v
Glue / Athena              Spark compute
                                |
                    +-----------+-----------+
                    |           |           |
                   Glue      EMR Serverless  EMR
                                            |
                                      +-----+-----+
                                      |           |
                                   EC2          EKS
                    |
                    v
             Iceberg / Delta / Hudi
                    |
                    v
        Glue Data Catalog / Lake Formation
                    |
                    v
        Athena / Redshift / downstream AI
```

The preceding modules established:

- Spark fundamentals
- Spark performance
- S3 and AWS foundations
- Glue
- Athena
- Lake Formation
- Iceberg
- streaming systems

This module connects those capabilities to **large-scale managed Spark compute**.

---

# 3. Prerequisites

The roadmap assumes the learner already understands:

- Python
- AWS CLI basics
- IAM basics
- S3
- Glue Data Catalog
- Apache Spark
- DataFrames
- partitions
- shuffle
- joins
- skew
- broadcast joins
- AQE
- Iceberg fundamentals
- Docker/container fundamentals
- Terraform/OpenTofu basics
- observability
- cost management

## What this module will refresh

Only enough Spark to understand EMR:

- driver
- executors
- stages
- tasks
- partitions
- shuffle
- Spark configuration

This is **not another PySpark course**.

The emphasis is:

```text
Spark
  +
AWS infrastructure
  +
security
  +
operations
  +
cost
  =
production EMR engineering
```

---

# 4. What Amazon EMR Is

Amazon EMR is AWS's managed platform for running open-source big-data frameworks and workloads.

The platform can support workloads involving technologies such as:

- Apache Spark
- Hadoop ecosystem components
- Hive
- Trino/Presto-family engines where supported by the selected EMR release
- lakehouse table formats
- AWS-native data services

The exact application versions and capabilities depend on the selected EMR release, Region, and deployment model.

Always verify the current release documentation before choosing a production release.

## EMR is not the same thing as Spark

Think:

```text
Apache Spark
=
distributed compute engine

Amazon EMR
=
AWS-managed platform for operating supported
big-data workloads, including Spark
```

EMR adds AWS integration and operating models around the compute engine.

---

# 5. Why AWS Glue Is Not Always Enough

AWS Glue and EMR overlap because both can run Spark workloads.

The correct comparison is not:

> Glue = small workloads; EMR = large workloads.

That is too simplistic.

A better comparison is:

| Requirement | Glue | EMR Serverless | EMR on EC2 | EMR on EKS |
|---|---|---|---|---|
| Lowest infrastructure burden | Strong | Strong | Lower | Lower |
| Cluster-level control | Limited | Limited | Strong | Strong through Kubernetes |
| Serverless operation | Yes | Yes | No | No |
| Custom cluster software | Limited | Limited | Strong | Strong |
| Kubernetes platform | No | No | No | Yes |
| Very large Spark workloads | Possible | Possible | Strong fit | Strong fit |
| Long-running/repeated workloads | Possible | Possible | Strong fit | Strong fit |
| Spot infrastructure strategy | Not the main model | Not EC2 Spot management | Strong | Depends on EKS node strategy |
| Operational complexity | Low | Low | Medium/high | High |
| Team Kubernetes expertise | Not required | Not required | Not required | Required |
| Infrastructure customization | Lower | Lower | High | High |
| Startup sensitivity | Good, service-dependent | Good, service-dependent | Cluster startup matters | Pod/image/node startup matters |

The right answer is workload-specific.

### Choose Glue when

- the workload fits Glue's managed ETL model
- minimal infrastructure operations are important
- AWS Glue integrations provide the required behavior
- deep cluster-level customization is unnecessary

### Choose EMR Serverless when

- Spark is required
- workload volume varies
- you want an application/job-run model
- you do not want to manage clusters
- capacity can be bounded with application limits
- warm capacity is valuable for latency-sensitive workloads

### Choose EMR on EC2 when

- cluster-level control matters
- custom software/configuration is required
- large or long-running Spark workloads justify infrastructure ownership
- instance selection and Spot strategies matter
- you need deeper control over the compute fleet

### Choose EMR on EKS when

- the organization already operates EKS well
- Kubernetes is a strategic platform
- multiple workloads need a shared Kubernetes operating model
- Spark workloads benefit from Kubernetes scheduling and platform capabilities
- the team accepts the additional Kubernetes operational complexity

---

# 6. EMR Architecture

The core mental model:

```text
                         Amazon EMR
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          EMR on EC2     EMR Serverless   EMR on EKS
              |               |               |
          EC2 cluster      AWS-managed       EKS
          node groups       capacity       Kubernetes
```

## What changes between models?

The Spark application can remain conceptually similar, but the operating layer changes.

```text
Spark code
   |
   v
EMR runtime
   |
   +----------------------+
   |                      |
Compute model          Control model
   |                      |
EC2 / Serverless / EKS   IAM / networking / scaling
```

---

# 7. What EMR Manages vs What You Manage

The answer depends on the deployment model.

| Concern | EMR on EC2 | EMR Serverless | EMR on EKS |
|---|---|---|---|
| Spark runtime integration | AWS | AWS | AWS |
| EC2 cluster lifecycle | Customer-controlled | AWS | EKS/platform |
| Kubernetes cluster | Not required | Not required | Customer/EKS platform |
| Spark application | Customer | Customer | Customer |
| Data | Customer | Customer | Customer |
| IAM | Customer | Customer | Customer |
| Network design | Customer | Customer configuration | Customer/EKS |
| Capacity model | EC2 fleet | Application capacity | Kubernetes resources/nodes |
| Scaling | Managed scaling/manual strategies | Service-managed | Kubernetes/service mechanisms |
| Cost control | Customer | Customer via limits/workload design | Customer/platform |
| Observability | Customer + AWS tools | Customer + AWS tools | Customer + AWS tools |
| Security posture | Customer | Customer | Customer |

The more infrastructure control you choose, the more operational responsibility you accept.

---

# 8. EMR Deployment Models

## 8.1 EMR on EC2

Mental model:

```text
EMR
 |
 +-- EC2 instances
      |
      +-- Primary
      +-- Core
      +-- Task
```

You control:

- cluster lifecycle
- instance types
- node groups
- capacity strategy
- networking
- bootstrap actions
- selected runtime configuration
- Spot/On-Demand strategy

This is the model with the greatest direct infrastructure control in this comparison.

## 8.2 EMR Serverless

Mental model:

```text
EMR Serverless Application
       |
       +-- Job Run 1
       +-- Job Run 2
       +-- Job Run 3
```

You create an application and submit job runs.

The service manages the underlying compute lifecycle.

The important distinction is:

```text
Application
=
configuration and capacity boundary

Job Run
=
one submitted unit of work
```

An application can have many job runs.

EMR Serverless supports automatic capacity behavior, application-level maximum capacity, and optional pre-initialized capacity. Current AWS documentation also describes automatic application start on job submission and automatic stop after an idle period by default; verify current defaults before relying on them operationally. citeturn0search1turn0search5

## 8.3 EMR on EKS

Mental model:

```text
EKS cluster
    |
    +-- Kubernetes namespace
             |
             +-- EMR virtual cluster
                      |
                      +-- Spark job
                              |
                       +------+------+
                       |             |
                    driver pod   executor pods
```

A virtual cluster is an EMR registration of an EKS namespace. Multiple virtual clusters can be backed by the same physical EKS cluster, while each virtual cluster maps to one Kubernetes namespace. The virtual-cluster object itself does not create active compute resources. citeturn0search7turn0search10

---

# 9. EMR on EC2 — Deep Dive

## 9.1 Cluster Mental Model

```text
EMR Cluster
 |
 +-- Primary node
 |
 +-- Core nodes
 |
 +-- Task nodes
```

### Primary node

The primary node provides cluster coordination responsibilities and hosts important cluster services.

Spark driver placement depends on workload and deployment configuration. Do not assume every Spark architecture has identical driver placement.

### Core nodes

Core nodes provide compute and, for Hadoop/HDFS-oriented workloads, distributed storage responsibilities.

When using S3 as the durable data lake, do not automatically assume HDFS is your source-of-truth storage layer.

### Task nodes

Task nodes are primarily compute capacity.

They are often a natural place to use Spot capacity because losing a task worker is generally easier to recover from than losing a critical coordination or persistent-storage role.

This is a pattern, not an absolute rule.

---

# 10. Primary, Core, and Task Nodes

| Node | Primary role | Compute | HDFS storage role | Spot suitability |
|---|---|---:|---:|---|
| Primary | Coordination/services | Yes | Not the main purpose | Usually conservative |
| Core | Compute + HDFS role | Yes | Yes, where HDFS is used | Requires care |
| Task | Additional compute | Yes | No | Often suitable |

### Production principle

If your architecture is:

```text
S3 = durable data
EMR = compute
```

you can often make task capacity more interruptible because the durable source and target data remain in S3.

Do not translate that into:

> "Always make everything Spot."

The correct strategy depends on:

- failure tolerance
- retry behavior
- workload criticality
- capacity availability
- cluster role
- startup time
- recovery behavior

---

# 11. EMR Steps

An EMR Step represents a unit of work submitted to an EMR cluster.

A typical batch flow:

```text
Create cluster
     |
     v
Add Step
     |
     v
Spark job
     |
     v
Observe status
     |
     +---- success ---> next step
     |
     +---- failure ---> diagnose/retry/terminate
```

Typical operations include:

```bash
aws emr list-clusters \
  --active

aws emr list-steps \
  --cluster-id "$CLUSTER_ID"

aws emr describe-step \
  --cluster-id "$CLUSTER_ID" \
  --step-id "$STEP_ID"
```

Check the current AWS CLI reference for exact options and output fields before using commands in automation.

## boto3 pattern

```python
import boto3

emr = boto3.client("emr", region_name="us-east-1")

response = emr.add_job_flow_steps(
    JobFlowId=cluster_id,
    Steps=[
        {
            "Name": "orders-transform",
            "ActionOnFailure": "CONTINUE",
            "HadoopJarStep": {
                "Jar": "command-runner.jar",
                "Args": [
                    "spark-submit",
                    "s3://example-bucket/jobs/orders.py",
                    "--input",
                    "s3://example-bucket/raw/orders/",
                    "--output",
                    "s3://example-bucket/gold/orders/",
                ],
            },
        }
    ],
)

print(response["StepIds"])
```

### Production considerations

- Use IAM roles rather than embedded credentials.
- Make output writes idempotent.
- Record a job identifier and input watermark.
- Store logs centrally.
- Avoid `CONTINUE` when downstream correctness depends on success.
- Decide failure behavior intentionally.

---

# 12. Transient vs Long-Running Clusters

## 12.1 Transient cluster

```text
Create
  |
Run
  |
Observe
  |
Persist results to S3
  |
Terminate
```

This is often attractive for batch workloads because the infrastructure lifetime closely follows the workload.

### Advantages

- reduced idle cost
- clear lifecycle
- reproducible environment
- easier cost attribution
- simpler teardown

### Risks

- startup latency
- repeated cluster provisioning
- dependency/bootstrap startup
- capacity availability

## 12.2 Long-running cluster

```text
Cluster starts
     |
     +-- Job A
     +-- Job B
     +-- Job C
     +-- Job D
     |
Cluster remains active
```

Advantages:

- reduced repeated startup overhead
- potentially higher utilization
- useful for sustained workloads

Risks:

- idle cost
- patching
- configuration drift
- noisy-neighbor effects
- scaling complexity
- long-lived failure modes

### Decision rule

If the workload is naturally batch-oriented and can tolerate startup time:

> Prefer transient compute unless sustained utilization makes a persistent platform economically or operationally justified.

---

# 13. Creating an EMR on EC2 Cluster

A production deployment should normally be automated with infrastructure as code.

The conceptual lifecycle is:

```text
IAM
  |
VPC / subnets / security groups
  |
EMR release
  |
Node groups
  |
Cluster configuration
  |
Logging
  |
Scaling
  |
Steps
```

## CLI learning pattern

For learning, the AWS CLI can be used to create and inspect clusters.

A representative command shape is:

```bash
aws emr create-cluster \
  --name "de-emr-lab" \
  --release-label "<CURRENT_SUPPORTED_EMR_RELEASE>" \
  --applications Name=Spark \
  --ec2-attributes \
    SubnetId="$SUBNET_ID" \
    InstanceProfile="EMR_EC2_DefaultRole" \
  --service-role "$EMR_SERVICE_ROLE_ARN" \
  --instance-groups '[
    {
      "InstanceGroupType": "MASTER",
      "InstanceCount": 1,
      "InstanceType": "<INSTANCE_TYPE>"
    },
    {
      "InstanceGroupType": "CORE",
      "InstanceCount": 2,
      "InstanceType": "<INSTANCE_TYPE>"
    }
  ]'
```

**Do not copy the placeholder roles or instance type blindly.** Use roles and policies designed for your account and current AWS documentation.

For production:

> Terraform/OpenTofu should be the repeatable source of infrastructure truth, while CLI is valuable for learning and operations.

---

# 14. EMR on EC2 Hands-On Lab

## Lab: Transient Spark Platform

### Goal

Run a realistic Spark workload using:

```text
S3 raw orders
      |
      v
Transient EMR EC2
      |
      v
Spark transformation
      |
      v
S3/Iceberg gold data
```

### Tasks

1. Create an AWS Budget.
2. Tag resources with:
   - `Project`
   - `Environment`
   - `Owner`
   - `CostCenter`
3. Create or select a private subnet.
4. Configure IAM roles.
5. Create a transient cluster.
6. Configure primary/core/task capacity.
7. Use Spot only where the workload can tolerate interruption.
8. Submit a PySpark job.
9. Read `orders` from S3.
10. Transform the data.
11. Write output to S3/Iceberg.
12. Inspect step status.
13. Inspect logs.
14. Open the Spark UI.
15. Record runtime.
16. Estimate cost.
17. Terminate the cluster.
18. Verify that no unnecessary billable resource remains.

### Evidence to save in your learning notes

```text
Cluster ID:
EMR release:
Region:
Instance strategy:
Input:
Output:
Runtime:
Peak capacity:
Observed bottleneck:
Cost estimate:
Failure encountered:
Fix:
Teardown verified:
```

---

# 15. EMR Serverless — Deep Dive

EMR Serverless separates your application definition from individual job runs.

```text
EMR Serverless Application
          |
    +-----+-----+
    |     |     |
  Run 1 Run 2 Run 3
```

## Application

The application establishes things such as:

- runtime family
- application type
- default configuration
- capacity limits
- optional pre-initialized capacity
- networking configuration
- tags
- monitoring-related settings

## Job run

A job run is an individual execution.

The distinction matters operationally:

```text
Application lifecycle
       !=
Job lifecycle
```

A single application can be used by multiple jobs, subject to the workload and isolation requirements of the platform.

---

# 16. EMR Serverless Job Runs

A production job submission should specify:

- application ID
- job name
- execution role
- entry point
- arguments
- Spark configuration
- monitoring configuration
- output location

Representative CLI pattern:

```bash
aws emr-serverless start-job-run \
  --application-id "$APPLICATION_ID" \
  --execution-role-arn "$JOB_EXECUTION_ROLE_ARN" \
  --job-driver '{
    "sparkSubmit": {
      "entryPoint": "s3://example-bucket/jobs/orders.py",
      "entryPointArguments": [
        "--input",
        "s3://example-bucket/raw/orders/",
        "--output",
        "s3://example-bucket/gold/orders/"
      ]
    }
  }'
```

Verify current API syntax and supported job-driver fields before production use.

## boto3 pattern

```python
import boto3

client = boto3.client("emr-serverless", region_name="us-east-1")

response = client.start_job_run(
    applicationId=application_id,
    executionRoleArn=execution_role_arn,
    jobDriver={
        "sparkSubmit": {
            "entryPoint": "s3://example-bucket/jobs/orders.py",
            "entryPointArguments": [
                "--input", "s3://example-bucket/raw/orders/",
                "--output", "s3://example-bucket/gold/orders/",
            ],
        }
    },
)

print(response["jobRunId"])
```

---

# 17. EMR Serverless Scaling and Capacity

This is a major production topic.

## Automatic scaling

EMR Serverless can add and release workers based on workload demand.

The exact behavior depends on the application type, runtime, job requirements, and configuration.

## Maximum capacity

A maximum capacity is a **guardrail**.

Conceptually:

```text
Job demand
    |
    v
Auto scaling
    |
    v
Maximum capacity
    |
    +---- allowed
    |
    +---- bounded
```

Current AWS API documentation describes maximum capacity in terms of cumulative CPU, memory, and disk limits; once a defined limit is reached, new resources are not created beyond it. citeturn0search2

A maximum capacity does **not** guarantee:

- optimal runtime
- correct Spark configuration
- lowest cost
- no failures
- sufficient capacity for every workload

It is a safety boundary, not a performance strategy.

## Pre-initialized capacity

Pre-initialized capacity keeps driver/executor workers warm.

Benefits:

- lower startup latency
- useful for iterative workloads
- useful for time-sensitive jobs

Cost implication:

> You pay for provisioned pre-initialized workers while they are maintained, even when they are idle.

AWS recommends sizing this capacity for useful utilization and using auto-stop behavior appropriately. citeturn0search0

## Capacity decision

```text
Need fast repeated startup?
       |
      Yes
       |
Use pre-initialized capacity
       |
Measure utilization
       |
Right-size
```

Do not enable warm capacity automatically for every batch workload.

---

# 18. EMR Serverless Hands-On Lab

## Lab: S3 → Iceberg → EMR Serverless → Athena

Architecture:

```text
S3 raw
  |
  v
Glue Catalog
  |
  v
Iceberg source
  |
  v
EMR Serverless
  |
  v
Spark transformation
  |
  v
Gold Iceberg
  |
  v
Athena
```

### Tasks

1. Create an EMR Serverless Spark application.
2. Configure a maximum capacity appropriate for the lab.
3. Configure an execution role with least privilege.
4. Submit a Spark job.
5. Pass input/output parameters.
6. Read an Iceberg table.
7. Transform the data.
8. Write a Gold Iceberg table.
9. Inspect job state.
10. Inspect logs.
11. Query the output with Athena.
12. Record runtime and capacity behavior.
13. Delete or stop the application as appropriate.
14. Verify teardown.

### Experiment

Run the same workload twice:

```text
Run A: no useful warm capacity
Run B: pre-initialized capacity
```

Record:

| Metric | Run A | Run B |
|---|---:|---:|
| Startup latency | | |
| Total runtime | | |
| Capacity used | | |
| Estimated cost | | |
| Operational complexity | | |

Then decide whether warm capacity is justified.

---

# 19. EMR on EKS — Deep Dive

EMR on EKS combines:

```text
Amazon EMR runtime
        +
Amazon EKS
        +
Kubernetes scheduling
```

The basic flow is:

```text
EKS cluster
    |
Kubernetes namespace
    |
EMR virtual cluster
    |
StartJobRun
    |
Spark driver pod
    |
Spark executor pods
```

AWS documentation describes a virtual cluster as an EMR registration against an EKS namespace. When a Spark job is submitted, EMR on EKS requests the Kubernetes scheduler to schedule pods. citeturn0search3turn0search10

## Why choose it?

Potential reasons:

- existing EKS platform
- Kubernetes-based organizational standard
- shared cluster platform
- standardized container tooling
- Kubernetes scheduling and policy ecosystem
- multiple workloads sharing a Kubernetes platform

## Why not choose it?

Because Kubernetes introduces real operational complexity:

- EKS lifecycle
- node groups
- IAM for workloads
- Kubernetes RBAC
- namespaces
- pod scheduling
- resource requests/limits
- image management
- networking
- cluster upgrades
- observability
- platform engineering

Therefore:

> **Kubernetes should be a requirement-driven decision, not a prestige choice.**

---

# 20. Virtual Clusters

A virtual cluster:

```text
Physical EKS cluster
       |
       +-- Namespace A
       |      |
       |    EMR virtual cluster A
       |
       +-- Namespace B
              |
            EMR virtual cluster B
```

This allows an organization to map EMR workloads to Kubernetes namespaces.

Important point:

> A virtual cluster is not an additional EC2 cluster.

AWS documentation states that virtual clusters do not create active resources that independently contribute to billing or require a separate infrastructure lifecycle. citeturn0search7

---

# 21. Spark on Kubernetes with EMR on EKS

A Spark job can be represented as:

```text
Spark application
       |
       v
EMR runtime image
       |
       +---- driver pod
       |
       +---- executor pods
```

The job's resources are scheduled by Kubernetes.

A job run can be submitted using AWS CLI/SDK mechanisms; current EMR on EKS also supports mechanisms such as `spark-submit` for supported releases. citeturn0search8turn0search15

Representative command shape:

```bash
aws emr-containers start-job-run \
  --virtual-cluster-id "$VIRTUAL_CLUSTER_ID" \
  --name "orders-spark-job" \
  --execution-role-arn "$EXECUTION_ROLE_ARN" \
  --release-label "<CURRENT_SUPPORTED_RELEASE>" \
  --job-driver '{
    "sparkSubmitJobDriver": {
      "entryPoint": "s3://example-bucket/jobs/orders.py",
      "sparkSubmitParameters": "--conf spark.executor.cores=2 --conf spark.executor.memory=4G"
    }
  }'
```

Verify current release labels and request schema against the AWS API documentation.

---

# 22. EMR on EC2 vs EMR on EKS

| Dimension | EMR on EC2 | EMR on EKS |
|---|---|---|
| Compute substrate | EC2 cluster | EKS |
| Cluster model | EMR cluster | Kubernetes cluster + namespace |
| Infrastructure control | High | High, but Kubernetes-mediated |
| Kubernetes expertise | Not required | Required |
| Multi-tenancy | EMR cluster patterns | Kubernetes namespace/platform patterns |
| Shared platform | Possible | Strong fit |
| Custom images | Supported mechanisms vary by model/release | Container-oriented |
| Operations | EMR-focused | EMR + Kubernetes |
| Scaling | EMR/EC2 mechanisms | Kubernetes/EKS mechanisms |
| Failure surface | EC2 + EMR + Spark | EKS + Kubernetes + EMR + Spark |
| Best fit | Dedicated/custom Spark platform | Existing Kubernetes data platform |

### EKS is justified when

1. Kubernetes is already a mature platform.
2. The organization has strong Kubernetes operations.
3. Multiple workloads benefit from a shared Kubernetes platform.
4. Platform-level scheduling, isolation, and container workflows are strategic requirements.

### EKS is not justified merely because

- Kubernetes is fashionable
- "containers are modern"
- the team wants every workload on Kubernetes

---

# 23. EMR Configuration

Configuration has a causal chain:

```text
Spark / EMR configuration
          |
          v
Resource behavior
          |
          v
Performance
          |
          v
Cost
```

Important categories include:

- executor memory
- executor cores
- driver memory
- driver cores
- shuffle behavior
- serialization
- dynamic allocation awareness
- logging
- adaptive query execution
- partition sizing

Do not tune blindly.

The process should be:

```text
Measure
  |
Identify bottleneck
  |
Change one meaningful variable
  |
Rerun
  |
Compare
```

---

# 24. Spark Configuration on EMR

Example:

```text
spark.executor.memory
spark.executor.cores
spark.driver.memory
spark.driver.cores
spark.sql.shuffle.partitions
spark.sql.adaptive.enabled
```

The exact defaults and recommended values depend on the EMR release, Spark version, workload, and instance configuration.

## Anti-pattern

```text
Job slow
  ↓
Add more executors
  ↓
Still slow
  ↓
Add more executors
```

The correct diagnostic chain is:

```text
Job slow
  |
  +-- CPU bound?
  +-- memory pressure?
  +-- GC?
  +-- shuffle?
  +-- skew?
  +-- S3 I/O?
  +-- bad partition sizing?
  +-- inefficient query plan?
```

Then choose a change.

---

# 25. Bootstrap Actions

Bootstrap actions are scripts used to install additional software or customize cluster instances during EMR cluster startup.

AWS documents that bootstrap actions run after an instance launches and before the EMR applications begin processing data. They can also run on nodes added to a running cluster. citeturn0search16

Typical uses:

- OS-level packages
- cluster configuration
- custom initialization
- installing dependencies

## Bootstrap action risks

A bootstrap script can become a hidden deployment system.

Common failures:

- not idempotent
- external dependency unavailable
- version drift
- shell failure not handled
- startup becomes slow
- package installation breaks a runtime
- undocumented assumptions

### Better practice

For repeatable production environments:

```text
Bootstrap
    |
    v
small, deterministic initialization
```

not:

```text
Bootstrap
    |
    +-- 900 lines
    +-- downloads latest package
    +-- modifies many system files
    +-- depends on internet
```

---

# 26. Custom Images

Custom images can improve reproducibility by packaging dependencies ahead of runtime.

Compare:

| Approach | Strength | Risk |
|---|---|---|
| Bootstrap | Fast to prototype | Drift and startup dependency |
| Custom image | Reproducible baseline | Image build/security lifecycle |
| Job-level dependency | Flexible | Distribution/runtime mismatch |
| Container-based dependency model | Strong reproducibility | More platform complexity |

Use custom images when:

- dependencies are stable
- startup installation is expensive
- reproducibility matters
- security scanning is part of the delivery process
- multiple jobs share the same runtime baseline

Verify exact custom-image capabilities for the selected EMR deployment model and release before implementation.

---

# 27. Python Dependency Packaging

Distributed Spark means:

```text
Driver environment
        !=
Executor environment
```

A package installed only on the driver is not necessarily available to executors.

Possible approaches include:

- Python wheels
- dependency archives
- `--py-files`
- S3-hosted artifacts
- supported virtual-environment approaches
- custom images where appropriate

Example:

```bash
spark-submit \
  --py-files s3://example-bucket/libs/company_data_utils-1.2.0-py3-none-any.whl \
  s3://example-bucket/jobs/orders.py
```

## Common production failures

### Missing executor dependency

```text
Driver starts
   |
   v
Executor starts
   |
   v
ImportError
```

### Python version mismatch

```text
Driver: Python X
Executor: Python Y
```

### Native binary mismatch

Examples:

- incompatible `numpy`
- incompatible compiled library
- platform-specific wheel

### Package too large

Large dependency distributions can increase startup and transfer overhead.

## Production rule

Build and test the exact artifact that will run in production.

---

# 28. Lakehouse Integration

EMR commonly participates in:

```text
                    Spark / EMR
                        |
          +-------------+-------------+
          |             |             |
       Iceberg        Delta          Hudi
          |             |             |
          +-------------+-------------+
                        |
                        v
                       S3
                        |
                        v
                Glue Data Catalog
                        |
              +---------+---------+
              |                   |
           Athena              Redshift
```

The exact integration model depends on:

- EMR release
- table format version
- catalog
- Spark configuration
- libraries/connectors
- Lake Formation configuration

Do not assume all three table formats behave identically.

---

# 29. Glue Data Catalog Integration

The Glue Data Catalog provides metadata used by AWS analytics services.

A useful mental model:

```text
S3
 |
 | physical data
 v
Iceberg/Delta/Hudi files
 |
 v
Glue Data Catalog
 |
 | metadata/catalog
 v
EMR / Athena / Redshift / other consumers
```

The catalog does not turn S3 into a database.

It provides metadata such as:

- table identity
- schema
- location
- partition/table metadata
- format information

The physical data remains in the underlying storage system.

---

# 30. Iceberg Integration

Iceberg is particularly important in this roadmap.

Conceptual model:

```text
Iceberg table
   |
   +-- metadata
   +-- snapshots
   +-- manifests
   +-- data files
   |
   v
S3
```

Spark reads and writes the table using an Iceberg-aware catalog.

A conceptual PySpark read:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("orders-read")
    .getOrCreate()
)

df = spark.table("analytics.orders_iceberg")

df.select(
    "order_id",
    "customer_id",
    "order_ts",
    "amount",
).show()
```

Write pattern:

```python
(
    transformed_df.writeTo("analytics.orders_gold")
    .using("iceberg")
    .append()
)
```

The exact catalog and Spark configuration must be supplied for the selected EMR release.

## Production concerns

- snapshot lifecycle
- small files
- partition evolution
- schema evolution
- concurrent writes
- maintenance
- catalog permissions
- Lake Formation controls
- Athena interoperability

---

# 31. Delta and Hudi Awareness

This module does not teach complete Delta Lake or Apache Hudi courses.

Know:

| Capability | Iceberg | Delta | Hudi |
|---|---|---|---|
| Transactional table format | Yes | Yes | Yes |
| Spark integration | Strong | Strong | Strong |
| Metadata/catalog choices | Multiple | Multiple | Multiple |
| CDC-oriented patterns | Strong | Strong | Strong |
| AWS ecosystem fit | Strong | Depends on deployment | Strong |
| Exact behavior | Version/config dependent | Version/config dependent | Version/config dependent |

The engineering question is not:

> "Which table format is universally best?"

It is:

> "Which table format matches the organization's engines, governance model, operational practices, and interoperability requirements?"

---

# 32. Lake Formation Integration

The architecture:

```text
EMR
 |
 v
Glue Data Catalog
 |
 v
Lake Formation
 |
 v
Governed S3 data
```

Lake Formation can provide fine-grained governance over Data Catalog resources.

Current AWS documentation states that EMR can integrate with Lake Formation using runtime roles and the Glue Data Catalog; current EMR releases support governed access patterns for Spark and other supported engines. AWS documents fine-grained table/row/column/cell permissions for applicable EMR configurations, with release-specific prerequisites. citeturn0search6turn0search9

Do not collapse IAM and Lake Formation into one system.

Think:

```text
IAM
=
who can call AWS APIs

Lake Formation
=
who can access governed catalog/data resources
```

The actual authorization path can involve both.

## Runtime roles

A production EMR job should use an appropriately scoped execution/runtime role rather than a broad instance role containing every data permission.

Current AWS documentation describes runtime-role-based access for Lake Formation-enabled EMR configurations. citeturn0search6

---

# 33. Logs and Spark UI

A Data Engineer should investigate evidence, not guess.

Typical evidence sources:

- EMR console
- step status
- cluster logs
- S3 log archive
- CloudWatch where configured
- Spark UI
- Spark event logs
- Kubernetes logs for EMR on EKS
- CloudTrail for API/IAM investigation where appropriate

## Diagnostic model

```text
Job slow
   |
   v
Is the cluster/platform healthy?
   |
   v
Which Spark stage is slow?
   |
   +-- CPU?
   +-- memory?
   +-- shuffle?
   +-- skew?
   +-- I/O?
   +-- serialization?
   |
   v
Root cause
   |
   v
Fix
   |
   v
Measure again
```

---

# 34. Deliberately Skewed Spark Job

Create data where:

```text
customer_id = "UNKNOWN"
```

appears in a very large percentage of rows.

Then run a join.

Expected symptom:

```text
Most tasks complete
       |
       v
One/few tasks run much longer
       |
       v
Stage completion stalls
```

## Investigation

1. Open Spark UI.
2. Identify the slow stage.
3. Inspect task duration distribution.
4. Inspect partition size.
5. Identify the skewed key.
6. Explain why the partition became disproportionately large.
7. Apply an appropriate mitigation.
8. Rerun.
9. Compare before/after.

Possible mitigations:

- salting
- broadcast when the other side is genuinely small
- AQE skew handling where applicable
- better partitioning
- data model correction

This applies the Spark concepts from Module 2.14 rather than reteaching them.

---

# 35. Cost Optimization

A useful conceptual model is:

```text
EMR platform cost
=
compute
+
storage
+
network
+
supporting services
+
idle time
```

The actual bill depends on the deployment model and AWS services used.

## Major levers

### 1. Transient clusters

```text
Create → compute → terminate
```

### 2. Auto-termination

Avoid paying for idle infrastructure.

### 3. Right-sizing

Use evidence from:

- CPU
- memory
- executor utilization
- shuffle
- spill
- runtime

### 4. Spot

Use interruption-tolerant capacity strategically.

### 5. Instance fleets

Diversify capacity choices where supported.

### 6. Managed scaling

Scale with workload rather than keeping a permanently oversized cluster.

### 7. Efficient Spark

A poorly optimized Spark job can dominate infrastructure cost.

### 8. S3-oriented architecture

Use durable S3 storage rather than retaining unnecessary local cluster state.

### 9. Log lifecycle

Logs also have storage and observability costs.

---

# 36. Spot Instances

Spot is an interruption-prone capacity strategy.

A common pattern:

```text
Primary
  |
On-Demand

Core
  |
Conservative capacity strategy

Task
  |
Spot
```

Why task nodes?

Because they are generally compute-only capacity and are easier to replace when a task can be retried.

But the decision depends on:

- workload fault tolerance
- task retry behavior
- shuffle sensitivity
- capacity availability
- SLA
- recovery design

## Spot is inappropriate when

- interruption risk violates the workload SLA
- the workload has poor retry behavior
- the node carries critical state that is not safely reconstructible
- the capacity strategy cannot meet required availability

---

# 37. Instance Fleets

An instance fleet allows capacity to be expressed across multiple EC2 instance choices, improving flexibility when one instance type is constrained.

Benefits can include:

- instance diversification
- improved capacity availability
- Spot diversification
- On-Demand fallback strategies

Conceptual example:

```text
Task fleet
 |
 +-- Instance type A
 +-- Instance type B
 +-- Instance type C
 |
 +-- Spot
 +-- On-Demand fallback
```

Do not treat every available instance type as interchangeable.

Consider:

- CPU
- memory
- network
- EBS
- architecture
- Spark executor fit
- workload profile

---

# 38. Managed Scaling

Scaling is not simply:

> "Add more machines."

A useful control loop is:

```text
Workload demand
     |
     v
Metrics/signals
     |
     v
Scale decision
     |
     v
Capacity change
     |
     v
Observe
```

## Failure modes

### Scaling too aggressively

- cost spikes
- unnecessary capacity
- scheduling overhead

### Scaling too slowly

- long queue times
- poor SLA
- underutilization

### Wrong node type

More nodes do not solve a memory-bound workload if each node has insufficient memory.

### Startup latency

Scaling that adds capacity too slowly may not help a short workload.

---

# 39. Auto-Termination

One of the simplest cost controls is:

```text
Job finishes
     |
     v
Cluster becomes idle
     |
     v
Auto-termination
     |
     v
No ongoing compute charge from the cluster
```

Use a termination strategy that matches:

- expected follow-up jobs
- startup latency
- cluster reuse
- SLA
- cost target

For batch pipelines, automatic termination is often preferable to relying on a human to remember.

---

# 40. Security

Production EMR security should cover:

- IAM
- execution/runtime roles
- least privilege
- S3 permissions
- Glue Catalog permissions
- Lake Formation
- KMS
- encryption at rest
- encryption in transit
- private subnets
- VPC endpoints where appropriate
- security groups
- logging
- audit trails

## Never

```text
spark code
  |
  +-- AWS_ACCESS_KEY_ID=...
  +-- AWS_SECRET_ACCESS_KEY=...
```

Prefer IAM roles and the AWS credential provider chain.

---

# 41. Private Subnets and Networking

A production pattern can be:

```text
                    Public Internet
                         X
                         |
                    Controlled VPC
                         |
                 +-------+-------+
                 |               |
          Private Subnet A   Private Subnet B
                 |               |
               EMR             EKS/EMR
                 |               |
                 +-------+-------+
                         |
                  VPC endpoints /
                  controlled egress
                         |
                         v
                         S3
```

Exact endpoint and egress requirements depend on:

- deployment model
- AWS services used
- subnet routing
- NAT strategy
- private connectivity design
- EMR release

Do not copy a generic endpoint list into production without validating it against the current AWS networking and EMR documentation.

---

# 42. Execution Roles and IAM

Separate roles by responsibility.

Conceptually:

```text
Human / CI role
      |
      v
Create infrastructure

EMR service role
      |
      v
EMR service operations

EC2 instance profile
      |
      v
Cluster infrastructure access

Job/runtime role
      |
      v
Actual data access
```

The exact role model differs by deployment model and feature.

## Least privilege checklist

- S3 prefixes limited to required paths
- Glue databases/tables limited to required resources
- KMS permissions limited to required keys
- Lake Formation grants explicit
- CloudWatch permissions limited
- no wildcard administrative access unless justified

---

# 43. Encryption

Use encryption at:

### Rest

- S3 SSE-KMS where required
- EBS encryption
- supported EMR encryption configuration
- log destinations

### Transit

- TLS
- encrypted service connections
- secure database connections
- secure Kafka connections where applicable

## Key management

Document:

- key ownership
- key policy
- service principals
- runtime-role permissions
- rotation expectations
- operational recovery

---

# 44. Production Architecture Patterns

## Architecture 1 — Serverless Batch

```text
S3
 |
 v
Glue Catalog
 |
 v
EMR Serverless
 |
 v
Iceberg
 |
 v
Athena
```

Use when:

- infrastructure operations should be low
- workload is variable
- Spark is required
- application-level capacity guardrails are sufficient

## Architecture 2 — Cost-Optimized Large Spark

```text
S3
 |
 v
Transient EMR EC2
 |
 +-- On-Demand primary
 +-- On-Demand/core strategy
 +-- Spot task capacity
 |
 v
Iceberg
```

Use when:

- cluster-level control matters
- workload is large
- cost optimization is important
- infrastructure operations are acceptable

## Architecture 3 — Kubernetes Data Platform

```text
EKS
 |
 v
EMR on EKS
 |
 v
Spark
 |
 v
S3 / Iceberg
```

Use when:

- EKS is already a mature platform
- Kubernetes operations are strategic

## Architecture 4 — Orchestrated Platform

```text
EventBridge / Step Functions / MWAA
              |
              v
          EMR job
              |
              v
          Spark ETL
              |
              v
       Glue Catalog
              |
              v
           Iceberg
              |
              v
            Athena
```

Orchestration is Topic 10; here we only establish the integration boundary.

---

# 45. Glue vs EMR Serverless vs EMR on EC2 vs EMR on EKS

## Final decision matrix

| Requirement | Glue | EMR Serverless | EMR on EC2 | EMR on EKS |
|---|---|---|---|---|
| Lowest operational burden | Strong | Strong | Lower | Lowest |
| Infrastructure control | Lower | Lower | Strong | Strong |
| Customization | Moderate | Moderate | Strong | Strong |
| Variable workloads | Strong | Strong | Good | Good |
| Very large Spark | Good | Good | Strong | Strong |
| Kubernetes platform | No | No | No | Strong |
| Fast startup | Good | Good | Cluster-dependent | Cluster/image/node-dependent |
| Long-running workloads | Possible | Possible | Strong | Strong |
| Spot strategy | Not direct EC2 control | Service-managed | Strong | EKS node strategy |
| Multi-team shared platform | Good | Good | Cluster design required | Strong |
| Kubernetes expertise required | No | No | No | Yes |
| Cost optimization at scale | Strong | Strong | Strong with tuning | Strong but complex |
| Cluster-level customization | Lower | Lower | Highest | High |

The matrix intentionally avoids "winner" labels.

The best service is the one that meets the requirements with the lowest acceptable total cost of ownership.

---

# 46. Decision-Making Framework

Use:

```text
Requirements
    |
    v
Data volume
    |
    v
Runtime
    |
    v
Latency/startup sensitivity
    |
    v
Customization
    |
    v
Cost target
    |
    v
Security requirements
    |
    v
Operational tolerance
    |
    v
Team skills
    |
    v
Platform decision
```

## Scenario 1 — Nightly four-hour Spark workload

Requirements:

- predictable
- large
- four-hour runtime
- batch
- no Kubernetes platform

Candidate:

- Glue
- EMR Serverless
- EMR EC2

Likely evaluation:

> Compare EMR Serverless and transient EMR EC2 using measured runtime, operational effort, and cost.

Do not choose solely from theoretical pricing.

## Scenario 2 — Unpredictable daily volume

Likely candidates:

- Glue
- EMR Serverless

Serverless capacity elasticity becomes attractive.

## Scenario 3 — Existing mature EKS platform

Evaluate:

> EMR on EKS

because Kubernetes platform investment already exists.

## Scenario 4 — Deep infrastructure customization

Evaluate:

> EMR on EC2

because cluster and instance-level control may justify the additional operational burden.

## Scenario 5 — Minimal infrastructure operations

Evaluate:

> Glue or EMR Serverless

depending on the Spark/runtime requirements.

---

# 47. Architecture Decision Records

## ADR 1 — EMR Serverless Instead of Glue

### Context

Spark workload has variable volume and the team does not want cluster operations.

### Decision

Use EMR Serverless.

### Alternatives

- Glue
- EMR EC2

### Trade-offs

Gain:

- low infrastructure burden
- elastic capacity model

Accept:

- less infrastructure control
- need for application capacity design

### Cost impact

Use maximum-capacity guardrails and measure actual utilization.

### Security impact

Use a least-privilege execution role and private connectivity where required.

---

## ADR 2 — Transient EC2 Instead of Long-Running EMR

### Context

Nightly batch workload has a defined processing window.

### Decision

Create a cluster for the workload and terminate it afterward.

### Alternatives

Long-running cluster.

### Trade-off

More startup overhead, less idle cost.

---

## ADR 3 — Spot Task Nodes

### Context

Task capacity can tolerate interruption.

### Decision

Use Spot for selected task capacity.

### Risk

Capacity interruptions.

### Mitigation

- task retry
- diversified instance choices
- On-Demand baseline where needed

---

## ADR 4 — EMR on EKS

### Context

Organization already has a mature EKS platform.

### Decision

Run Spark workloads through EMR on EKS.

### Alternatives

EMR EC2.

### Trade-off

Greater platform complexity, stronger Kubernetes integration.

---

## ADR 5 — Iceberg on S3 with Glue Catalog

### Context

Multiple AWS engines must consume the same lakehouse tables.

### Decision

Use Iceberg with an AWS-compatible catalog architecture.

### Benefits

- transactional table abstraction
- schema evolution
- snapshot model
- cross-engine interoperability

### Risks

- metadata maintenance
- file sizing
- permissions
- concurrent writers

---

# 48. Orchestration Awareness

Topic 10 teaches orchestration deeply.

Here, understand only the boundary:

```text
Orchestrator
     |
     v
Submit EMR job
     |
     v
Wait / poll
     |
     v
Observe
     |
 +---+---+
 |       |
Success Failure
 |       |
Next    Retry/alert
```

Possible orchestrators:

- Step Functions
- MWAA/Airflow
- EventBridge-triggered workflows

Production orchestration requires:

- idempotency
- retry policy
- timeout
- failure notification
- job correlation ID
- safe reprocessing

Do not put business-critical orchestration logic inside a notebook.

---

# 49. EMR Studio and Notebooks

EMR Studio supports interactive development and analytics workflows.

Use it for:

- exploration
- debugging
- interactive Spark development
- data investigation

Do not confuse:

```text
Notebook
=
interactive development

Production pipeline
=
versioned, tested, observable, reproducible execution
```

A notebook can help develop a job.

It should not automatically become the production orchestration system.

---

# 50. Hands-On Labs

## Lab 1 — EMR Serverless

Build:

```text
S3 → EMR Serverless → Iceberg → Athena
```

Measure:

- startup
- runtime
- capacity
- cost estimate

---

## Lab 2 — Transient EMR EC2

Build:

```text
S3
 ↓
EMR EC2
 ↓
Spark
 ↓
S3/Iceberg
```

Include:

- primary
- core
- Spot task capacity

Measure:

- runtime
- cluster size
- logs
- estimated cost

---

## Lab 3 — Same Job, Three Platforms

Run the same Spark workload using:

```text
Glue
EMR Serverless
EMR EC2
```

Record:

| Metric | Glue | EMR Serverless | EMR EC2 |
|---|---:|---:|---:|
| Startup | | | |
| Runtime | | | |
| Cost | | | |
| Configuration effort | | | |
| Operational effort | | | |

Then write a recommendation.

---

## Lab 4 — EMR on EKS

Only perform a real EKS lab if the account has sufficient budget and the learner understands EKS cleanup.

Tasks:

1. Create/use an EKS environment.
2. Create a namespace.
3. Register the namespace as an EMR virtual cluster.
4. Submit a Spark job.
5. Inspect driver pod.
6. Inspect executor pods.
7. Inspect logs.
8. Inspect job state.
9. Remove the virtual cluster.
10. Remove the EKS/EC2 resources created solely for the lab.

If a real EKS environment is too expensive or operationally heavy:

> Build a conceptual/local simulation and label it clearly as a simulation.

Never claim that a local simulation is equivalent to production EKS.

---

## Lab 5 — Iceberg

Build:

```text
S3
 ↓
Iceberg
 ↓
Glue Catalog
 ↓
EMR Serverless
 ↓
Spark
 ↓
Gold table
 ↓
Athena
```

Test:

- read
- append
- schema evolution awareness
- query from Athena

---

## Lab 6 — Deliberate Skew

Create:

```text
UNKNOWN = 60%+ of records
```

Run a skewed join.

Measure:

- slowest task
- stage duration
- partition imbalance

Apply a mitigation.

Measure again.

---

## Lab 7 — Cost Optimization

Compare:

```text
Baseline
vs
Spot task capacity
vs
Managed scaling
vs
Auto-termination
```

Do not combine all changes at once if the purpose is causal measurement.

---

## Lab 8 — Failure Injection

Deliberately introduce:

- missing S3 permission
- missing Python dependency
- invalid Spark configuration
- failed Spark task
- insufficient capacity
- wrong IAM role

For each failure:

```text
Symptom
Evidence
Root cause
Fix
Verification
Prevention
```

---

# 51. Break/Fix Exercises

## Incident 1 — Cannot Read S3

Symptoms:

```text
AccessDenied
```

Investigate:

1. job execution role
2. S3 bucket policy
3. KMS key policy if SSE-KMS is used
4. Lake Formation permissions if governed
5. CloudTrail evidence where appropriate

Do not immediately add `AdministratorAccess`.

---

## Incident 2 — Missing Python Dependency

Symptom:

```text
ModuleNotFoundError
```

Investigate:

```text
Driver environment
      vs
Executor environment
```

Confirm that the dependency is distributed to every required worker.

---

## Incident 3 — Cluster Costs Too Much

Investigate:

- idle duration
- cluster size
- instance type
- Spot usage
- scaling behavior
- auto-termination
- retry volume

---

## Incident 4 — Spark Stage Is Extremely Slow

Investigate:

- skew
- shuffle
- partition count
- executor memory
- executor cores
- spill
- S3 I/O

---

## Incident 5 — EMR Serverless Uses Excessive Capacity

Investigate:

- maximum capacity
- input volume
- Spark configuration
- partition behavior
- skew
- repeated retries

---

## Incident 6 — Cluster Starts but Job Fails

Use:

```text
Cluster state
  ↓
Step state
  ↓
Step logs
  ↓
Spark driver logs
  ↓
Executor logs
  ↓
Spark UI
```

Do not diagnose only from the final error line.

---

# 52. Production Troubleshooting Runbook

Use this reusable structure:

```text
SYMPTOM
  ↓
EVIDENCE
  ↓
LIKELY CAUSES
  ↓
COMMANDS / CONSOLE LOCATIONS
  ↓
DIAGNOSIS
  ↓
FIX
  ↓
VERIFICATION
  ↓
PREVENTION
```

## Useful CLI investigation patterns

```bash
aws emr list-clusters \
  --active

aws emr describe-cluster \
  --cluster-id "$CLUSTER_ID"

aws emr list-steps \
  --cluster-id "$CLUSTER_ID"

aws emr describe-step \
  --cluster-id "$CLUSTER_ID" \
  --step-id "$STEP_ID"
```

For EMR Serverless:

```bash
aws emr-serverless get-application \
  --application-id "$APPLICATION_ID"

aws emr-serverless get-job-run \
  --application-id "$APPLICATION_ID" \
  --job-run-id "$JOB_RUN_ID"
```

For EMR on EKS:

```bash
aws emr-containers describe-virtual-cluster \
  --id "$VIRTUAL_CLUSTER_ID"

aws emr-containers describe-job-run \
  --virtual-cluster-id "$VIRTUAL_CLUSTER_ID" \
  --id "$JOB_RUN_ID"
```

For Kubernetes evidence, use the appropriate current `kubectl` commands for:

- pods
- events
- logs
- resource state

Do not expose credentials in command history.

---

# 53. CLI + boto3 + Terraform

## CLI

Use CLI for:

- learning
- inspection
- incident response
- small operational actions
- automation building blocks

## boto3

Use boto3 for:

- job submission
- status polling
- automation
- workflow integration

Example polling pattern:

```python
import time
import boto3

client = boto3.client("emr-serverless", region_name="us-east-1")

while True:
    response = client.get_job_run(
        applicationId=application_id,
        jobRunId=job_run_id,
    )

    state = response["jobRun"]["state"]
    print(f"state={state}")

    if state in {"SUCCESS", "FAILED", "CANCELLING", "CANCELLED"}:
        break

    time.sleep(15)
```

Production additions:

- timeout
- structured logging
- retry/backoff
- metrics
- failure notification
- idempotency

## Terraform/OpenTofu

Use infrastructure as code for repeatability.

Typical infrastructure concerns:

- VPC
- subnets
- security groups
- IAM roles
- EMR resources
- logging
- EKS infrastructure where required
- tagging
- budget guardrails

Do not copy a provider resource name from an old tutorial without checking the current provider documentation.

---

# 54. Performance Engineering

Connect the Spark mental model to infrastructure:

```text
Spark plan
   |
   v
Stages
   |
   v
Tasks
   |
   v
Executors
   |
   v
EC2 / Serverless workers / Kubernetes pods
```

## Performance dimensions

### CPU

Ask:

> Are executors CPU saturated?

### Memory

Ask:

> Are executors spilling, failing, or running into GC pressure?

### Shuffle

Ask:

> Is data movement dominating the stage?

### Skew

Ask:

> Are a small number of partitions much larger than the others?

### I/O

Ask:

> Is S3/file access the bottleneck?

### Partitioning

Ask:

> Are there too many tiny partitions or too few huge ones?

### File layout

Ask:

> Is the workload reading millions of small files?

---

# 55. Advanced Performance Engineering

## Executor sizing

Larger executors can reduce overhead but can also increase:

- GC pressure
- failure blast radius
- resource fragmentation

## Driver sizing

The driver can become a bottleneck for:

- large query plans
- metadata-heavy operations
- excessive collect operations
- high scheduling overhead

## Broadcast joins

Use only when the broadcast side is genuinely suitable.

## AQE

Use Adaptive Query Execution as a runtime optimization capability, not as a replacement for good data layout.

## Spill

Spill indicates memory pressure and/or workload characteristics that need investigation.

## S3 I/O

Measure:

- input volume
- output volume
- file count
- file size
- compression
- partition pruning

---

# 56. Advanced Cost Engineering

Answer:

> Why did this EMR workload cost 2× more this month?

Use this investigation tree:

```text
Cost increased
      |
      +-- More data?
      |
      +-- Longer runtime?
      |
      +-- Larger cluster?
      |
      +-- Different instance types?
      |
      +-- Less Spot usage?
      |
      +-- More retries?
      |
      +-- Idle time?
      |
      +-- More S3 operations?
      |
      +-- More logging/storage?
      |
      +-- Network changes?
      |
      +-- Inefficient Spark plan?
```

## Cost evidence

Track:

- workload volume
- runtime
- worker count
- instance types
- Spot ratio
- retries
- bytes read
- bytes written
- output file count
- cluster lifetime

Cost engineering is measurement, not guesswork.

---

# 57. Production Engineering Principles

## Reliability

- retries
- idempotency
- failure isolation
- job recovery
- safe reprocessing

## Scalability

- partition sizing
- executor sizing
- node groups
- scaling limits
- workload-aware capacity

## Performance

- Spark UI
- shuffle
- skew
- file layout
- I/O
- executor resources

## Security

- least privilege
- private networking
- encryption
- IAM roles
- Lake Formation

## Cost

- transient clusters
- Spot
- scaling
- right-sizing
- auto-termination
- application maximum capacity

## Operability

- logs
- metrics
- alerts
- runbooks
- reproducible infrastructure

---

# 58. Common Mistakes

## Mistake 1 — Choosing EMR when Glue is sufficient

Fix:

> Compare operational burden and required control before choosing EMR.

## Mistake 2 — Assuming Serverless is always cheaper

Serverless removes infrastructure management, but cost depends on workload behavior and capacity utilization.

## Mistake 3 — Leaving EC2 clusters running

Fix:

> Auto-terminate and verify.

## Mistake 4 — Using Spot carelessly

Fix:

> Use Spot where the workload can recover from interruption.

## Mistake 5 — No cost guardrails

Fix:

> Budget + tags + capacity limits + teardown.

## Mistake 6 — Oversizing instances

Fix:

> Measure resource utilization.

## Mistake 7 — Ignoring Spark UI

Fix:

> Diagnose the slow stage before changing infrastructure.

## Mistake 8 — Adding executors as a universal fix

More capacity cannot fix every bottleneck.

## Mistake 9 — Installing dependencies manually

Fix:

> Build reproducible artifacts.

## Mistake 10 — Non-reproducible bootstrap

Fix:

> Keep initialization small and deterministic.

## Mistake 11 — Public networking by default

Fix:

> Design private subnets and controlled egress.

## Mistake 12 — Overly broad IAM

Fix:

> Separate infrastructure roles from job/runtime roles.

## Mistake 13 — Confusing Kubernetes complexity with value

Fix:

> Require a concrete platform reason for EKS.

## Mistake 14 — Running production pipelines from notebooks

Fix:

> Promote tested code into reproducible jobs.

## Mistake 15 — Not measuring startup time

Startup is part of the workload's real performance.

## Mistake 16 — Not measuring actual cost

A theoretical cost model is not a production cost measurement.

---

# 59. Interview Preparation

## Beginner

### What is Amazon EMR?

**Short answer:**  
Amazon EMR is an AWS-managed platform for running supported big-data workloads such as Apache Spark.

**Production answer:**  
EMR provides multiple operating models, including EC2 clusters, Serverless, and EMR on EKS, allowing teams to trade infrastructure control against operational burden.

---

### Why use EMR?

**Short answer:**  
When the workload needs capabilities or operational models beyond a simpler managed ETL service.

**Production answer:**  
The decision depends on customization, scale, runtime, infrastructure control, cost, networking, and team capabilities.

---

### What is EMR Serverless?

**Answer:**  
A serverless operating model where an application provides a runtime/capacity boundary and individual job runs execute workloads without the learner managing an EC2 cluster.

---

### What are primary, core, and task nodes?

**Answer:**  
Primary nodes provide cluster coordination/services, core nodes provide compute and HDFS-related responsibilities where applicable, and task nodes provide additional compute capacity.

---

### What is an EMR Step?

**Answer:**  
A unit of work submitted to an EMR on EC2 cluster.

---

# 60. Intermediate Interview Questions

## EMR vs Glue?

Answer using:

- infrastructure control
- customization
- startup
- scaling
- operational burden
- workload pattern
- cost

Do not answer:

> "EMR is bigger."

---

## Transient vs long-running?

A transient cluster follows the workload lifecycle.

A long-running cluster prioritizes reuse and reduced repeated startup at the cost of idle and operational burden.

---

## Why Spot task nodes?

Task nodes are generally more interruption-tolerant because they provide compute rather than being the primary location for persistent distributed-storage responsibility.

---

## What is managed scaling?

A mechanism that adjusts compute capacity based on workload demand and configured boundaries.

---

## What is EMR on EKS?

An operating model for running supported EMR Spark workloads on an EKS Kubernetes platform through EMR virtual clusters and Kubernetes scheduling.

---

## What is a virtual cluster?

An EMR representation associated with a Kubernetes namespace on an EKS cluster.

---

# 61. Advanced Interview Questions

## Design a large-scale Spark platform on AWS

A strong answer should cover:

1. S3 data lake
2. Iceberg
3. Glue Catalog
4. Lake Formation
5. Spark compute model
6. IAM/runtime roles
7. private networking
8. observability
9. cost controls
10. orchestration
11. data quality
12. teardown/lifecycle

---

## When would you choose EMR Serverless over EMR EC2?

Use Serverless when:

- cluster operations are not valuable
- workloads are variable
- Spark is required
- application-level capacity controls are sufficient

Use EC2 when:

- cluster-level control matters
- sustained utilization justifies infrastructure
- custom software/configuration is required
- EC2 capacity strategies are important

---

## When is EMR on EKS justified?

When the organization already has a mature EKS platform and Kubernetes provides meaningful platform value.

---

## How would you reduce EMR cost?

Answer:

```text
Measure
  ↓
right-size
  ↓
transient lifecycle
  ↓
Spot where safe
  ↓
instance diversification
  ↓
managed scaling
  ↓
auto-termination
  ↓
optimize Spark
  ↓
track cost per workload
```

---

## How would you diagnose a slow EMR job?

Answer:

```text
Cluster/platform
   ↓
Step/job
   ↓
Spark UI
   ↓
Slow stage
   ↓
Task distribution
   ↓
CPU / memory / shuffle / skew / I/O
   ↓
Fix
   ↓
Measure
```

---

# 62. Scenario-Based Practice Questions

## Question 1

A nightly Spark workload takes four hours. It is large but predictable. The organization does not use Kubernetes.

Which options should be evaluated?

### Solution

Evaluate:

- EMR Serverless
- transient EMR EC2
- Glue if its capabilities meet the requirements

Use measured runtime, operational effort, and cost.

---

## Question 2

Workload volume is highly unpredictable.

### Solution

EMR Serverless is a strong candidate because application capacity can scale with demand and be bounded.

Still compare against Glue.

---

## Question 3

The organization has a mature EKS platform.

### Solution

Evaluate EMR on EKS because Kubernetes may provide meaningful shared-platform value.

---

## Question 4

The organization needs deep cluster customization.

### Solution

Evaluate EMR on EC2.

---

## Question 5

An EMR job costs twice as much as last month.

### Solution

Investigate:

- data volume
- runtime
- cluster size
- instance type
- Spot ratio
- retries
- idle time
- file layout
- S3 operations

---

## Question 6

One Spark task takes 45 minutes while others finish in 5 minutes.

### Solution

Investigate skew and partition imbalance before adding more executors.

---

## Question 7

EMR Serverless starts slowly.

### Solution

Investigate:

- application startup
- worker initialization
- pre-initialized capacity suitability
- job configuration

Do not automatically enable warm capacity without measuring its cost.

---

## Question 8

Executors report `ModuleNotFoundError`.

### Solution

Check dependency distribution to executors and the Python runtime compatibility.

---

## Question 9

An EMR job receives `AccessDenied` on an S3 read.

### Solution

Inspect:

- runtime/job role
- S3 policy
- bucket policy
- KMS permissions if applicable
- Lake Formation if governed

---

## Question 10

The team wants Kubernetes because "it is more modern."

### Solution

Reject the reasoning. Require a concrete operational/platform requirement.

---

# 63. Cheat Sheets

## EMR Models

```text
EMR on EC2
=
Cluster control

EMR Serverless
=
Application + job runs + managed capacity

EMR on EKS
=
EMR Spark + Kubernetes
```

## EC2 Node Types

```text
Primary
=
coordination/services

Core
=
compute + HDFS role where applicable

Task
=
additional compute
```

## Cost Controls

```text
Transient
Spot
Fleets
Managed scaling
Auto-termination
Right-sizing
Capacity limits
Efficient Spark
```

## Troubleshooting

```text
Cluster
  ↓
Step/job
  ↓
Logs
  ↓
Spark UI
  ↓
Stage
  ↓
Task
  ↓
Executor
  ↓
Root cause
  ↓
Fix
  ↓
Measure
```

## Decision Framework

```text
Glue
   vs
EMR Serverless
   vs
EMR EC2
   vs
EMR EKS
```

Ask:

```text
How much infrastructure control?
How variable is workload demand?
How much startup latency is acceptable?
How much customization?
Is Kubernetes already strategic?
What is the cost target?
What can the team operate?
```

---

# 64. Required Mental Models

## Mental Model 1

```text
EMR
=
managed big-data compute
+
AWS integration
+
deployment flexibility
```

## Mental Model 2

```text
EMR EC2
=
you operate the cluster lifecycle
```

## Mental Model 3

```text
EMR Serverless
=
AWS manages the underlying compute lifecycle
```

## Mental Model 4

```text
EMR on EKS
=
Spark workloads operating through Kubernetes
```

## Mental Model 5

```text
Transient cluster
=
create
→ compute
→ destroy
```

## Mental Model 6

```text
Production EMR
=
compute choice
+
Spark tuning
+
security
+
observability
+
cost control
```

---

# 65. Learning Loop

For every major concept:

```text
READ
 ↓
UNDERSTAND
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

This module is complete only when the learner can operate the system, not merely describe it.

---

# 66. Production Readiness Checklist

Before calling an EMR workload production-ready:

## Architecture

- [ ] Compute model chosen from requirements
- [ ] Deployment model documented
- [ ] Workload lifecycle documented
- [ ] Failure modes identified
- [ ] Alternatives rejected with evidence

## Security

- [ ] IAM least privilege
- [ ] Job/runtime role separated appropriately
- [ ] S3 access scoped
- [ ] KMS configured where required
- [ ] Lake Formation controls documented where applicable
- [ ] Private networking evaluated
- [ ] No hard-coded credentials

## Reliability

- [ ] Retry behavior documented
- [ ] Idempotency designed
- [ ] Output recovery designed
- [ ] Backfill/reprocessing strategy defined

## Observability

- [ ] Job logs available
- [ ] Spark UI/event logs available
- [ ] Failure alerts defined
- [ ] Cost visibility available
- [ ] Operational runbook written

## Cost

- [ ] Budget configured
- [ ] Cost tags configured
- [ ] Capacity limits evaluated
- [ ] Spot strategy evaluated
- [ ] Auto-termination configured where appropriate
- [ ] Runtime measured
- [ ] Cost per workload measured

## Reproducibility

- [ ] Infrastructure as code
- [ ] Dependency artifacts versioned
- [ ] Spark configuration versioned
- [ ] EMR release explicitly selected
- [ ] Deployment process documented

---

# 67. Current AWS Documentation Safety

AWS services change frequently.

Before production use, verify:

- EMR release versions
- supported Spark versions
- EMR Serverless capabilities
- EMR on EKS capabilities
- custom-image behavior
- instance support
- Spot behavior
- scaling behavior
- IAM requirements
- Lake Formation integration
- Iceberg integration
- Terraform/OpenTofu provider support
- CLI syntax
- boto3 API shape
- pricing
- service quotas

## Never invent

- pricing
- quotas
- API parameters
- Terraform resource names
- CLI flags
- service integrations
- deprecated behavior

If a detail is not verified:

> **Verify against current AWS documentation before using in production.**

---

# 68. Current-Documentation Notes

The following AWS behaviors are particularly version-sensitive and should be rechecked during implementation:

1. EMR release labels and Spark versions.
2. EMR Serverless worker sizing and application limits.
3. Pre-initialized capacity behavior and idle handling.
4. EMR on EKS release support and job-submission methods.
5. Custom-image support by deployment model/release.
6. Lake Formation prerequisites and release-specific behavior.
7. Current EC2 instance and Spot availability.
8. Current pricing and service quotas.

AWS currently documents EMR Serverless maximum capacity using CPU, memory, and disk limits and documents pre-initialized capacity as a warm worker pool with an associated idle cost. citeturn0search0turn0search2turn0search5

AWS currently documents EMR on EKS virtual clusters as namespace-backed logical EMR environments and job runs as units of work such as Spark JARs, PySpark scripts, and SparkSQL queries. citeturn0search8turn0search10

AWS currently documents Lake Formation integration with EMR using runtime roles and the Glue Data Catalog, with release-specific support for fine-grained access controls. citeturn0search6turn0search9

---

# 69. Final Roadmap Coverage Audit

| Roadmap requirement | Covered? | Where? | Hands-on? |
|---|---|---|---|
| EMR purpose | ✅ | Sections 1–5 | Yes |
| Managed Spark / open-source engines | ✅ | Section 4 | Yes |
| EMR on EC2 | ✅ | Sections 8–14 | Yes |
| Primary nodes | ✅ | Sections 9–10 | Yes |
| Core nodes | ✅ | Sections 9–10 | Yes |
| Task nodes | ✅ | Sections 9–10 | Yes |
| EMR Steps | ✅ | Section 11 | Yes |
| Transient clusters | ✅ | Section 12 | Yes |
| Long-running clusters | ✅ | Section 12 | Yes |
| EMR Serverless | ✅ | Sections 15–18 | Yes |
| Applications | ✅ | Section 15 | Yes |
| Job runs | ✅ | Section 16 | Yes |
| Automatic scaling | ✅ | Section 17 | Yes |
| Pre-initialized capacity | ✅ | Section 17 | Yes |
| Maximum capacity | ✅ | Section 17 | Yes |
| EMR on EKS | ✅ | Sections 19–21 | Yes |
| Virtual clusters | ✅ | Section 20 | Yes |
| Spot task nodes | ✅ | Section 36 | Yes |
| Instance fleets | ✅ | Section 37 | Yes |
| Managed scaling | ✅ | Section 38 | Yes |
| Auto-termination | ✅ | Section 39 | Yes |
| Spark configuration | ✅ | Sections 23–24 | Yes |
| Bootstrap actions | ✅ | Section 25 | Yes |
| Custom images | ✅ | Section 26 | Yes |
| Python dependencies | ✅ | Section 27 | Yes |
| Iceberg | ✅ | Sections 28–30 | Yes |
| Delta awareness | ✅ | Section 31 | Awareness |
| Hudi awareness | ✅ | Section 31 | Awareness |
| Glue Catalog | ✅ | Section 29 | Yes |
| Lake Formation | ✅ | Section 32 | Yes |
| Logs | ✅ | Section 33 | Yes |
| Spark UI | ✅ | Sections 33–34 | Yes |
| Glue vs EMR comparison | ✅ | Sections 5 and 45 | Yes |
| Step Functions/Airflow submission awareness | ✅ | Section 48 | Conceptual |
| EMR Studio awareness | ✅ | Section 49 | Awareness |
| Security | ✅ | Sections 40–43 | Yes |
| Execution roles | ✅ | Section 42 | Yes |
| Encryption | ✅ | Section 43 | Yes |
| Private subnets | ✅ | Section 41 | Yes |
| Hands-on EMR Serverless lab | ✅ | Lab 1 | Yes |
| Hands-on EMR EC2 lab | ✅ | Lab 2 | Yes |
| Hands-on EMR on EKS lab | ✅ | Lab 4 | Yes |
| Iceberg lab | ✅ | Lab 5 | Yes |
| Deliberate skew diagnosis | ✅ | Lab 6 | Yes |
| Cost comparison | ✅ | Labs 2, 3, 7 | Yes |
| Failure injection | ✅ | Lab 8 | Yes |
| Production decision-making | ✅ | Sections 46–47 | Yes |
| Architecture decision records | ✅ | Section 47 | Yes |
| Production runbook | ✅ | Section 52 | Yes |
| Interview preparation | ✅ | Sections 59–60 | Yes |
| Practice questions | ✅ | Section 62 | Yes |
| Cheat sheets | ✅ | Section 63 | Yes |
| Mental models | ✅ | Section 64 | Yes |
| Cost safety | ✅ | Warning + Sections 36–37, 54–56 | Yes |
| AWS documentation safety | ✅ | Sections 67–68 | Yes |

### Roadmap Coverage

**100% of the explicitly supplied Topic 09 requirements are covered.**

---

# 70. Final Quality Check

## Content

- [x] Starts from beginner concepts
- [x] Progresses to advanced production concepts
- [x] Uses simple language before professional terminology
- [x] Uses Data Engineering terminology
- [x] Covers the supplied roadmap concepts
- [x] Includes Python examples
- [x] Includes AWS CLI examples
- [x] Includes boto3 examples
- [x] Includes Terraform/OpenTofu guidance
- [x] Includes hands-on labs
- [x] Includes break/fix scenarios
- [x] Includes troubleshooting
- [x] Includes Spark UI investigation
- [x] Includes performance engineering
- [x] Includes cost engineering
- [x] Includes security
- [x] Includes architecture decisions
- [x] Includes decision matrices
- [x] Includes interview preparation
- [x] Includes practice questions
- [x] Includes cheat sheets
- [x] Includes final roadmap audit

## AWS correctness

- [x] No intentionally invented APIs
- [x] No invented quotas
- [x] No hard-coded pricing
- [x] No hard-coded credentials
- [x] Version-sensitive behavior is explicitly marked for verification
- [x] Current official AWS documentation was consulted for key EMR Serverless, EMR on EKS, bootstrap, and Lake Formation claims

## Production quality

- [x] IAM least privilege
- [x] Private networking discussed
- [x] Encryption discussed
- [x] Logs discussed
- [x] Monitoring discussed
- [x] Failure handling discussed
- [x] Cost guardrails discussed
- [x] Teardown discussed
- [x] Reproducibility discussed
- [x] Idempotency discussed
- [x] Operational runbooks included

## File scope

This learning artifact is intentionally self-contained.

No additional source files, Terraform files, code files, or supporting Markdown files are required for the module itself.

---

# 71. Final Operating Standard

A Data Engineer who has completed this module should be able to say:

> **I do not choose EMR because it is powerful. I choose an EMR operating model because the workload requirements justify its control, scalability, customization, cost profile, and operational complexity.**

The production mental model is:

```text
Requirements
     |
     v
Compute model
     |
     v
Spark configuration
     |
     v
Security
     |
     v
Networking
     |
     v
Observability
     |
     v
Cost controls
     |
     v
Failure recovery
     |
     v
Measured production outcome
```

And the final decision model is:

```text
                    Spark workload
                          |
             +------------+------------+
             |            |            |
            Glue       EMR Serverless  EMR
                                      |
                                +-----+-----+
                                |           |
                               EC2         EKS
             |
             v
       Choose from evidence:
       control
       startup
       scale
       customization
       security
       cost
       operations
       team skills
```

**Depth in one cloud turns general data-engineering knowledge into deliverable systems.**
