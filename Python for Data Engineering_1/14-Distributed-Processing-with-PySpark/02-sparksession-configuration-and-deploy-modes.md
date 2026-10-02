# SparkSession, Configuration, and Deploy Modes

> **Stage:** 2 — Python for Data Engineering  
> **Module:** 2.14 — Distributed Processing with PySpark  
> **Topic:** 02 — SparkSession, Configuration and Deploy Modes  
> **Target:** Apache Spark 4.x / PySpark 4.x  
> **Level:** Beginner → Production Data Engineer  
>
> This chapter assumes that Topic 01 introduced the driver, executors, worker nodes, cluster managers, partitions, tasks, jobs, stages, and basic PySpark architecture. This chapter focuses on the next question:
>
> **How do we create a Spark application, configure it, launch it, and move the same application from local development into a real cluster environment?**

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

1. Explain what a Spark application is.
2. Explain what `SparkSession` is and why it exists.
3. Create and configure a `SparkSession`.
4. Explain the conceptual relationship between `SparkSession` and `SparkContext`.
5. Explain what `SparkConf` is.
6. Inspect effective Spark configuration.
7. Distinguish application logic from Spark configuration and infrastructure configuration.
8. Explain configuration sources and precedence without assuming that one universal precedence rule applies to every property.
9. Explain static/startup configuration versus runtime configuration.
10. Explain local execution modes such as `local`, `local[2]`, and `local[*]`.
11. Explain Spark Standalone deployment.
12. Explain the difference between `--master` and `--deploy-mode`.
13. Explain client deploy mode.
14. Explain cluster deploy mode.
15. Explain how `spark-submit` launches a Spark application.
16. Explain driver and executor resource configuration.
17. Explain why driver and executor Python environments must be compatible.
18. Explain how Python dependencies can be distributed.
19. Explain how one application can move from development to testing, staging, and production without embedding environment-specific infrastructure in business logic.
20. Diagnose common configuration and deployment problems.
21. Reason about deployment architecture rather than memorizing commands.

The core mental model is:

```text
PySpark Application
        ↓
   SparkSession
        ↓
Spark Configuration
        ↓
Deployment Configuration
        ↓
   Cluster Manager
        ↓
 Driver + Executors
```

---

# 2. What Is a Spark Application?

A **Spark application** is a complete application execution coordinated by a Spark driver and supported by executor processes.

A PySpark application normally contains:

- Python application code
- a `SparkSession`
- driver-side execution
- Spark configuration
- executors
- a deployment environment
- data-processing logic

A simplified architecture is:

```text
                    Python Application
                           |
                           v
                    +-------------+
                    | SparkSession|
                    +------+------+
                           |
                           v
                     Spark Driver
                           |
                           v
                    Cluster Manager
                           |
                 +---------+---------+
                 |                   |
                 v                   v
             Executor 1          Executor 2
                 |                   |
                 +---------+---------+
                           |
                         Tasks
```

### What each component means

**Python application**

The code you write.

**SparkSession**

The primary entry point through which modern PySpark applications interact with Spark.

**Driver**

The coordinating process for the application.

**Cluster manager**

The resource-management layer that helps allocate resources and launch application components.

**Executors**

Processes that execute distributed work for the application.

This connects directly to Topic 01. Topic 01 explained *what* these components are; this topic explains *how the application is configured and launched*.

---

# 3. What Is SparkSession?

## 3.1 Simple Explanation

`SparkSession` is the primary entry point for working with Spark from modern PySpark applications.

You can think of it as the application's main gateway into the Spark runtime.

```text
Your Python application
          |
          v
    SparkSession
          |
          v
      Spark runtime
```

Instead of your code manually assembling many lower-level Spark components, modern PySpark applications normally begin with a `SparkSession`.

---

## 3.2 Why Does SparkSession Exist?

Older Spark APIs exposed multiple entry points for different capabilities.

Modern Spark consolidated the primary application-facing APIs around `SparkSession`.

This gives application code a consistent starting point for:

- DataFrame operations
- Spark SQL
- configuration access
- catalog interaction
- application-level Spark functionality

RDD-specific APIs and lower-level APIs still exist, but they are not the focus of this chapter.

---

## 3.3 SparkSession Is Not the Driver

A common beginner mistake is:

> "SparkSession is the driver."

They are related, but they are not the same thing.

A useful mental model is:

```text
PySpark application
       |
       v
SparkSession
       |
       v
Driver-side Spark runtime
       |
       +------------------+
       |                  |
       v                  v
   Planning/          Coordination
   execution          with executors
```

`SparkSession` is an application-facing API object.

The driver is the process responsible for coordinating the application.

---

# 4. Creating a SparkSession

The canonical pattern is:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("MySparkApplication")
    .getOrCreate()
)
```

Let's understand every part.

---

## 4.1 Import SparkSession

```python
from pyspark.sql import SparkSession
```

This imports the modern PySpark entry-point class.

---

## 4.2 `SparkSession.builder`

```python
SparkSession.builder
```

The builder provides a fluent API for constructing or retrieving a SparkSession.

You can add application settings before finalizing the session.

---

## 4.3 `.appName(...)`

```python
.appName("MySparkApplication")
```

This gives the Spark application an identifiable name.

Application names matter because operators need to distinguish workloads in:

- Spark UIs
- cluster-management systems
- logs
- monitoring systems
- production job history

Use meaningful names.

For example:

```python
.appName("DailyCustomerAggregation")
```

is more useful operationally than:

```python
.appName("test")
```

---

## 4.4 `.getOrCreate()`

```python
.getOrCreate()
```

This asks Spark to return an existing session when one is already available in the relevant application context, or create one when necessary.

This is especially useful in:

- notebooks
- interactive development
- applications that should have one primary SparkSession

It also helps avoid casually creating multiple independent sessions when application code does not need them.

---

# 5. What Happens When SparkSession Is Created?

Consider:

```python
spark = (
    SparkSession.builder
    .appName("Demo")
    .getOrCreate()
)
```

Conceptually:

```text
Python code
    |
    v
SparkSession.builder
    |
    v
Application configuration
    |
    v
Spark runtime initialization
    |
    v
Driver-side Spark environment
```

The exact internal lifecycle depends on the deployment environment.

The important mental model is:

```text
SparkSession
    ↓
connects application code
    ↓
to the Spark execution environment
```

The session does not itself become an executor.

---

# 6. SparkSession Builder API

The most important builder operations for this chapter are:

```python
SparkSession.builder
```

```python
.appName(...)
```

```python
.master(...)
```

```python
.config(...)
```

```python
.enableHiveSupport()
```

```python
.getOrCreate()
```

---

## 6.1 `.master(...)`

Example:

```python
SparkSession.builder.master("local[*]")
```

This specifies the Spark master/deployment target from the application side.

It is useful for local development.

However, production applications often receive deployment configuration externally through `spark-submit` or the platform rather than hardcoding the deployment target in application source.

---

## 6.2 `.config(...)`

Example:

```python
SparkSession.builder.config(
    "spark.sql.shuffle.partitions",
    "10",
)
```

This supplies a Spark configuration property.

Use configuration deliberately.

Avoid turning application code into a large collection of environment-specific deployment settings.

---

## 6.3 `.enableHiveSupport()`

This enables Hive-related support when the application/environment requires it.

It is relevant when working with compatible catalog/metastore setups.

Do not add it simply because "production Spark should always enable Hive support."

The correct configuration depends on the platform and catalog architecture.

---

## 6.4 Production Guidance

A useful production pattern is:

```text
Application code
    ↓
Business/data-processing logic

Deployment layer
    ↓
Master
Deploy mode
Resources
Environment
Infrastructure
```

The goal is to prevent application logic from becoming tightly coupled to one environment.

---

# 7. Understanding `getOrCreate()`

Consider:

```python
spark = (
    SparkSession.builder
    .appName("MyApplication")
    .getOrCreate()
)
```

The name is meaningful:

```text
get existing session
        OR
create a session
```

## 7.1 Why This Matters in Notebooks

In an interactive notebook, you may execute:

```python
spark = ...
```

multiple times.

Creating a new Spark application/session every time without understanding the lifecycle can produce confusing behaviour.

A single primary session is normally easier to reason about.

---

## 7.2 Demonstration

```python
from pyspark.sql import SparkSession

spark1 = (
    SparkSession.builder
    .appName("Demo")
    .getOrCreate()
)

spark2 = (
    SparkSession.builder
    .appName("DemoAgain")
    .getOrCreate()
)

print(spark1 is spark2)
```

In a normal shared-session context, the second call can retrieve the existing session rather than blindly creating another independent session.

The important lesson is not to rely on object identity as a production design principle. The important lesson is:

> Understand the session lifecycle of the environment in which your code runs.

---

# 8. SparkSession and SparkContext

Historically, `SparkContext` represented a lower-level connection to the Spark execution environment.

The modern conceptual relationship is:

```text
SparkSession
      |
      v
SparkContext
      |
      v
Spark execution environment
```

You can access the context through:

```python
spark.sparkContext
```

For example:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("ContextDemo")
    .master("local[*]")
    .getOrCreate()
)

sc = spark.sparkContext

print(sc.appName)
```

## 8.1 Why SparkSession Is the Normal Starting Point

Modern PySpark applications generally begin with:

```python
SparkSession
```

rather than constructing a standalone `SparkContext` for ordinary DataFrame/Spark SQL work.

`SparkContext` still appears in:

- legacy applications
- lower-level APIs
- real production code
- older tutorials
- APIs that expose context-level functionality

Do not confuse "older" with "invalid." The correct question is whether the API is appropriate for the workload and Spark version.

RDD-specific details belong to Topic 03.

---

# 9. What Is Spark Configuration?

A useful distinction is:

> **Application code tells Spark what work to perform; configuration tells Spark how the application should run.**

For example:

```text
Application logic
    |
    +-- read data
    +-- transform data
    +-- aggregate
    +-- write data

Spark configuration
    |
    +-- application name
    +-- deployment target
    +-- driver resources
    +-- executor resources
    +-- runtime behaviour
```

There is also infrastructure configuration:

```text
Infrastructure
    |
    +-- machines
    +-- containers
    +-- Kubernetes resources
    +-- network
    +-- storage
    +-- credentials
```

These are related but distinct layers.

---

# 10. Three Configuration Layers

A production Data Engineer should distinguish:

```text
1. Application logic
2. Spark configuration
3. Infrastructure configuration
```

## Application logic

Answers:

> What should the pipeline do?

Example:

```python
df = spark.read.parquet(input_path)

result = transform(df)

result.write.mode("overwrite").parquet(output_path)
```

## Spark configuration

Answers:

> How should Spark execute this application?

Examples:

```text
spark.executor.memory
spark.executor.cores
spark.driver.memory
spark.sql.shuffle.partitions
```

## Infrastructure configuration

Answers:

> What resources and environment exist around Spark?

Examples:

- Kubernetes pods
- worker machines
- network policies
- object-storage access
- container images
- infrastructure credentials

This separation becomes increasingly important as applications move toward production.

---

# 11. SparkConf

`SparkConf` is a configuration object used to define Spark settings.

Example:

```python
from pyspark import SparkConf

conf = SparkConf()

conf.setAppName("ConfigurationDemo")
conf.set("spark.executor.memory", "4g")
```

The resulting configuration can be supplied when constructing Spark's execution environment.

For example:

```python
from pyspark import SparkConf
from pyspark.sql import SparkSession

conf = (
    SparkConf()
    .setAppName("ConfigurationDemo")
)

spark = (
    SparkSession.builder
    .config(conf=conf)
    .getOrCreate()
)
```

Modern applications also commonly use the builder directly:

```python
spark = (
    SparkSession.builder
    .appName("ConfigurationDemo")
    .config("spark.executor.memory", "4g")
    .getOrCreate()
)
```

The important concept is that `SparkConf` and builder `.config()` both participate in supplying Spark configuration.

---

# 12. Configuration Through SparkSession

A common modern pattern is:

```python
spark = (
    SparkSession.builder
    .appName("MyApplication")
    .config("spark.sql.shuffle.partitions", "10")
    .getOrCreate()
)
```

The structure is:

```text
config("KEY", "VALUE")
        |
        +-- key = Spark property name
        |
        +-- value = configured value
```

Examples:

```python
.config("spark.executor.memory", "4g")
.config("spark.executor.cores", "4")
.config("spark.sql.shuffle.partitions", "100")
```

Configuration values are often represented as strings when supplied through command-line or configuration files.

Spark interprets the value according to the property.

---

# 13. Important Configuration Categories

## 13.1 Application Identity

```text
spark.app.name
```

Identifies the application.

In code:

```python
.appName("DailyOrdersPipeline")
```

---

## 13.2 Deployment Target

```text
spark.master
```

Conceptually identifies where Spark should run.

Examples:

```text
local[*]
spark://spark-master:7077
```

In production, deployment systems may provide this externally.

---

## 13.3 Driver Resources

```text
spark.driver.memory
spark.driver.cores
```

These describe driver-side resource requirements.

Example:

```text
spark.driver.memory = 4g
spark.driver.cores  = 2
```

Driver resources are not the same thing as executor resources.

---

## 13.4 Executor Resources

```text
spark.executor.memory
spark.executor.cores
spark.executor.instances
```

These describe resources allocated for executor processes.

Example:

```text
spark.executor.memory    = 8g
spark.executor.cores     = 4
spark.executor.instances = 3
```

Conceptually:

```text
3 executors
×
4 cores
=
approximately 12 task slots
```

Actual resource allocation depends on the cluster manager and infrastructure.

---

## 13.5 Python Environment

Important properties include:

```text
spark.pyspark.python
spark.pyspark.driver.python
```

These help control which Python executable/environment is used for:

- executor-side Python processes
- driver-side Python execution

Exact deployment semantics can depend on how Spark is launched and how the environment is packaged.

---

## 13.6 Runtime / SQL Configuration

Many runtime settings are accessible through:

```python
spark.conf
```

For example:

```python
spark.conf.get("spark.sql.shuffle.partitions")
```

This topic only establishes the configuration mechanism. The detailed meaning and tuning of individual SQL execution settings belongs to later Module 2.14 topics.

---

## 13.7 Serialization

You may encounter:

```text
spark.serializer
```

Serialization determines how certain objects are serialized for distributed execution.

For this chapter, remember:

```text
Serialization
    ↓
moves/represents data and objects across execution boundaries
```

Serialization performance is an important distributed-systems concern, but it is not a primary subject of this chapter.

---

# 14. `spark.conf`

Spark provides runtime configuration access through:

```python
spark.conf
```

## 14.1 Read a Configuration

```python
value = spark.conf.get("spark.sql.shuffle.partitions")

print(value)
```

This is useful when you need to know what configuration Spark currently exposes for a property.

---

## 14.2 Set a Runtime Configuration

Where the property supports runtime modification:

```python
spark.conf.set(
    "spark.sql.shuffle.partitions",
    "10",
)
```

Then:

```python
print(
    spark.conf.get("spark.sql.shuffle.partitions")
)
```

The important lesson is:

> Not every Spark configuration property can safely or meaningfully be changed after the application has started.

---

## 14.3 Unset

Where supported:

```python
spark.conf.unset("some.property")
```

Do not assume that every property can be unset or dynamically modified.

Always distinguish runtime SQL/application settings from deployment/resource settings.

---

# 15. Static vs Runtime Configuration

This distinction is critical.

Some configuration affects how Spark starts or how resources are allocated.

Other configuration controls behaviour during an already-running application.

Think:

```text
Startup / deployment configuration
            vs
Runtime configuration
```

Ask:

> **Does this setting affect how Spark starts, allocates resources, or establishes the execution environment, or can it safely change after startup?**

### Examples of deployment/resource concerns

```text
spark.driver.memory
spark.driver.cores
spark.executor.memory
spark.executor.cores
spark.executor.instances
```

These are tied closely to how the application receives resources.

### Runtime configuration example

A SQL/runtime setting may be adjustable through:

```python
spark.conf.set(...)
```

### Engineering rule

Do not assume:

```python
spark.conf.set(...)
```

can dynamically resize your cluster.

Changing:

```text
spark.executor.memory
```

after executors have already been allocated is fundamentally different from changing a runtime SQL property.

---

# 16. Configuration Sources

Spark configuration can come from several places.

A useful conceptual model is:

```text
Defaults
   ↓
Configuration files
   ↓
Submission-time settings
   ↓
Application-level settings
   ↓
Runtime settings
```

However, do **not** memorize this diagram as a universal precedence law.

The effective configuration depends on:

- the specific property
- how Spark was launched
- deployment mode
- cluster manager
- configuration file
- command-line options
- application code
- runtime APIs

The production habit is:

> **Inspect the effective configuration instead of assuming which source won.**

---

# 17. `spark-defaults.conf`

`spark-defaults.conf` is a configuration file commonly used to provide Spark defaults.

A conceptual file may contain:

```text
spark.app.name              MyApplication
spark.executor.memory       4g
spark.executor.cores        2
```

This can be useful for:

- environment-level defaults
- standardized configuration
- cluster-level administration
- reducing repeated command-line arguments

### Risks

Centralized defaults can also create confusion if developers do not know they exist.

For example:

```text
Application code says one thing
       +
spark-defaults.conf says another
       +
spark-submit overrides something
```

This is why production systems should make effective configuration observable.

---

# 18. `spark-env.sh`

`spark-env.sh` is a Spark environment configuration script used in deployments where environment variables and host-level settings need to be defined.

It is useful for things such as:

- environment variables
- host-specific Spark settings
- deployment environment customization

Do not confuse environment variables with Spark configuration properties.

For example:

```text
Environment variable
        ≠
Spark configuration property
```

They can influence the same application environment but operate through different mechanisms.

---

# 19. Local Deployment Mode

Local mode runs Spark on one machine.

Common forms include:

```text
local
local[1]
local[2]
local[4]
local[*]
```

## 19.1 `local`

A simple local execution mode.

## 19.2 `local[2]`

Conceptually requests two local execution threads.

```text
One machine
   |
   +-- local execution thread 1
   +-- local execution thread 2
```

## 19.3 `local[4]`

Conceptually uses four local execution threads.

## 19.4 `local[*]`

Uses the available logical processors for local execution.

This is extremely convenient for development.

---

# 20. Running Local Mode

Example:

```bash
spark-submit \
  --master local[2] \
  jobs/my_job.py
```

Or:

```bash
spark-submit \
  --master local[*] \
  jobs/my_job.py
```

The mental model is:

```text
Submitting machine
       |
       v
One local Spark execution environment
       |
       v
Local execution resources
```

There is no multi-machine cluster.

---

# 21. Why Local Mode Is Useful

Local mode is excellent for:

- learning
- development
- unit tests
- integration tests
- fast experiments
- debugging application logic

It removes much of the infrastructure complexity while retaining Spark's programming model.

---

# 22. Why Local Mode Is Not a Real Cluster

`local[*]` is useful but can hide production problems.

It does not fully reproduce:

- multiple worker machines
- real inter-machine network communication
- executor placement across hosts
- worker failure
- cluster resource contention
- production object-storage conditions
- cluster-level Python environment differences
- all deployment-specific scheduling behaviour

Therefore:

```text
Works locally
      ≠
Guaranteed to work identically in production
```

But do not overstate the difference.

Local mode is still valuable for validating:

- application syntax
- transformations
- basic correctness
- many unit/integration behaviours

The correct engineering approach is:

```text
Local testing
    +
representative cluster testing
    +
production deployment validation
```

---

# 23. Spark Standalone

Spark Standalone is Spark's own cluster-management system.

A conceptual architecture is:

```text
                  Spark Master
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Worker 1     Worker 2     Worker 3
          |            |            |
       Executor     Executor     Executor
```

The roles are:

- **Master** — coordinates resource allocation in the Standalone system.
- **Worker** — provides resources.
- **Driver** — coordinates the Spark application.
- **Executor** — executes application work.

The master and Spark driver are not the same thing.

```text
Master
  ↓
resource management

Driver
  ↓
application coordination
```

---

# 24. Spark Standalone Application Flow

Conceptually:

```text
Developer / scheduler
        |
        | spark-submit
        v
Spark Standalone Master
        |
        | resource allocation
        v
Worker nodes
        |
        v
Executors
        |
        v
Tasks
```

This connects directly to Topic 01.

Topic 01 taught the components.

Topic 02 teaches how submission and configuration determine where those components run.

---

# 25. `--master`

The `--master` argument identifies the deployment target/master.

Example:

```bash
spark-submit \
  --master local[*] \
  my_job.py
```

or:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  my_job.py
```

The meaning is fundamentally:

> **Which Spark execution/deployment target should receive this application?**

---

# 26. `--master` vs `--deploy-mode`

These are commonly confused.

### `--master`

Answers:

> **Which cluster manager/deployment target?**

Examples:

```text
local[*]
spark://spark-master:7077
```

### `--deploy-mode`

Answers:

> **Where should the driver run relative to the submission client?**

Examples:

```text
client
cluster
```

Therefore:

```text
--master
    =
where/how Spark is deployed

--deploy-mode
    =
where the driver runs
```

This distinction is one of the most important ideas in this chapter.

---

# 27. Client vs Cluster Deploy Mode

## 27.1 Client Mode

Conceptually:

```text
Submitting Machine
       |
       v
     Driver
       |
       v
 Cluster Manager
       |
       v
   Executors
```

The driver runs on the machine from which the application is submitted.

This is useful for:

- interactive development
- environments where the submission host is expected to remain available
- debugging with direct access to driver logs

But it creates a dependency:

```text
Submitting machine
       ↓
must remain available for driver
```

for the lifetime of the application.

---

## 27.2 Cluster Mode

Conceptually:

```text
Submitting Machine
       |
       v
 Cluster Manager
       |
       v
     Driver
       |
       v
   Executors
```

The driver is launched within the cluster environment.

The submitting machine primarily submits the application rather than hosting the long-running driver.

This is often useful for scheduled production workloads because the application is less dependent on the interactive submission host.

---

# 28. Client Mode — Detailed Example

Consider:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  jobs/my_job.py
```

Conceptual lifecycle:

```text
1. Developer machine runs spark-submit
              ↓
2. Spark client starts/hosts driver
              ↓
3. Driver communicates with cluster manager
              ↓
4. Resources are allocated
              ↓
5. Executors start
              ↓
6. Driver coordinates work
              ↓
7. Executors execute tasks
```

### Operational implications

The submitting machine matters because it hosts the driver.

If that machine:

- loses network connectivity
- terminates
- loses the process
- becomes unavailable

the application can be affected.

Logs are also naturally associated with the driver environment on the submitting side.

---

# 29. Cluster Mode — Detailed Example

Consider:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  jobs/my_job.py
```

Conceptual lifecycle:

```text
1. Submission machine sends application request
              ↓
2. Cluster manager receives request
              ↓
3. Driver is launched in cluster environment
              ↓
4. Driver requests/uses executor resources
              ↓
5. Executors start
              ↓
6. Driver coordinates execution
              ↓
7. Application runs inside cluster
```

The submitting machine does not need to remain the application's driver host.

This can be useful for scheduled batch processing.

---

# 30. Client vs Cluster Comparison

| Concern | Client mode | Cluster mode |
|---|---|---|
| Driver location | Submission/client environment | Cluster environment |
| Submission host dependency | Higher | Lower after submission |
| Interactive debugging | Often convenient | Less directly interactive |
| Driver logs | Associated with client environment | Cluster-side |
| Production batch use | Depends on environment | Often useful for cluster-managed batch |
| Network considerations | Client must communicate with cluster | Driver is inside cluster |
| Application lifecycle | Driver tied to client process/environment | Driver tied to cluster-managed application |

Neither mode is universally correct.

The appropriate choice depends on:

- workload type
- scheduler
- network topology
- operational model
- logging
- failure requirements
- cluster platform

---

# 31. Deployment Environments

Spark can be deployed using several environments:

```text
Local
   ↓
Spark Standalone
   ↓
YARN
   ↓
Kubernetes
   ↓
Managed Spark platforms
```

The important question is not "Which one is the best?"

The useful engineering questions are:

- What manages resources?
- Where does the driver run?
- Where do executors run?
- How is the application submitted?
- How are Python dependencies supplied?
- How are logs collected?
- What happens when infrastructure fails?

---

# 32. YARN and Kubernetes — Scope for This Chapter

Topic 01 introduced YARN and Kubernetes as cluster managers.

Here, only the deployment relationship matters.

### YARN

```text
spark-submit
     ↓
YARN
     ↓
Driver + Executors
```

YARN provides the resource-management environment.

### Kubernetes

```text
spark-submit
     ↓
Kubernetes
     ↓
Driver Pod + Executor Pods
```

Kubernetes provides the container orchestration environment.

This chapter does not teach:

- Kubernetes administration
- YARN administration
- cluster security configuration
- advanced storage/networking

Those are separate infrastructure concerns.

---

# 33. `spark-submit`

`spark-submit` is the standard command-line mechanism for launching Spark applications.

A conceptual structure is:

```bash
spark-submit \
    --master ... \
    --deploy-mode ... \
    --conf ... \
    application.py
```

Think of it as:

```text
Application artifact
       +
Deployment instructions
       +
Spark configuration
       ↓
Spark application launch
```

---

# 34. Important `spark-submit` Options

## `--master`

Specifies the deployment target.

```bash
--master local[*]
```

or:

```bash
--master spark://spark-master:7077
```

---

## `--deploy-mode`

Specifies driver deployment mode.

```bash
--deploy-mode client
```

or:

```bash
--deploy-mode cluster
```

---

## `--conf`

Supplies a Spark configuration property.

```bash
--conf spark.executor.memory=8g
```

---

## `--name`

Sets the application name.

```bash
--name DailyCustomerPipeline
```

---

## `--packages`

Requests JVM/Java dependencies from configured package repositories.

Example:

```bash
--packages group:artifact:version
```

Use this only when the required package coordinates are known and compatible with the Spark/Scala/runtime environment.

---

## `--jars`

Supplies additional JAR dependencies.

```bash
--jars path/to/dependency.jar
```

---

## `--py-files`

Supplies Python files/packages needed by the application.

```bash
--py-files dependencies.zip
```

The exact packaging method should match the project's Python dependency strategy.

---

# 35. Complete `spark-submit` Example

A conceptual production-style submission might look like:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --name DailyCustomerPipeline \
  --conf spark.driver.memory=4g \
  --conf spark.executor.memory=8g \
  --conf spark.executor.cores=4 \
  --conf spark.executor.instances=3 \
  jobs/daily_customer_pipeline.py
```

This command expresses:

```text
Deployment target
        ↓
Driver placement
        ↓
Application identity
        ↓
Driver resources
        ↓
Executor resources
        ↓
Application code
```

It does not guarantee that the cluster can provide those resources.

---

# 36. Driver Resource Configuration

Important settings include:

```text
spark.driver.memory
spark.driver.cores
```

## Driver memory

Example:

```text
spark.driver.memory = 4g
```

This describes driver memory allocation.

The driver needs memory for things such as:

- application coordination
- planning state
- metadata
- results that are intentionally returned to it
- driver-side Python/application objects

The driver should not be treated as a location to store the entire distributed dataset.

---

## Driver cores

Example:

```text
spark.driver.cores = 2
```

This provides driver CPU resources.

Driver CPU needs are different from executor CPU needs because the driver coordinates the application rather than processing all distributed partitions.

---

# 37. Executor Resource Configuration

Important settings include:

```text
spark.executor.memory
spark.executor.cores
spark.executor.instances
```

Suppose:

```text
3 executors
4 cores per executor
8 GB memory per executor
```

Conceptually:

```text
Executor 1 → 4 cores / 8 GB
Executor 2 → 4 cores / 8 GB
Executor 3 → 4 cores / 8 GB

Total configured executor cores ≈ 12
Total configured executor memory ≈ 24 GB
```

This does not mean that exactly 24 GB of usable memory is available for arbitrary application data.

There are JVM/runtime overheads and cluster-manager constraints.

Likewise, configured resources are not the same as guaranteed available resources.

---

# 38. Resource Model

The complete mental model is:

```text
Cluster Capacity
       ↓
Cluster Manager
       ↓
Driver + Executors
       ↓
CPU + Memory
       ↓
Tasks
```

A configuration such as:

```text
spark.executor.cores=4
```

is an instruction/request in the Spark deployment model.

The actual outcome depends on:

- cluster capacity
- cluster manager
- worker resources
- scheduling
- platform policies
- application configuration

---

# 39. Configuration Is Not Capacity

This distinction is critical.

Suppose you specify:

```text
spark.executor.instances=20
```

That does not mean:

```text
20 executors will definitely start.
```

If the cluster has insufficient capacity, policies prevent allocation, or deployment configuration is incompatible, the application may not receive the requested resources.

Similarly:

```text
spark.executor.memory=64g
```

does not create 64 GB of RAM.

It requests/configures that resource size for executor processes within the supported deployment environment.

---

# 40. Driver Python vs Executor Python

PySpark applications contain Python execution on the driver and may involve Python processes on executors.

Therefore:

```text
Driver Python environment
        ≠
Executor Python environment
```

They need to be compatible.

A common failure looks like:

```text
Developer laptop
   |
   +-- pandas 2.x
   +-- custom package X
   +-- Python 3.12

Cluster executor
   |
   +-- missing package X
   +-- incompatible Python
```

The driver may successfully start while executor-side work fails later.

---

# 41. Python Environment Configuration

Relevant properties include:

```text
spark.pyspark.driver.python
spark.pyspark.python
```

Conceptually:

```text
Driver
  ↓
Driver Python

Executors
  ↓
Executor Python
```

The exact way these are configured depends on the deployment environment.

The key production requirement is:

> **Make the Python runtime and dependencies reproducible across driver and executor environments.**

---

# 42. Dependency Distribution

Python dependencies can be made available using approaches such as:

- virtual environments
- packaged Python environments
- `--py-files`
- container images
- environment-specific packaging mechanisms
- platform-managed dependency environments

For example:

```bash
spark-submit \
  --py-files dependencies.zip \
  jobs/my_job.py
```

The correct mechanism depends on:

- dependency size
- native dependencies
- deployment platform
- Python version
- reproducibility requirements

---

# 43. `uv` and Reproducible Python Environments

For this roadmap, Python environments are managed with modern tooling such as `uv`.

A conceptual development environment might contain:

```text
Python 3.12+
pyspark
pyarrow
pandas
pytest
```

The important production principle is not the tool itself.

It is:

```text
Declare dependencies
       ↓
Lock versions
       ↓
Build reproducible environment
       ↓
Use compatible environment on driver/executors
```

A deployment should not depend on manually installing random packages on one machine.

---

# 44. "Works on My Machine"

A common Spark deployment failure:

```text
Works locally
      ↓
Fails on cluster
```

Possible reason:

```text
Local environment
    ≠
Executor environment
```

For example:

```text
Local:
Python 3.12
pydantic installed
custom_package installed

Cluster:
Python 3.11
pydantic version mismatch
custom_package missing
```

The solution is not always "install the package manually."

The engineering solution is to establish a reproducible dependency-distribution strategy.

---

# 45. Application Code vs Deployment Configuration

A strong production design separates:

```text
Business Logic
       ≠
Spark Configuration
       ≠
Infrastructure Configuration
```

### Application

```text
read data
transform data
validate data
write data
```

### Deployment

```text
cluster
executor count
executor memory
executor cores
driver resources
deploy mode
Python environment
```

### Infrastructure

```text
machines
containers
network
object storage
identity
secrets
```

This separation improves:

- maintainability
- portability
- testing
- reproducibility
- deployment automation

---

# 46. Development → Testing → Staging → Production

A mature pipeline should be able to move through:

```text
Development
     ↓
Testing
     ↓
Staging
     ↓
Production
```

without rewriting its core business logic for every environment.

A useful pattern is:

```text
Same application
       +
different deployment configuration
```

For example:

```text
Development:
local[*]

Testing:
small Spark environment

Staging:
representative cluster

Production:
production cluster/platform
```

The application logic should remain as stable as practical.

---

# 47. Externalized Configuration

Avoid hardcoding:

```python
MASTER = "spark://production-master:7077"
```

inside business logic.

Prefer deployment-time configuration where appropriate:

```bash
spark-submit \
  --master "$SPARK_MASTER" \
  --deploy-mode "$SPARK_DEPLOY_MODE" \
  jobs/pipeline.py
```

The exact mechanism may be:

- command-line arguments
- environment variables
- scheduler configuration
- platform configuration
- configuration files
- deployment templates

Do not put secrets into source code or ordinary Spark configuration.

---

# 48. Complete Beginner Example

Create:

```text
jobs/spark_session_demo.py
```

with:

```python
from pyspark.sql import SparkSession


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("SparkSessionDemo")
        .getOrCreate()
    )

    data = [
        ("Alice", 30),
        ("Bob", 25),
    ]

    df = spark.createDataFrame(
        data,
        ["name", "age"],
    )

    df.show()

    spark.stop()


if __name__ == "__main__":
    main()
```

## What each part does

### Import

```python
from pyspark.sql import SparkSession
```

Loads the modern PySpark session API.

### Create session

```python
spark = (
    SparkSession.builder
    .appName("SparkSessionDemo")
    .getOrCreate()
)
```

Creates/reuses the application's SparkSession.

### Data

```python
data = [
    ("Alice", 30),
    ("Bob", 25),
]
```

Creates small driver-side Python data.

### DataFrame

```python
df = spark.createDataFrame(
    data,
    ["name", "age"],
)
```

Creates a Spark DataFrame.

The DataFrame API itself is taught deeply in later topics.

### Display

```python
df.show()
```

Requests execution to produce output.

### Stop

```python
spark.stop()
```

Ends the Spark application/session lifecycle.

---

# 49. Running the Beginner Example

Run:

```bash
spark-submit \
  --master local[*] \
  jobs/spark_session_demo.py
```

Conceptually:

```text
Shell
  |
  | spark-submit
  v
Spark application
  |
  v
SparkSession
  |
  v
Local Spark runtime
  |
  v
DataFrame operation
  |
  v
Output
  |
  v
spark.stop()
```

---

# 50. Configuration Example

Consider:

```python
from pyspark.sql import SparkSession


spark = (
    SparkSession.builder
    .appName("ConfigurationExample")
    .config("spark.sql.adaptive.enabled", "true")
    .getOrCreate()
)
```

Here:

```text
spark.sql.adaptive.enabled
```

is being introduced only as an example of a Spark configuration property.

The purpose of this chapter is to teach:

```text
How configuration is supplied and inspected
```

not Adaptive Query Execution itself.

AQE belongs to a later Module 2.14 topic.

---

# 51. Inspecting Configuration

You should learn to inspect what Spark actually sees.

## Application name

```python
print(
    spark.conf.get("spark.app.name")
)
```

## Master

```python
print(
    spark.conf.get("spark.master")
)
```

## SparkContext configuration

```python
for key, value in spark.sparkContext.getConf().getAll():
    print(f"{key}={value}")
```

This is useful during debugging.

---

# 52. Why Configuration Inspection Matters

Suppose you believe:

```text
spark.executor.memory = 8g
```

but the application behaves as if another configuration is active.

Instead of guessing:

```text
"Maybe Spark ignored me."
```

inspect the effective environment.

Production engineering is often:

```text
Hypothesis
   ↓
Inspect
   ↓
Verify
   ↓
Change
   ↓
Measure
```

rather than:

```text
Guess
   ↓
Change five settings
   ↓
Hope
```

---

# 53. Debugging Configuration Problems

## Scenario 1 — Spark Application Does Not Start

### Symptom

`spark-submit` fails immediately.

### Possible causes

- invalid master URL
- missing Spark installation/runtime
- incompatible Java environment
- invalid configuration
- unavailable cluster manager
- malformed dependency configuration

### Investigation

Start with:

```text
1. Exact command
2. Master target
3. Deploy mode
4. Spark version
5. Error message
6. Environment
```

### Fix

Correct the specific deployment/configuration problem rather than changing unrelated settings.

---

# 54. Scenario 2 — Wrong Master Is Being Used

### Symptom

The application runs locally when you expected a cluster.

### Likely cause

The effective `spark.master` is not what you expected.

### Investigation

Inspect:

```python
spark.conf.get("spark.master")
```

and inspect the actual `spark-submit` command/environment.

### Lesson

Never assume the deployment target.

Verify it.

---

# 55. Scenario 3 — Driver Cannot Communicate With the Cluster

### Symptoms

The driver starts but cannot communicate reliably with cluster resources.

### Possible causes

- network reachability
- incorrect hostname
- incorrect port
- firewall/network policy
- deployment topology
- incorrect cluster configuration

### Investigation

Reason from:

```text
Driver
  ↓
network
  ↓
cluster resources
```

Do not immediately increase memory.

This is a deployment/connectivity problem until evidence suggests otherwise.

---

# 56. Scenario 4 — Executors Do Not Start

### Possible causes

- insufficient cluster capacity
- invalid executor resource requests
- scheduler/resource policy
- worker availability
- incompatible deployment configuration

### Investigation

Check:

```text
Requested resources
       ↓
Cluster capacity
       ↓
Cluster manager
       ↓
Worker availability
```

Remember:

> Configuration requests resources; it does not manufacture resources.

---

# 57. Scenario 5 — Dependency Exists on Driver but Not Executors

### Symptom

The application starts, but executor-side Python code fails with an import error.

### Likely cause

The driver environment and executor environment are different.

### Investigation

Compare:

```text
Driver Python version
Driver packages
Executor Python version
Executor packages
```

### Fix

Use a reproducible dependency-distribution mechanism.

---

# 58. Scenario 6 — Works Locally, Fails on Cluster

This is one of the most common Spark engineering situations.

Possible differences include:

```text
Local:
- Python environment
- filesystem
- network
- resources
- Spark configuration

Cluster:
- different Python environment
- object storage
- network policies
- resource limits
- different deployment mode
- different configuration
```

The correct response is not:

> "Spark is broken."

Instead:

```text
Identify environmental difference
        ↓
Reproduce
        ↓
Inspect
        ↓
Fix
```

---

# 59. Scenario 7 — Configured Memory Is Unavailable

Suppose:

```text
spark.executor.memory = 32g
```

but workers cannot provide executors of that size.

The application may remain pending or fail to start depending on the platform.

The key distinction is:

```text
Requested memory
      ≠
Available memory
```

---

# 60. Scenario 8 — Unexpected Configuration

Suppose you configure:

```python
.config("some.setting", "A")
```

but observe:

```text
B
```

Do not guess.

Investigate:

- configuration files
- submission arguments
- deployment environment
- application code
- runtime settings
- property-specific precedence

Then inspect the effective configuration.

---

# 61. Common Beginner Mistakes

## Mistake 1 — Thinking SparkSession Performs the Distributed Work

SparkSession is an entry point.

It does not replace the driver/executor architecture.

---

## Mistake 2 — Confusing SparkSession With the Driver

```text
SparkSession
    ≠
Driver process
```

The session is an API object associated with the Spark application.

---

## Mistake 3 — Confusing Master With Deploy Mode

```text
--master
    =
deployment target

--deploy-mode
    =
driver placement mode
```

---

## Mistake 4 — Assuming `local[*]` Equals a Cluster

It uses one machine.

It does not create a multi-machine cluster.

---

## Mistake 5 — Assuming Configured Resources Are Guaranteed

```text
spark.executor.memory=8g
```

does not create 8 GB of RAM.

The infrastructure must be able to provide it.

---

## Mistake 6 — Hardcoding Production Infrastructure

Avoid:

```python
MASTER = "spark://production-master:7077"
```

inside reusable business logic.

---

## Mistake 7 — Assuming Everything Can Change at Runtime

Some settings are tied to application startup or resource allocation.

---

## Mistake 8 — Assuming Driver and Executor Python Environments Match Automatically

They may not.

Dependency distribution must be designed.

---

## Mistake 9 — Creating Unnecessary SparkSessions

Understand the session lifecycle of your environment.

---

## Mistake 10 — Testing Only in Local Mode

Local testing is valuable, but cluster deployment introduces additional variables.

---

# 62. Hands-On Lab 1 — Create a SparkSession

Create a small application:

```python
from pyspark.sql import SparkSession


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("SessionLab")
        .master("local[*]")
        .getOrCreate()
    )

    print("Application:", spark.conf.get("spark.app.name"))
    print("Master:", spark.conf.get("spark.master"))

    spark.stop()


if __name__ == "__main__":
    main()
```

### Tasks

Record:

```text
Application name:
Master:
Spark version:
```

### Checkpoint

Explain:

> What did `SparkSession.builder` configure, and what did `getOrCreate()` do?

---

# 63. Hands-On Lab 2 — Change Application Name

Run the same program with:

```python
.appName("SessionLabA")
```

Then:

```python
.appName("SessionLabB")
```

Observe how the application identity changes in Spark's application metadata/UI.

### Checkpoint

Why does an application name matter operationally?

---

# 64. Hands-On Lab 3 — Local Parallelism

Run the application using:

```text
local[1]
local[2]
local[4]
local[*]
```

For example:

```bash
spark-submit \
  --master local[2] \
  jobs/session_lab.py
```

Then:

```bash
spark-submit \
  --master local[4] \
  jobs/session_lab.py
```

### Record

```text
Master setting:
Observed behavior:
Available logical processors:
```

Do not conclude that a larger number always makes every workload faster.

---

# 65. Hands-On Lab 4 — Inspect Configuration

Use:

```python
print(
    spark.conf.get("spark.app.name")
)

print(
    spark.conf.get("spark.master")
)
```

Then:

```python
for key, value in spark.sparkContext.getConf().getAll():
    print(f"{key}={value}")
```

### Questions

1. Which settings are visible?
2. Which settings came from the application?
3. Which appear to come from the environment?
4. What would you inspect if a production value surprised you?

---

# 66. Hands-On Lab 5 — Use `spark-submit`

Run:

```bash
spark-submit \
  --master local[*] \
  jobs/session_lab.py
```

Compare that with directly invoking Python:

```bash
python jobs/session_lab.py
```

### Conceptual difference

A Spark application should normally be launched through a Spark-aware deployment mechanism when you need `spark-submit` features such as:

- master selection
- deploy mode
- resource configuration
- dependency distribution
- Spark application packaging

Direct Python execution can still be useful in some local-development contexts, but `spark-submit` makes the Spark deployment intent explicit.

---

# 67. Hands-On Lab 6 — Command-Line Configuration

Run:

```bash
spark-submit \
  --master local[*] \
  --conf spark.sql.shuffle.partitions=10 \
  jobs/session_lab.py
```

Then inspect:

```python
print(
    spark.conf.get("spark.sql.shuffle.partitions")
)
```

The purpose is to learn:

```text
Submission-time configuration
        ↓
Spark application
        ↓
Effective configuration
```

Do not treat this lab as a shuffle-tuning exercise.

---

# 68. Hands-On Lab 7 — Spark Standalone

Using the project's existing Spark Standalone environment, if available:

```text
Spark Master
    |
    +-- Worker
    |
    +-- Worker
```

Submit the same application against the Standalone master.

Conceptually:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  jobs/session_lab.py
```

The exact hostname and port must match your environment.

Observe:

- application registration
- driver location
- executor allocation
- logs
- application lifecycle

Do not modify the project's other files as part of this learning chapter.

---

# 69. Hands-On Lab 8 — Client vs Cluster Mode

Where the Standalone environment supports both modes, run:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  jobs/session_lab.py
```

Then compare with:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  jobs/session_lab.py
```

Observe:

```text
Driver location
Logs
Submission behavior
Application lifecycle
Network dependency
```

### Questions

1. Where did the driver run?
2. Where did you observe the driver logs?
3. What happened when the submission command returned?
4. What dependency did the client-mode driver have on the submitting environment?

---

# 70. Predict → Run → Observe → Explain

For every important Spark deployment experiment, use:

```text
Predict
   ↓
Run
   ↓
Observe
   ↓
Inspect configuration/logs
   ↓
Explain
   ↓
Change one thing
   ↓
Run again
   ↓
Compare
```

This is a better learning method than blindly copying commands.

Before running:

> Predict where the driver will run.

Then verify.

Before running:

> Predict which cluster manager will receive the application.

Then verify.

Before running:

> Predict which Python environment the executor will use.

Then verify.

This builds production debugging instincts.

---

# 71. Production Scenario A — Local Success, Production Failure

A developer runs:

```text
local[*]
```

and the application succeeds.

Production fails.

Possible differences:

```text
Python environment
Spark configuration
filesystem
object storage
network
cluster capacity
deploy mode
dependency distribution
```

### Reasoning process

```text
Local success
     ↓
Identify production differences
     ↓
Classify difference
     ↓
Reproduce
     ↓
Inspect
     ↓
Fix
```

Do not assume the Spark transformation itself is necessarily the problem.

---

# 72. Production Scenario B — Driver on Submission Machine

A long-running production job is launched in client mode.

The submission machine is then unavailable.

### Question

What should you investigate?

### Reasoning

In client mode:

```text
Submission machine
      ↓
Driver
```

Therefore the submission environment can become a critical part of the application's lifecycle.

For scheduled production workloads, deployment architecture should be selected deliberately rather than inherited from interactive development.

---

# 73. Production Scenario C — Executor Import Error

The driver can import:

```python
import my_company_package
```

but an executor fails with:

```text
ModuleNotFoundError
```

### Likely issue

The executor Python environment does not contain the same dependency.

### Investigation

Compare:

```text
Driver Python
Executor Python
Dependency versions
Packaging/distribution
Container/environment
```

### Production lesson

Dependency reproducibility is part of application deployment.

---

# 74. Production Scenario D — Changing Executor Memory at Runtime

A developer writes:

```python
spark.conf.set(
    "spark.executor.memory",
    "16g",
)
```

and expects existing executors to immediately become 16 GB processes.

That expectation is incorrect.

Executor resource allocation is part of deployment/resource management.

The correct question is:

> **Was the required resource configuration supplied at application startup/deployment time?**

---

# 75. Production Scenario E — Hardcoded Production Master

Bad pattern:

```python
spark = (
    SparkSession.builder
    .appName("Pipeline")
    .master("spark://production-master:7077")
    .getOrCreate()
)
```

This couples application source code to one infrastructure environment.

A more portable pattern is to keep the application focused on its logic and supply deployment information externally.

For example:

```bash
spark-submit \
  --master "$SPARK_MASTER" \
  --deploy-mode "$SPARK_DEPLOY_MODE" \
  jobs/pipeline.py
```

This is only a conceptual pattern; the actual deployment system may supply these settings through a scheduler or platform.

---

# 76. Version Awareness

This roadmap targets modern Spark 4.x.

When using tutorials written for older Spark releases, verify:

- API availability
- configuration behaviour
- deployment semantics
- Python support
- Java requirements
- deprecated options
- cluster-manager integration

Do not automatically copy Spark 2.x-era examples into a Spark 4.x project.

A useful engineering habit is:

```text
Tutorial
   ↓
Check Spark version
   ↓
Check official API/configuration
   ↓
Run a small test
   ↓
Adopt
```

---

# 77. What This Chapter Does Not Teach

This chapter intentionally establishes configuration and deployment foundations without duplicating later topics.

It does **not** deeply teach:

- RDD internals
- DataFrame transformations
- Spark SQL
- join optimization
- shuffle optimization
- partition tuning
- data skew
- salting
- caching/persistence
- UDF performance
- Catalyst optimization
- Adaptive Query Execution
- deep Spark UI analysis
- advanced PySpark testing

Those topics belong to later Module 2.14 chapters.

They may be mentioned here only when necessary to explain why a configuration or deployment concept matters.

---

# 78. Topic-Specific Self-Check Questions

## Basic

### 1. What is SparkSession?

**Answer guidance:** The primary modern entry point for working with Spark from PySpark applications.

### 2. What does `getOrCreate()` mean?

**Answer guidance:** Obtain an existing appropriate SparkSession when available or create one when needed.

### 3. What does `--master` mean?

**Answer guidance:** It specifies the Spark deployment target/master.

### 4. What is `SparkConf`?

**Answer guidance:** A configuration object used to supply Spark settings.

### 5. What is `spark.conf`?

**Answer guidance:** An interface for accessing and, where supported, changing Spark runtime configuration.

---

## Intermediate

### 6. What is the relationship between SparkSession and SparkContext?

**Answer guidance:** SparkSession is the modern application entry point and exposes/accesses the underlying SparkContext through `spark.sparkContext`.

### 7. What is the difference between local and Standalone deployment?

**Answer guidance:** Local uses one machine; Standalone uses a Spark-managed multi-machine cluster.

### 8. What is the difference between `--master` and `--deploy-mode`?

**Answer guidance:** `--master` identifies the deployment target; `--deploy-mode` controls where the driver runs relative to the submitting client.

### 9. Why can `local[*]` hide production problems?

**Answer guidance:** It does not reproduce all multi-machine networking, resource, executor, dependency, and cluster-management behaviour.

### 10. Why is configuration inspection important?

**Answer guidance:** It prevents debugging based on assumptions and reveals the effective environment.

---

## Advanced

### 11. Why should infrastructure configuration be externalized?

**Answer guidance:** To keep business logic portable across environments and make deployment reproducible and maintainable.

### 12. Why can driver and executor Python environments differ?

**Answer guidance:** They may run in different processes/hosts/containers with independently supplied environments.

### 13. Why does changing a runtime configuration not necessarily resize executors?

**Answer guidance:** Executor resources are allocated as part of deployment/startup; runtime configuration is not equivalent to resource provisioning.

### 14. Why does `spark.executor.instances=10` not guarantee ten executors?

**Answer guidance:** The cluster manager and infrastructure must have sufficient available resources and permit the requested allocation.

### 15. Why can a job work in client mode but fail in cluster mode?

**Answer guidance:** Driver location, network topology, Python environment, file paths, dependency distribution, and configuration can differ.

---

## Architecture

### 16. How would you deploy the same PySpark application across development and production?

**Answer guidance:** Keep application logic stable and externalize environment-specific deployment/resource configuration.

### 17. Where should a long-running production driver run?

**Answer guidance:** Choose a deployment mode that places the driver in an appropriate cluster-managed environment when the operational model requires independence from the submitting workstation.

### 18. How would you debug a local-success/cluster-failure problem?

**Answer guidance:** Compare effective Spark configuration, Python environments, filesystem/object-storage access, networking, resources, deployment mode, and dependencies.

### 19. How would you distinguish a configuration problem from an infrastructure-capacity problem?

**Answer guidance:** Inspect the effective requested resources and compare them with actual cluster capacity and scheduler/platform constraints.

### 20. How would you make a Spark application portable across environments?

**Answer guidance:** Separate business logic from deployment configuration, externalize environment-specific settings, package dependencies reproducibly, and validate each environment.

---

# 79. Interview Preparation

## Basic

### 1. What is SparkSession?

**Model answer:** SparkSession is the primary modern entry point for PySpark applications. It provides application-facing access to Spark functionality and configuration.

### 2. Why was SparkSession introduced?

**Model answer:** It provides a unified modern entry point for Spark functionality that historically involved multiple context/session entry points.

### 3. What does `getOrCreate()` do?

**Model answer:** It obtains an existing SparkSession when one is available in the relevant application context or creates one when necessary.

### 4. What is SparkConf?

**Model answer:** SparkConf is an object used to supply Spark configuration properties.

### 5. What is `spark.conf`?

**Model answer:** It provides access to Spark runtime configuration, including reading properties and changing supported runtime settings.

### 6. What is `spark-submit`?

**Model answer:** It is Spark's standard application-submission mechanism for specifying deployment, resources, dependencies, and the application to run.

### 7. What does `--master` specify?

**Model answer:** It identifies the Spark deployment target or cluster manager endpoint.

### 8. What does `--deploy-mode` specify?

**Model answer:** It specifies the driver deployment mode, commonly client or cluster.

### 9. Why can local mode be misleading?

**Model answer:** Local mode does not reproduce every multi-machine network, scheduling, resource, executor-failure, and environment characteristic of a cluster.

### 10. How do driver and executor resources differ?

**Model answer:** Driver resources support application coordination and driver-side computation; executor resources support distributed task execution.

---

## Intermediate

### 11. Explain SparkSession versus SparkContext.

**Model answer:** SparkSession is the modern application entry point. SparkContext is a lower-level execution-context abstraction still exposed through the session and present in legacy/lower-level code.

### 12. Explain local versus Standalone.

**Model answer:** Local executes on one machine. Standalone uses Spark's own cluster manager to allocate resources across worker nodes.

### 13. Explain client versus cluster deploy mode.

**Model answer:** Client mode places the driver on the submitting client environment. Cluster mode places the driver inside the cluster-managed environment.

### 14. Why is `--master local[*]` not equivalent to a real cluster?

**Model answer:** It uses one machine and therefore does not reproduce multi-machine network, worker, executor-placement, and cluster-resource behaviour.

### 15. Why should production infrastructure not normally be hardcoded in application logic?

**Model answer:** It couples the code to one environment and makes deployment across development/staging/production harder.

---

## Advanced

### 16. Why can changing `spark.conf` not resize an existing executor?

**Model answer:** Executor resources are established through application deployment/resource allocation. Runtime configuration is not a resource-provisioning mechanism.

### 17. What happens if executor Python dependencies differ from the driver?

**Model answer:** Driver-side code may start successfully while executor-side Python tasks fail with import/version/runtime errors.

### 18. Why inspect effective configuration rather than relying on source code?

**Model answer:** Multiple configuration sources can participate in the final environment, and property-specific behaviour can vary.

### 19. Why can cluster mode reduce dependency on the submitting host?

**Model answer:** The driver is launched in the cluster environment rather than running on the submitting client.

### 20. Why doesn't requesting more executors necessarily produce more executors?

**Model answer:** Allocation depends on cluster capacity, resource policies, scheduler/platform behaviour, and valid deployment configuration.

---

## Production and Architecture

### 21. A production job is scheduled nightly. What deployment mode would you investigate first and why?

**Model answer:** Investigate cluster deploy mode when the operational requirement is to run the driver inside the cluster and reduce dependence on the scheduler/submission host. Validate against the actual platform.

### 22. A job works locally but fails only in cluster mode. What do you compare?

**Model answer:** Compare driver/executor Python environments, filesystem/object-storage access, network topology, Spark configuration, resource limits, deployment mode, dependency packaging, and paths.

### 23. A team has different Spark master URLs for dev, staging, and production. Where should they live?

**Model answer:** In deployment/environment configuration rather than business logic, using the organization's scheduler/platform/configuration mechanism.

### 24. A job requests 64 GB executor memory but remains pending. What do you investigate?

**Model answer:** Compare requested resources with available worker capacity, cluster-manager policies, memory overhead requirements, and deployment configuration.

### 25. How would you make a PySpark application reproducible?

**Model answer:** Pin dependencies, use reproducible Python environments, externalize deployment settings, use versioned application artifacts, and validate the same application across representative environments.

---

# 80. Final Architecture Exercise

## Scenario

> You have a PySpark batch pipeline that works on a developer laptop but now needs to run as a scheduled production workload on a Spark cluster.

Design:

```text
Application
    ↓
SparkSession
    ↓
Configuration
    ↓
spark-submit
    ↓
Cluster Manager
    ↓
Driver
    ↓
Executors
```

You must explain:

- deployment mode
- driver location
- executor resources
- Python environment
- configuration separation
- logging
- failure considerations
- development vs production differences

---

## 80.1 Stop and Design Before Reading the Reference

Write your own architecture first.

Answer:

1. What remains unchanged between local and production?
2. What changes?
3. Where does the driver run?
4. Who allocates executor resources?
5. Where do Python dependencies come from?
6. Where does deployment configuration live?
7. How is the application launched?
8. How are logs collected?
9. What happens if the submission machine disappears?
10. What would you verify before calling the deployment production-ready?

---

## 80.2 Reference Solution

A reasonable conceptual architecture is:

```text
                  Scheduled Production Job
                           |
                           v
                    spark-submit / scheduler
                           |
                           v
                    Cluster Manager
                           |
                  +--------+--------+
                  |                 |
                  v                 v
               Driver          Executor Pool
                  |                 |
                  |          +------+------+------+
                  |          |      |      |      |
                  |          v      v      v      v
                  |       Executor Executor Executor ...
                  |
                  +------ application coordination
```

The deployment should separate:

```text
Application logic
        +
Environment configuration
        +
Infrastructure
```

For example:

```text
Application:
    jobs/daily_pipeline.py

Deployment:
    master
    deploy mode
    driver resources
    executor resources
    Python environment

Infrastructure:
    cluster
    network
    storage
    identity
```

A production design should make the Python environment reproducible for both driver and executor processes.

The deployment should also avoid making the production scheduler dependent on an engineer's interactive laptop.

---

# 81. Knowledge Checkpoint

Before moving to Topic 03, explain these concepts without looking at your notes.

## Core Concepts

- [ ] Spark application
- [ ] SparkSession
- [ ] SparkContext
- [ ] SparkConf
- [ ] `spark.conf`
- [ ] `spark-submit`
- [ ] `--master`
- [ ] `--deploy-mode`

## Deployment

- [ ] local mode
- [ ] Spark Standalone
- [ ] client mode
- [ ] cluster mode

## Resources

- [ ] driver memory
- [ ] driver cores
- [ ] executor memory
- [ ] executor cores
- [ ] executor instances
- [ ] task slots at a conceptual level

## Environment

- [ ] driver Python
- [ ] executor Python
- [ ] dependency distribution
- [ ] reproducible Python environments

## Production

- [ ] configuration sources
- [ ] static vs runtime configuration
- [ ] externalized infrastructure configuration
- [ ] local vs production differences
- [ ] basic configuration debugging

You should be able to explain each in your own words, not just reproduce definitions.

---

# 82. Production Mindset

Throughout this topic, train yourself to ask:

```text
Where does the driver run?

Where do executors run?

Who allocates resources?

Where does configuration come from?

Which configuration is static?

Which configuration is dynamic?

What happens if the driver dies?

What happens if an executor dies?

Are Python dependencies available everywhere?

Does local testing represent production?

How is the application launched?

How are environments separated?

How are infrastructure settings externalized?
```

These questions turn Spark configuration from a collection of flags into an architecture discipline.

---

# 83. Final Summary

The complete relationship is:

```text
SparkSession
     ↓
Configuration
     ↓
Deployment
     ↓
Cluster Manager
     ↓
Driver
     ↓
Executors
```

In plain English:

> Your Python application uses `SparkSession` as its primary Spark entry point. Spark configuration describes how the application should operate. Deployment configuration determines where and how the application runs. A cluster manager allocates the required resources. The driver coordinates the application, while executors perform distributed work.

The critical distinction is:

```text
--master
    ↓
Which deployment target?

--deploy-mode
    ↓
Where does the driver run?
```

And the critical production distinction is:

```text
Application logic
        ≠
Spark configuration
        ≠
Infrastructure configuration
```

A strong Data Engineer does not merely know how to type:

```python
SparkSession.builder.getOrCreate()
```

They understand what environment that session is connecting to, how the application is deployed, where the driver runs, how executors receive resources, how Python dependencies reach those executors, and how the same application can be moved safely from development to production.

---

# 84. Glossary

| Term | Meaning |
|---|---|
| **Spark application** | A complete Spark workload coordinated by a driver and supported by executors. |
| **SparkSession** | The primary modern entry point for working with Spark from PySpark. |
| **SparkContext** | A lower-level Spark execution-context abstraction exposed through SparkSession. |
| **SparkConf** | A configuration object used to supply Spark properties. |
| **Configuration** | Settings that control how a Spark application operates. |
| **Runtime configuration** | Configuration that can be read or, where supported, changed while the application is running. |
| **Deployment configuration** | Settings controlling application placement, resources, and startup. |
| **Local mode** | Spark execution using resources on one machine. |
| **Standalone** | Spark's own cluster-management system. |
| **Cluster manager** | A resource-management environment that allocates resources to Spark applications. |
| **Master** | A deployment target/cluster-manager endpoint; in Standalone, the master is also a specific resource-management component. |
| **Worker** | A machine/resource host in a Spark Standalone cluster. |
| **Driver** | The coordinating process for a Spark application. |
| **Executor** | A process associated with a Spark application that executes distributed tasks. |
| **Deploy mode** | The mode determining where the driver runs relative to the submitting client. |
| **Client mode** | The driver runs in the client/submitting environment. |
| **Cluster mode** | The driver is launched within the cluster-managed environment. |
| **`spark-submit`** | Spark's standard application submission command. |
| **Driver memory** | Memory allocated/configured for the driver process. |
| **Driver cores** | CPU resources configured for the driver. |
| **Executor memory** | Memory allocated/configured for executor processes. |
| **Executor cores** | CPU resources configured for each executor. |
| **Executor instances** | Requested number of executor processes. |
| **Python environment** | The Python runtime and installed dependencies used by driver/executor Python processes. |
| **`spark-defaults.conf`** | A Spark configuration file used to provide default properties. |
| **`spark-env.sh`** | A Spark environment script used for deployment-related environment settings. |
| **`--master`** | `spark-submit` option specifying the deployment target. |
| **`--deploy-mode`** | `spark-submit` option specifying client or cluster driver deployment mode. |
| **`--conf`** | `spark-submit` option for supplying a Spark configuration property. |
| **`--py-files`** | `spark-submit` option for distributing Python files/packages. |
| **`--jars`** | `spark-submit` option for supplying JVM JAR dependencies. |
| **`--packages`** | `spark-submit` option for requesting JVM package dependencies. |

---

# 85. Topic 02 Completion Standard

You are ready for **Topic 03 — RDDs vs DataFrames** when you can explain, without notes:

```text
Spark Application
       ↓
SparkSession
       ↓
Spark Configuration
       ↓
spark-submit
       ↓
--master
       ↓
--deploy-mode
       ↓
Cluster Manager
       ↓
Driver
       ↓
Executors
       ↓
Python Environments
```

You should be able to:

- create a SparkSession
- explain `getOrCreate()`
- explain SparkContext's relationship to SparkSession
- explain SparkConf and `spark.conf`
- inspect effective configuration
- distinguish startup/resource settings from runtime settings
- run local mode
- explain Spark Standalone
- distinguish `--master` from `--deploy-mode`
- explain client mode
- explain cluster mode
- configure basic driver/executor resources
- reason about Python dependency distribution
- diagnose basic deployment failures
- explain why local success does not guarantee production success
- design a clean separation between application logic and deployment configuration

The goal is not to memorize Spark flags.

The goal is to understand:

> **How a PySpark application is created, configured, launched, and deployed as a production Data Engineering workload.**
