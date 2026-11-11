# Practice Questions — Distributed Processing with PySpark

## Overview

This practice set consolidates Module 2.14 across Topics 01–16. It contains exactly 40 applied problems: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced. The questions are designed to train execution reasoning rather than terminology memorization.

### Study Method

1. Read only the problem first.
2. Predict the execution behavior: partitions, tasks, stages, shuffles, executors, memory, and likely physical-plan operators.
3. Attempt the PySpark or architecture solution independently.
4. Run small deterministic experiments where appropriate.
5. Inspect `explain("formatted")` and the Spark UI when the problem calls for evidence.
6. Compare your reasoning with the solution.
7. Explain the trade-offs aloud and record what evidence would confirm your diagnosis.

### Important Runtime Note

Exact task counts, physical plans, timings, shuffle sizes, and UI metrics depend on Spark version, configuration, data distribution, and execution environment. The solutions intentionally do not fabricate runtime results.

# Part I — Basic

Questions 1–10

# Question 1 — Trace the Spark Application

**Difficulty:** Basic

**Topics:** Topic 01 — distributed architecture

## Problem

A PySpark job reads a distributed dataset, filters rows, and finishes with `count()`. The cluster has one driver, two worker nodes, and three executors with four cores each. The input DataFrame has 24 partitions. Explain where planning happens and how the work is divided.

## What You Need to Do

Trace the roles of the driver, cluster manager, executors, cores, partitions, tasks, and the action. Explain what happens if one executor is lost after completing some tasks.

## Solution

### Step 1 — Identify the control plane

The driver owns the Spark application and plans the computation. The cluster manager allocates resources. Executors run tasks and hold intermediate data.

### Step 2 — Map partitions to tasks

The 24 input partitions provide the parallel work. For a stage processing those partitions, Spark creates one task per partition. With twelve executor cores available, work can run in waves rather than all 24 tasks simultaneously.

### Step 3 — Explain the action

`count()` is an action, so it triggers execution of the lazy filter plan. The driver coordinates the resulting job and its stages.

### Step 4 — Explain failure recovery

If an executor is lost, Spark can recompute lost partition results from lineage and retry the affected tasks on surviving resources, subject to the execution state and dependencies.

## Why This Solution Works

Spark separates coordination from data processing. Partitions are the unit of parallel work, while executor cores provide task slots. Lineage is central to fault tolerance because Spark can reconstruct lost partition results instead of requiring every intermediate result to be permanently replicated.

## Key Takeaway

Think from data → partitions → tasks → executor slots, while the driver coordinates rather than processing the entire dataset itself.

# Question 2 — Create a Production-Oriented SparkSession

**Difficulty:** Basic

**Topics:** Topic 02 — SparkSession and configuration

## Problem

You need a small local development session for a PySpark transformation. The pipeline should use UTC timestamps, adaptive execution, and a small shuffle partition count suitable for a laptop. The code will later be submitted with `spark-submit`.

## What You Need to Do

Write a coherent SparkSession builder and explain which settings belong to the application configuration rather than being hard-coded throughout transformation functions.

## Solution

### Step 1 — Create one session

Use a single application-level SparkSession: `SparkSession.builder.appName("customer_transform").master("local[*]")...getOrCreate()`.

### Step 2 — Set development-relevant SQL configuration

For a small local exercise, configure `spark.sql.session.timeZone` to `UTC`, enable `spark.sql.adaptive.enabled`, and choose a deliberately small `spark.sql.shuffle.partitions` value appropriate to the test workload.

### Step 3 — Keep configuration centralized

Transformation functions should accept DataFrames and express business logic. Deployment and environment settings should be supplied through Spark configuration or submission configuration rather than scattered through business logic.

## Why This Solution Works

SparkSession is the application entry point for the structured APIs. Centralizing configuration makes development and production behavior reproducible and lets `spark-submit`, `spark-defaults.conf`, or environment-specific deployment settings control operational concerns.

## Key Takeaway

Keep Spark configuration at the application/deployment boundary; keep transformation code focused on data logic.

# Question 3 — Choose RDD or DataFrame

**Difficulty:** Basic

**Topics:** Topic 03 — RDDs vs DataFrames

## Problem

A team wants to compute revenue by country from structured records containing `country` and `amount`. One developer proposes an RDD `map` followed by `reduceByKey`; another proposes DataFrame expressions and `groupBy`.

## What You Need to Do

Choose an abstraction for the structured workload and explain the execution and optimization implications.

## Solution

### Step 1 — Prefer the DataFrame API

For structured data, express the aggregation with DataFrame operations such as `groupBy("country").agg(F.sum("amount"))`.

### Step 2 — Explain why

A DataFrame has a schema and exposes structured expressions that Spark can analyze and optimize. In PySpark, RDD record-level functions cross into Python more directly and can introduce serialization and Python-worker overhead.

### Step 3 — State when RDDs remain relevant

RDDs can still appear in legacy code, very low-level partition-oriented logic, or APIs that require them. They are not the default choice simply because Python syntax feels familiar.

## Why This Solution Works

The key distinction is not merely API style. DataFrames give Spark structured information that Catalyst can reason about, while arbitrary Python record functions are more opaque and can incur Python/JVM transfer costs.

## Key Takeaway

For structured data transformations, start with DataFrames unless there is a concrete reason to drop to RDD-level control.

# Question 4 — Predict Jobs from Lazy Evaluation

**Difficulty:** Basic

**Topics:** Topic 04 — transformations, actions, lazy evaluation

## Problem

Consider: `filtered = df.filter(F.col("amount") > 100); selected = filtered.select("id", "amount"); selected.count()`. The developer says the filter and select already executed when those assignments ran.

## What You Need to Do

Correct the mental model and explain what triggers execution.

## Solution

### Step 1 — Classify operations

`filter()` and `select()` are transformations. They are lazy, so they construct a logical computation rather than immediately processing all rows.

### Step 2 — Identify the trigger

`count()` is an action. It causes Spark to execute the required computation represented by `selected`.

### Step 3 — Explain the benefit

Because execution is delayed, Spark can build and optimize the plan before processing the data.

## Why This Solution Works

Lazy evaluation separates describing a computation from executing it. This allows Spark to optimize the complete expression graph rather than running every transformation independently.

## Key Takeaway

DataFrame assignments usually build a plan; actions such as `count`, `show`, `collect`, and writes trigger execution.

# Question 5 — Build a Clean DataFrame Transformation

**Difficulty:** Basic

**Topics:** Topic 05 — DataFrame API

## Problem

A DataFrame has `customer_id`, `amount`, and `status`. You need a new `amount_with_tax` column, keep only completed records with positive amounts, and return only three business columns.

## What You Need to Do

Write a chained DataFrame transformation using column expressions, `lit`, `filter`, and `select`.

## Solution

### Step 1 — Derive the value

Use `withColumn("amount_with_tax", F.col("amount") * F.lit(1.18))`. The expression is a Spark Column expression rather than a Python scalar loop.

### Step 2 — Filter rows

Use `filter((F.col("status") == "completed") & (F.col("amount") > 0))`.

### Step 3 — Project the contract

Finish with `select("customer_id", "amount", "amount_with_tax")`.

## Why This Solution Works

Column expressions remain inside Spark's structured expression system. Chaining transformations gives Spark a single lazy plan that can later be optimized and executed across partitions.

## Key Takeaway

Express row logic with Spark column expressions rather than collecting data and looping in Python.

# Question 6 — Use a Temporary View Safely

**Difficulty:** Basic

**Topics:** Topic 06 — Spark SQL and temporary views

## Problem

A DataFrame named `orders` must be queried by an analyst using SQL. The analyst needs rows for one date and wants total revenue by `customer_id`.

## What You Need to Do

Register a temporary view and write the SQL transformation. Explain how this relates to the original DataFrame.

## Solution

### Step 1 — Register the view

Call `orders.createOrReplaceTempView("orders")`.

### Step 2 — Express the query

Use SQL such as `SELECT customer_id, SUM(amount) AS revenue FROM orders WHERE order_date = '2026-10-01' GROUP BY customer_id`.

### Step 3 — Connect SQL to DataFrames

The result is still a Spark DataFrame. SQL and the DataFrame API are two ways of expressing structured Spark computation and are processed through Spark's optimizer.

## Why This Solution Works

A temporary view provides a SQL name for a DataFrame within the Spark session. It does not automatically create a durable table or imply caching.

## Key Takeaway

A temporary view is a query interface over Spark data, not a separate durable storage layer.

# Question 7 — Inspect and Change Partition Count

**Difficulty:** Basic

**Topics:** Topic 08 — partitioning

## Problem

A DataFrame has many more partitions than the local development workload needs. You want to reduce the number of partitions before a small write without performing a full redistribution.

## What You Need to Do

Explain how you would inspect the current partition count and when `coalesce()` is appropriate.

## Solution

### Step 1 — Inspect

In classic PySpark execution, `df.rdd.getNumPartitions()` can be used diagnostically to inspect the current partition count.

### Step 2 — Reduce partitions

`df.coalesce(target)` can merge partitions without a full shuffle in its normal reduction use case.

### Step 3 — State the trade-off

Reducing too aggressively can reduce parallelism and make an upstream or downstream operation effectively single-threaded or under-parallelized.

## Why This Solution Works

Partitions determine execution parallelism. `coalesce` is useful for controlled reduction, but it is not a universal file-compaction strategy and should not be used blindly on large workloads.

## Key Takeaway

Partition count is an execution resource; reduce it only when the resulting parallelism remains appropriate.

# Question 8 — Decide Whether to Cache

**Difficulty:** Basic

**Topics:** Topic 10 — caching and persistence

## Problem

A filtered DataFrame is used by three downstream actions. The filter is expensive, and the same transformed data is reused. Another DataFrame is used only once.

## What You Need to Do

Decide which DataFrame is a caching candidate and explain what `cache()` does and when it materializes data.

## Solution

### Step 1 — Identify reuse

The repeatedly reused DataFrame is a candidate because caching can avoid recomputing the same lineage for later actions.

### Step 2 — Cache lazily

Call `reused = expensive.filter(...).cache()`. `cache()` itself does not immediately process the data.

### Step 3 — Materialize and clean up

The first action computes and populates cached partitions. After the workload is finished, `unpersist()` can release cached data when it is no longer needed.

## Why This Solution Works

Caching trades storage resources for reduced recomputation. It is valuable when reuse is substantial enough to justify memory/disk pressure; caching a one-use DataFrame adds overhead without reuse benefit.

## Key Takeaway

Cache because of measured reuse and recomputation cost, not because caching is automatically faster.

# Question 9 — Write a Small Explicit-Schema Test

**Difficulty:** Basic

**Topics:** Topic 16 — testing PySpark code

## Problem

A transformation converts `amount` into `amount_with_tax`. The test currently creates data using inferred types and compares collected Python lists, causing fragile failures.

## What You Need to Do

Design a small pytest test using an explicit schema and Spark DataFrame equality tools taught in the module.

## Solution

### Step 1 — Build deterministic input

Create a small DataFrame with an explicit `StructType` schema, including representative values and a known numeric type.

### Step 2 — Call a pure transformation

Pass the DataFrame into a `DataFrame → DataFrame` function rather than testing a job entry point that also reads files and creates SparkSession.

### Step 3 — Compare DataFrames

Use `pyspark.testing.assertDataFrameEqual` and, when the contract requires it, `assertSchemaEqual`. Configure order-insensitive comparison or numeric tolerance where appropriate.

## Why This Solution Works

Explicit schemas make tests deterministic and prevent accidental type inference from changing the contract. DataFrame-aware assertions test Spark results without forcing business logic into brittle driver-side list comparisons.

## Key Takeaway

Design transformations as pure DataFrame functions and test their data and schema contracts directly.

# Question 10 — Choose a Safe Read Strategy

**Difficulty:** Basic

**Topics:** Topic 14 — data sources and schemas

## Problem

A production CSV feed occasionally contains malformed records. The pipeline must preserve valid rows, make bad records observable, and avoid silently changing column types through inference.

## What You Need to Do

Describe the read strategy using an explicit schema and an appropriate malformed-record mode.

## Solution

### Step 1 — Define the schema

Supply an explicit schema to `DataFrameReader` rather than relying on production schema inference.

### Step 2 — Choose malformed-record behavior

Use `PERMISSIVE` with an appropriate corrupt-record column when the workflow is designed to retain valid records while quarantining or inspecting malformed input. `FAILFAST` is appropriate when the contract says any malformed record should fail the job.

### Step 3 — Separate ingestion from quarantine

Make the handling policy explicit: valid data proceeds to the pipeline, while malformed rows are captured for investigation rather than silently discarded.

## Why This Solution Works

Input schema and malformed-record behavior are correctness decisions. They determine whether bad data becomes visible, silently disappears, or stops the pipeline.

## Key Takeaway

Production ingestion should make schema and bad-record behavior explicit.

# Part II — Moderate

Questions 11–20

# Question 11 — Reason About Two Actions and a Shuffle

**Difficulty:** Moderate

**Topics:** Topics 04, 07 — lazy execution, jobs, joins, shuffle

## Problem

A pipeline filters a fact DataFrame, joins it with a large dimension on `customer_id`, then calls `count()` and later `write.parquet(...)` on the same uncached result. The team reports two expensive runs.

## What You Need to Do

Explain the likely execution pattern and identify the main reason the same work can be repeated.

## Solution

### Step 1 — Identify the actions

`count()` and the write are separate actions. Each can trigger execution of the required lineage.

### Step 2 — Identify the expensive boundary

A large-large join commonly requires data movement and a shuffle, creating stage boundaries.

### Step 3 — Explain repeated work

Because the result was not persisted, the second action can recompute the filter, join, and associated shuffle.

### Step 4 — Evaluate caching

If the joined result is genuinely reused and fits the resource budget, persistence may reduce recomputation. Verify the trade-off rather than caching automatically.

## Why This Solution Works

Spark's laziness means transformations are not materialized just because a DataFrame variable exists. Multiple actions can independently execute the lineage. A shuffle-heavy join makes that repeated computation particularly expensive.

## Key Takeaway

When several actions consume the same expensive lineage, ask whether persistence can trade storage for avoided recomputation.

# Question 12 — Combine DataFrame API and SQL

**Difficulty:** Moderate

**Topics:** Topics 05, 06 — DataFrame API and Spark SQL

## Problem

A transformation team prefers DataFrame expressions for reusable code, while analysts prefer SQL for a final aggregation. You need to filter and normalize data in Python, then expose it for a SQL aggregation.

## What You Need to Do

Design the handoff without converting to pandas or collecting data to the driver.

## Solution

### Step 1 — Transform with DataFrame expressions

Use `filter`, `withColumn`, casts, and null handling in a pure DataFrame transformation.

### Step 2 — Register a temporary view

Call `clean.createOrReplaceTempView("clean_orders")`.

### Step 3 — Run SQL

Execute the final aggregation with `spark.sql(...)`, returning another DataFrame.

### Step 4 — Preserve distributed execution

Keep the entire workflow inside Spark; do not call `collect()` merely to move from DataFrame API code to SQL.

## Why This Solution Works

DataFrame and SQL expressions converge into Spark's structured execution model. A temporary view changes the interface used to express the next transformation, not the distributed processing engine underneath.

## Key Takeaway

Switch between DataFrame API and Spark SQL at the expression boundary, not by moving data to Python.

# Question 13 — Diagnose a Shuffle-Heavy Join

**Difficulty:** Moderate

**Topics:** Topics 07, 08 — joins, shuffle, partitioning

## Problem

Two large DataFrames are joined on `customer_id`. The Spark UI shows substantial shuffle read/write and long stage duration. Both sides are large enough that broadcasting is not an obvious choice.

## What You Need to Do

Give a systematic first-pass diagnosis and one sensible redesign path.

## Solution

### Step 1 — Inspect the plan

Use `explain("formatted")` and look for `Exchange` and the selected join operator. Confirm whether the join is performing a distributed shuffle.

### Step 2 — Reduce data before the join

Filter unnecessary rows and project only required columns before the join. If one side can be aggregated to the required grain first, do that before joining.

### Step 3 — Evaluate partitioning

If the workload repeatedly joins or aggregates on the same key, consider whether appropriate repartitioning or storage layout can improve downstream work. Do not add repartitions without evidence.

### Step 4 — Measure

Use the Spark UI to compare shuffle bytes, task-time distribution, and stage behavior before and after the change.

## Why This Solution Works

Large-large joins inherently require data movement when matching keys are distributed differently. Reducing input size and unnecessary columns lowers shuffle cost; partitioning can help when it aligns with repeated workload needs.

## Key Takeaway

Treat shuffle as a data-movement problem: reduce bytes first, then consider partitioning and join strategy.

# Question 14 — Broadcast a Small Dimension Carefully

**Difficulty:** Moderate

**Topics:** Topics 07, 12 — broadcast joins and explain plans

## Problem

A 500-million-row fact DataFrame joins to a small customer dimension. The team wants to avoid shuffling the fact table.

## What You Need to Do

Show how to express a broadcast join and explain how to verify that Spark actually planned a broadcast strategy.

## Solution

### Step 1 — Broadcast the small side

Use `fact.join(F.broadcast(dim), "customer_id", "left")` when the dimension is genuinely small enough for the available driver/executor memory constraints.

### Step 2 — Inspect the plan

Call `explain("formatted")` and look for `BroadcastExchange` and `BroadcastHashJoin` or the corresponding plan structure.

### Step 3 — Check operational evidence

Use the SQL and stage views in Spark UI to verify runtime behavior. A hint communicates intent; it does not make an oversized relation safe.

### Step 4 — Avoid blind broadcasting

If the dimension can grow beyond safe memory limits, reassess the strategy rather than permanently forcing broadcast.

## Why This Solution Works

Broadcasting changes the data movement pattern: Spark distributes the small relation rather than shuffling the large side for the join. The physical plan and runtime UI are the evidence that the strategy was selected and executed.

## Key Takeaway

Broadcast is a resource trade-off, not a magic performance switch; verify the plan and memory implications.

# Question 15 — Fix Partitioning Without Destroying Parallelism

**Difficulty:** Moderate

**Topics:** Topics 08, 14 — partitions and output files

## Problem

A daily pipeline writes data partitioned by `event_date`. It creates thousands of tiny files because the upstream DataFrame has many partitions that do not align well with the storage partitioning.

## What You Need to Do

Propose a partition-aware write strategy and explain why `coalesce(1)` is not a general solution.

## Solution

### Step 1 — Understand the two meanings of partition

In-memory execution partitions determine task parallelism; `partitionBy("event_date")` creates on-disk directory layout. They are related but not identical concepts.

### Step 2 — Repartition intentionally

If appropriate for the workload, use `repartition("event_date")` or a justified partition count before the write so rows are distributed by the output key.

### Step 3 — Avoid one-task writes

`coalesce(1)` can collapse parallelism and force a bottleneck. It should not be used as generic compaction for large data.

### Step 4 — Validate file layout

Inspect output file counts and sizes and compare write time. Use `maxRecordsPerFile` where it fits the taught design.

## Why This Solution Works

Output layout is affected by how records are distributed among write tasks. Aligning execution partitioning with the storage partitioning key can make output more manageable, but excessive repartitioning itself costs a shuffle.

## Key Takeaway

Solve small files with deliberate output partitioning and file sizing, not by blindly forcing one file.

# Question 16 — Handle a Skewed Aggregation

**Difficulty:** Moderate

**Topics:** Topics 09, 08 — skew and partitioning

## Problem

A `groupBy("customer_id")` aggregation has one customer representing a very large fraction of the records. One task runs far longer than the others.

## What You Need to Do

Diagnose the symptom and explain two possible remedies covered by the module.

## Solution

### Step 1 — Confirm skew

Compare task durations and partition-level distributions in the Spark UI and inspect key frequencies. A hot key producing a straggler is a classic skew signature.

### Step 2 — Use two-phase aggregation where applicable

Pre-aggregate data locally or by a salted key, then perform a second aggregation to reconstruct the correct customer-level result.

### Step 3 — Consider AQE awareness

AQE can help with skewed joins, but the module explicitly notes that AQE cannot fix every form of skew, such as skew within aggregations or windows. Do not assume AQE solves this aggregation automatically.

## Why This Solution Works

Hash partitioning sends all records for the same grouping key toward the same logical aggregation target. A highly frequent key can therefore create an oversized partition and a straggling task. Two-phase aggregation can distribute partial work before final reconstruction.

## Key Takeaway

A skewed aggregation requires reasoning about key frequency and where the aggregation state is concentrated.

# Question 17 — Replace an Unnecessary Python UDF

**Difficulty:** Moderate

**Topics:** Topics 11, 12 — UDFs and Catalyst

## Problem

A pipeline uses a Python UDF to uppercase a string and then filters on another ordinary column. The plan shows Python execution and the job is slower than expected.

## What You Need to Do

Redesign the transformation and explain why the built-in implementation is preferable.

## Solution

### Step 1 — Replace row-wise Python logic

Use a built-in expression such as `F.upper(F.col("name"))` rather than a Python UDF.

### Step 2 — Filter early

Apply the ordinary column filter before expensive custom logic where semantics allow.

### Step 3 — Inspect the plan

Use `explain("formatted")` to verify that the built-in expression remains visible to Spark's optimizer and that the Python evaluation boundary is gone or reduced.

## Why This Solution Works

Built-in expressions are part of Spark's structured expression system and are visible to Catalyst and code generation. A Python UDF introduces Python worker execution and a serialization boundary and can prevent some optimizations.

## Key Takeaway

Use built-ins whenever the required logic is already expressible in Spark's native expression language.

# Question 18 — Read a Physical Plan

**Difficulty:** Moderate

**Topics:** Topic 12 — Catalyst and explain plans

## Problem

You inspect a formatted plan and see `FileScan`, `Filter`, `Project`, `Exchange`, `SortMergeJoin`, and `HashAggregate`.

## What You Need to Do

Explain what each operator tells you and identify which operator most directly signals a shuffle.

## Solution

### Step 1 — Read the scan

`FileScan` describes the source read. Inspect `PushedFilters`, `PartitionFilters`, and `ReadSchema` to see whether filtering and projection are reaching the scan.

### Step 2 — Read row processing

`Filter` restricts rows and `Project` selects or derives columns.

### Step 3 — Identify data movement

`Exchange` represents a redistribution boundary, commonly a shuffle.

### Step 4 — Read the join and aggregate

`SortMergeJoin` is a distributed join strategy; `HashAggregate` may appear in partial and final forms around aggregation.

## Why This Solution Works

A physical plan is an execution blueprint. Reading it lets you reason about data movement and optimization opportunities before spending time tuning blindly.

## Key Takeaway

When diagnosing Spark performance, read the physical plan before changing configuration.

# Question 19 — Choose a Save Mode for a Daily Partition

**Difficulty:** Moderate

**Topics:** Topic 14 — save modes and idempotent writes

## Problem

A daily job processes only `2026-10-01` and may be retried. A naive `overwrite` can remove unrelated dates, while `append` can duplicate the retried date.

## What You Need to Do

Describe a safer partition-level write design using the concepts taught in the module.

## Solution

### Step 1 — Identify the failure mode

Plain `append` is not automatically idempotent. Static `overwrite` can be destructive if the target scope is broader than the intended date.

### Step 2 — Use partition-aware overwrite

Use dynamic partition overwrite when the sink and configuration support it, so only partitions represented by the output are replaced.

### Step 3 — Define the idempotency contract

The job should produce the same logical contents for the target date on repeated runs. Validate the target partition after the write.

### Step 4 — Keep the boundary explicit

Do not claim that dynamic partition overwrite alone solves every concurrency or object-storage atomicity problem; those are separate reliability concerns.

## Why This Solution Works

Idempotency is a correctness property, not simply a save-mode name. The write scope must match the business partition being recomputed, and retries must replace the intended logical result rather than duplicate it.

## Key Takeaway

Design retries around a precise write scope and verify idempotency; never equate `overwrite` with safe reruns.

# Question 20 — Design a Reusable Spark Test Fixture

**Difficulty:** Moderate

**Topics:** Topic 16 — pytest and SparkSession fixture

## Problem

A test suite creates a new local SparkSession in every test, uses machine-local time zones, and leaves shuffle configuration at production scale. The suite is slow and occasionally inconsistent.

## What You Need to Do

Redesign the fixture using the module's testing practices.

## Solution

### Step 1 — Use a session-scoped fixture

Create one reusable local SparkSession for the test run rather than starting Spark for every test.

### Step 2 — Use test-friendly settings

Use a small shuffle partition count, disable the Spark UI for tests, and set `spark.sql.session.timeZone` to UTC.

### Step 3 — Keep test data tiny and explicit

Create small DataFrames with explicit schemas inside individual tests or helpers.

### Step 4 — Preserve isolation

Do not let one test rely on cached state, temporary views, or mutable global DataFrames left by another test.

## Why This Solution Works

Spark startup is relatively expensive compared with tiny unit tests. A shared test session reduces overhead, while deterministic configuration removes environment-dependent behavior. Small explicit inputs keep tests fast and understandable.

## Key Takeaway

A fast Spark test suite is an engineered environment: one reusable session, tiny deterministic data, explicit schemas, and isolated tests.

# Part III — Hard

Questions 21–30

# Question 21 — Investigate a Single Straggling Task

**Difficulty:** Hard

**Topics:** Topics 09, 15, 08 — skew, UI, partitioning

## Problem

A production join finishes quickly for most tasks, but one task runs dramatically longer. The Stages tab shows uneven task durations and a large difference between median and maximum task time.

## What You Need to Do

Build a diagnosis using evidence from the Spark UI, identify the likely cause, and propose a fix without immediately adding executors.

## Solution

### Step 1 — Localize the bottleneck

Start at the slowest stage and inspect task-time distribution. A single extreme task among otherwise normal tasks is evidence of uneven work rather than simply insufficient cluster-wide capacity.

### Step 2 — Test the skew hypothesis

Inspect the join key distribution and look for a hot key. Compare partition-level input or shuffle metrics if available. If one key accounts for a large share of records, the skew diagnosis is supported.

### Step 3 — Choose a targeted remedy

For a skewed join, consider broadcast if the small side is truly safe to broadcast, AQE skew-join optimization, or selective salting for severe hot keys.

### Step 4 — Measure the change

Compare task-time distribution, shuffle behavior, and total runtime before and after the change. Do not accept 'more executors' as evidence of a root-cause fix.

## Why This Solution Works

Skew creates stragglers because the cluster can have plenty of total capacity while one partition contains disproportionate work. The UI provides evidence about distribution, while key-frequency analysis connects the symptom to the data model.

## Key Takeaway

A straggler is a distribution problem until evidence shows otherwise; diagnose the slow task, not just the cluster.

# Question 22 — Repair a Bad Partitioning Strategy

**Difficulty:** Hard

**Topics:** Topics 08, 14, 15 — partitioning, writes, UI

## Problem

A job reads moderate data, calls `coalesce(1)` early, performs a large aggregation, and then writes partitioned output. The UI shows very long task time in the upstream stage and poor parallelism.

## What You Need to Do

Explain why the design is harmful and redesign it for distributed execution and controlled output files.

## Solution

### Step 1 — Identify the bottleneck

`coalesce(1)` reduces the DataFrame to one partition before the expensive aggregation. That can make the aggregation depend on an extremely narrow execution path and waste available parallelism.

### Step 2 — Remove the early reduction

Let the aggregation operate with an appropriate number of partitions. If redistribution is needed, use a justified `repartition` at the point where it helps the workload.

### Step 3 — Handle output separately

Before writing partitioned output, choose a partition count and key distribution appropriate for the target layout. Use `repartition` by the output key when justified rather than forcing a single file.

### Step 4 — Verify

Use the Stages tab to confirm parallelism improves and inspect output file counts. Measure write time and task distribution.

## Why This Solution Works

Execution partitioning and output file layout solve different problems. Collapsing execution to one partition early sacrifices parallelism, while output shaping should happen near the write boundary with an evidence-based strategy.

## Key Takeaway

Never use output-file convenience as a reason to serialize a large upstream computation.

# Question 23 — Apply Selective Salting to a Hot Join Key

**Difficulty:** Hard

**Topics:** Topics 07, 09 — joins, skew, salting

## Problem

A large fact table joins to a dimension table. `customer_id = 'VIP'` represents a huge fraction of fact rows, creating a single straggling join partition. The dimension is not small enough to broadcast safely.

## What You Need to Do

Design a selective salting strategy and explain how correctness is preserved.

## Solution

### Step 1 — Isolate the hot key

Confirm the hot key from frequency analysis rather than salting every key. Selective salting limits extra work to the skewed portion.

### Step 2 — Add a salt to the hot fact rows

For the hot key, derive a salt value from a bounded range. The fact-side join key becomes `(customer_id, salt)` for salted rows.

### Step 3 — Replicate the matching dimension row

For the hot dimension record, create matching salt values across the same salt range. Normal keys can retain an unsalted path.

### Step 4 — Reconstruct the result

After the join, remove the salt from the logical business key and perform any required final aggregation so the salted fragments represent the same logical customer.

### Step 5 — Validate

Check row counts, duplicate behavior, and business totals for the hot key. Compare task-time distribution before and after.

## Why This Solution Works

The problem is concentration of one key into one logical join target. Salting spreads the hot key across multiple join keys, creating more parallel work. The second-stage reconstruction restores the original business semantics.

## Key Takeaway

Salting is a data-distribution technique: spread a hot key deliberately, then reconstruct the logical result.

# Question 24 — Decide Between Broadcast, AQE, and Salting

**Difficulty:** Hard

**Topics:** Topics 07, 09, 13 — joins, skew, AQE

## Problem

A join initially appears to require a large-large shuffle. After filtering, the dimension becomes small. The fact table also contains one moderately skewed key. The team proposes manually forcing broadcast, salting everything, or disabling AQE.

## What You Need to Do

Reason about the decision order and explain which evidence should guide the design.

## Solution

### Step 1 — Inspect the actual plan and data

Use `explain("formatted")` and runtime statistics to determine the initial strategy and actual relation sizes.

### Step 2 — Let runtime information matter

AQE can switch join strategies at runtime when a relation becomes small enough after earlier stages. It can also coalesce post-shuffle partitions and handle skewed joins in supported cases.

### Step 3 — Consider explicit broadcast only when justified

If the dimension is predictably small and memory-safe, explicit broadcast can communicate intent. But an oversized broadcast can create memory pressure.

### Step 4 — Reserve salting for residual severe skew

If AQE and an appropriate join strategy still leave a severe hot-key problem, selective salting may be justified. Salting every key adds complexity and data volume unnecessarily.

### Step 5 — Measure

Compare final plans, task distributions, shuffle metrics, and memory behavior.

## Why This Solution Works

AQE exists precisely because static estimates do not always reflect runtime reality. Manual tuning should complement evidence rather than fight adaptive behavior. Broadcast changes memory pressure; salting changes data volume and key structure.

## Key Takeaway

Use the least invasive mechanism that solves the measured problem, and verify the final runtime plan.

# Question 25 — Diagnose an Ineffective Cache

**Difficulty:** Hard

**Topics:** Topics 10, 15 — caching and Spark UI

## Problem

A team cached a very large DataFrame after a join. The job became slower, executors show memory pressure, and only one action consumes the cached DataFrame.

## What You Need to Do

Diagnose why caching may hurt and redesign the pipeline.

## Solution

### Step 1 — Check reuse

The first question is whether the cached result is reused enough to amortize materialization and storage cost. With one action, the benefit is usually weak.

### Step 2 — Inspect storage and executors

Use the Storage and Executors tabs to determine cache occupancy, memory pressure, and whether cached data is contributing to eviction or resource contention.

### Step 3 — Remove unnecessary persistence

If there is no meaningful reuse, remove the cache. If reuse is real but the cached relation is unnecessarily large, cache a reduced representation after filtering/projection/aggregation where semantics permit.

### Step 4 — Unpersist intentionally

When reuse ends, call `unpersist()` so storage resources can be released.

## Why This Solution Works

Caching is a resource trade-off. It can prevent recomputation, but it also consumes storage resources and may cause eviction, memory pressure, or slower execution. The UI should support the decision.

## Key Takeaway

A cache is successful only when avoided recomputation outweighs its materialization and resource cost.

# Question 26 — Explain a UDF-Driven Plan Regression

**Difficulty:** Hard

**Topics:** Topics 11, 12, 15 — UDFs, Catalyst, UI

## Problem

A pipeline previously filtered Parquet data efficiently. A refactor wraps a simple string predicate in a Python UDF. After the change, the SQL tab shows Python evaluation and more data is processed than expected.

## What You Need to Do

Explain why the refactor can damage performance and how to redesign and verify it.

## Solution

### Step 1 — Compare plans

Use `explain("formatted")` before and after the change. Inspect the scan's `PushedFilters` and look for Python evaluation.

### Step 2 — Identify optimizer opacity

A Python UDF is not equivalent to a native Spark expression from Catalyst's perspective. Spark may be unable to push the predicate into the file scan through the UDF.

### Step 3 — Rewrite with built-ins

Express the predicate using Spark-native functions such as string predicates or `regexp_*` functions when those semantics match the requirement.

### Step 4 — Verify runtime impact

Check the SQL plan and UI for reduced data movement/input processing and disappearance or reduction of the Python boundary.

## Why This Solution Works

The performance regression is not caused merely by Python syntax. The UDF changes the expression from an optimizer-visible native expression into custom Python computation, which can block pushdown and introduce serialization/Python-worker overhead.

## Key Takeaway

A seemingly small UDF can change both computation cost and the optimizer's ability to reduce data early.

# Question 27 — Interpret an AQE Plan Change

**Difficulty:** Hard

**Topics:** Topics 12, 13 — Catalyst and AQE

## Problem

Before execution, the plan shows a sort-merge join. During execution, the SQL tab indicates an adaptive plan and runtime behavior consistent with a broadcast join. A developer claims Spark ignored the original plan.

## What You Need to Do

Explain what happened and how Catalyst and AQE differ.

## Solution

### Step 1 — Explain Catalyst's role

Catalyst creates and optimizes a plan before execution using the information available at planning time.

### Step 2 — Explain AQE

AQE observes runtime statistics at stage boundaries and can re-optimize the remaining execution plan.

### Step 3 — Explain the join change

If a relation becomes small enough after earlier processing, AQE can switch a join strategy at runtime, such as converting a sort-merge join to a broadcast join when supported.

### Step 4 — Verify

Inspect the adaptive plan and SQL UI metrics rather than assuming the initial plan is the final runtime strategy.

## Why This Solution Works

The initial plan is not necessarily the final execution strategy in an adaptive application. AQE adds runtime feedback to the static optimization process.

## Key Takeaway

Catalyst plans before execution; AQE can revise the remaining plan after runtime statistics become available.

# Question 28 — Design a JDBC Read Without Overloading PostgreSQL

**Difficulty:** Hard

**Topics:** Topics 02, 14 — configuration and JDBC

## Problem

A 50-million-row PostgreSQL table is being read through Spark JDBC. A developer sets `numPartitions=200` to maximize parallelism, causing the source database to experience too many concurrent connections.

## What You Need to Do

Redesign the read strategy and explain what the JDBC partitioning options mean.

## Solution

### Step 1 — Bound source concurrency

Choose a `numPartitions` value based on PostgreSQL capacity, network, and Spark resources rather than treating a large number as automatically faster.

### Step 2 — Define the partitioning inputs

Use `partitionColumn`, `lowerBound`, `upperBound`, and `numPartitions` to describe how Spark should split the JDBC read. The bounds participate in partitioning; they should not be misunderstood as a universal filtering guarantee.

### Step 3 — Tune fetch size carefully

Use `fetchsize` as a tuning parameter after validating database behavior and memory usage.

### Step 4 — Measure both systems

Observe Spark runtime and source-database connection/load behavior. The fastest Spark configuration is not useful if it overloads the source system.

## Why This Solution Works

JDBC is a distributed boundary between Spark and a transactional database. Parallelism creates concurrent source work, so the database is part of the performance budget. Spark-side parallelism must be bounded by source capacity.

## Key Takeaway

Distributed extraction is a shared-resource problem: tune Spark and the source database together.

# Question 29 — Debug a Driver OOM vs Executor OOM

**Difficulty:** Hard

**Topics:** Topics 01, 02, 15 — architecture, resources, UI

## Problem

Two failures occur. Run A fails after `collect()` on a large result. Run B fails because one executor processes a very large skewed partition. The team wants to increase driver memory for both.

## What You Need to Do

Diagnose the two failures and explain why the same resource change is inappropriate.

## Solution

### Step 1 — Diagnose Run A

`collect()` moves all returned records to the driver. A large result can exhaust driver memory. The first fix is usually to redesign the result flow so large data is not collected.

### Step 2 — Diagnose Run B

A skewed or oversized partition is processed by an executor task, so the pressure is on executor-side memory/resources. Inspect task distribution and executor failure evidence.

### Step 3 — Match the fix to the architecture

Driver memory settings affect the driver; executor memory and overhead affect executor-side resources. But simply increasing memory can hide rather than solve a skew or data-volume design problem.

### Step 4 — Verify with evidence

Use Spark UI, logs, task metrics, and the failing operation to distinguish the failure domain.

## Why This Solution Works

Spark has distinct driver and executor processes with different responsibilities. Resource tuning must follow the process that actually failed, while correctness/performance redesign should address the underlying workload.

## Key Takeaway

Always identify which Spark process owns the failing work before changing memory settings.

# Question 30 — Build a Plan Regression Test

**Difficulty:** Hard

**Topics:** Topics 12, 16 — explain plans and testing

## Problem

A critical fact-to-dimension query is expected to use a broadcast join and a pushed filter. A future refactor could silently change the plan without changing the query result.

## What You Need to Do

Design a lightweight regression test that checks these performance-sensitive properties without asserting fabricated full-plan text.

## Solution

### Step 1 — Execute a representative query on small deterministic data

Keep the dataset tiny so the test remains fast and stable.

### Step 2 — Capture the relevant plan

Use `explain` or an appropriate plan representation and inspect for the expected physical characteristics.

### Step 3 — Assert targeted invariants

Check for the relevant broadcast operator and evidence of pushed filtering rather than snapshotting every line of a full plan.

### Step 4 — Keep the test version-aware

Plan text can vary across Spark versions. Assert the important contract, document why it matters, and avoid brittle formatting dependencies.

## Why This Solution Works

Performance regressions can occur even when functional outputs remain correct. Targeted plan assertions create a guardrail while avoiding brittle tests tied to every optimizer detail.

## Key Takeaway

Test performance contracts at the level of important plan properties, not every character of a generated plan.

# Part IV — Advanced

Questions 31–40

# Question 31 — End-to-End Diagnosis of a Slow Skewed Pipeline

**Difficulty:** Advanced

**Topics:** Topics 07, 08, 09, 13, 15 — joins, partitioning, skew, AQE, UI

## Problem

A production pipeline joins a very large fact table with a dimension, aggregates by customer, and writes partitioned output. After growth in data volume, the job becomes slow. The UI shows one very long join task, large shuffle read, and many small output files. AQE is enabled.

## What You Need to Do

Produce an investigation and remediation plan that distinguishes the different bottlenecks instead of applying one global tuning change.

## Solution

### Step 1 — Separate the symptoms

The long join task suggests skew; large shuffle read suggests expensive data movement; many small output files suggest an output partitioning problem. AQE being enabled does not mean every issue is automatically fixed.

### Step 2 — Investigate the join

Inspect the physical plan and runtime task distribution. Determine whether the dimension can safely broadcast. If not, evaluate AQE skew handling and selective salting for a severe hot key.

### Step 3 — Investigate the aggregation

Check whether the customer aggregation itself is skewed. If a hot customer dominates the aggregation, use an appropriate two-phase strategy rather than assuming join optimization solves the aggregation.

### Step 4 — Redesign output separately

Near the write boundary, use deliberate repartitioning by the output key and appropriate file sizing rather than `coalesce(1)`. Validate the number and size of output files.

### Step 5 — Measure each change independently

Record stage/task distribution, shuffle metrics, spill where relevant, and output file counts. Change one major variable at a time.

## Why This Solution Works

The pipeline contains multiple independent dimensions of performance: join movement, key skew, aggregation concentration, and storage layout. AQE can improve some runtime decisions but cannot repair poor data layout or every form of skew.

## Key Takeaway

Production Spark tuning is a chain of evidence: isolate the bottleneck, choose a targeted intervention, and measure its effect.

# Question 32 — Redesign a Python UDF Pipeline

**Difficulty:** Advanced

**Topics:** Topics 05, 11, 12, 15 — DataFrame API, UDFs, Catalyst, UI

## Problem

A pipeline processes hundreds of millions of rows. It uses a Python UDF to normalize strings, another Python UDF for a date-derived value, and then filters the result. The SQL tab shows Python execution and the scan reads more data than expected.

## What You Need to Do

Redesign the pipeline while preserving the business logic and explain how you would prove the redesign improved it.

## Solution

### Step 1 — Classify each UDF

Determine whether each operation is already expressible with Spark built-ins. String normalization and date logic commonly belong in native expressions when supported.

### Step 2 — Move cheap filters earlier

Apply optimizer-visible filters before custom computation whenever semantics allow.

### Step 3 — Replace native-capable UDFs

Use `F` expressions, casts, conditional expressions, date functions, and string functions where they match the required semantics.

### Step 4 — Keep unavoidable custom logic narrow

If custom Python logic remains necessary, minimize the number of rows and columns crossing the Python boundary. Consider pandas/Arrow-oriented approaches only where their execution model fits the problem.

### Step 5 — Compare evidence

Inspect formatted plans for Python evaluation and pushdown, then use Spark UI/SQL metrics to compare runtime behavior. Do not claim a speedup without measuring it.

## Why This Solution Works

The best optimization is often removing unnecessary custom execution rather than tuning resources. Native expressions remain visible to Catalyst and can participate in code generation and pushdown opportunities, while Python UDFs add a Python-worker boundary and reduce optimizer visibility.

## Key Takeaway

First optimize the computation model; only then tune resources.

# Question 33 — Design a Partitioning Strategy for Repeated Workloads

**Difficulty:** Advanced

**Topics:** Topics 08, 12, 13, 14 — partitioning, plans, AQE, storage

## Problem

A lakehouse pipeline repeatedly joins and aggregates large datasets by `customer_id`, then writes curated data partitioned by `event_date`. The team proposes partitioning the files by `customer_id` because it is the join key.

## What You Need to Do

Evaluate the proposal and design a storage/execution strategy that distinguishes query keys from physical directory partitioning.

## Solution

### Step 1 — Separate directory partitioning from execution partitioning

`partitionBy` controls on-disk directory layout. It should be chosen for selective, manageable storage filtering rather than simply because a column is used for joins.

### Step 2 — Consider execution partitioning

For a specific operation, `repartition("customer_id")` can redistribute rows by the join/aggregation key, but that is an execution cost and should be justified.

### Step 3 — Consider bucketing where appropriate

The module teaches bucketing with `bucketBy` and `sortBy` as a way to pre-organize tables for repeated joins/aggregations, subject to matching bucket counts and compatibility limitations.

### Step 4 — Let AQE handle runtime variability

AQE can coalesce post-shuffle partitions and adapt supported join strategies, reducing the need for rigid manual tuning.

### Step 5 — Validate the physical plan

Use `explain("formatted")` to determine whether the chosen storage/execution design actually reduces the relevant exchanges; do not assume that a partitioning declaration eliminates shuffles.

## Why This Solution Works

Physical storage layout, execution partitioning, and bucketing solve different problems. Choosing a high-cardinality business key as a directory partition can create operationally poor layouts, while bucketing may be appropriate for repeated keyed workloads under its constraints.

## Key Takeaway

Do not confuse the column that drives a query with the column that should define your storage directories.

# Question 34 — Build an Idempotent Object-Storage Write

**Difficulty:** Advanced

**Topics:** Topics 08, 14, 15 — partitioning, writes, operations

## Problem

A daily Spark pipeline writes Parquet to S3-compatible object storage. Retries can occur, and a failed run can leave partial files. The job currently uses `append`, which duplicates data on retry.

## What You Need to Do

Design a safer logical write contract using the taught Spark mechanisms and explain what they do not guarantee.

## Solution

### Step 1 — Define the logical unit of replacement

For a daily pipeline, the date partition is the natural rerun scope. The job should produce the complete intended contents for that partition.

### Step 2 — Use dynamic partition overwrite where supported

Configure the write so partitions represented by the current output replace those logical partitions rather than blindly appending another copy.

### Step 3 — Control output partitioning

Repartition appropriately near the write boundary to avoid excessive small files.

### Step 4 — Validate after writing

Check row counts, partition presence, and data-quality expectations. Treat write success and data correctness as separate checks.

### Step 5 — State the boundary

Dynamic partition overwrite improves logical rerun behavior but does not by itself provide full transactional atomicity for plain object-store files or solve concurrent-reader consistency. The module explicitly treats those limitations as motivation for lakehouse table formats.

## Why This Solution Works

Idempotency concerns the logical result of retries; object-store atomicity concerns how physical files become visible and consistent. These are related but distinct reliability properties.

## Key Takeaway

A robust write design must reason separately about idempotency, file layout, validation, and atomicity.

# Question 35 — Engineer a Production Spark Test Pyramid

**Difficulty:** Advanced

**Topics:** Topics 05, 06, 11, 14, 16 — transformations, SQL, UDFs, I/O, testing

## Problem

A team has a large PySpark job with DataFrame transformations, SQL views, UDFs, and MinIO I/O. Its only test is an end-to-end test that takes too long for CI.

## What You Need to Do

Design a layered test strategy that catches correctness and important performance regressions while keeping the fast suite small.

## Solution

### Step 1 — Unit-test pure transformations

Refactor business logic into `DataFrame → DataFrame` functions and test them with small explicit-schema DataFrames using DataFrame equality and schema assertions.

### Step 2 — Test edge semantics

Include NULL, empty, duplicate, timezone-boundary, and ANSI-error cases where they affect the transformation contract.

### Step 3 — Test SQL and UDFs locally

Register temporary views for SQL transformations and test UDF behavior directly as Python logic plus inside Spark where execution integration matters.

### Step 4 — Add focused integration tests

Use local files and a MinIO/S3-compatible environment for representative I/O behavior, and validate outputs with data-quality checks where appropriate.

### Step 5 — Add plan regression tests

For critical performance contracts, assert targeted properties such as broadcast join selection or pushed filters.

### Step 6 — Keep CI fast

Use a session-scoped Spark fixture, tiny data, parallel test processes where safe, and separate slower integration tests from the fast unit suite.

## Why This Solution Works

Most business logic can be validated without full I/O or large data. Integration tests then cover system boundaries, while plan tests protect important execution contracts. This structure makes failures easier to localize and keeps CI feedback fast.

## Key Takeaway

Testing architecture should mirror code architecture: pure logic gets fast tests; boundaries get focused integration tests; critical plans get targeted regression checks.

# Question 36 — Diagnose a Production Failure from Spark UI Evidence

**Difficulty:** Advanced

**Topics:** Topics 01, 02, 09, 10, 11, 15 — architecture, resources, skew, cache, UDF, UI

## Problem

A job has three symptoms: executors show high memory pressure, one stage has a few extreme task durations, and the SQL plan contains a Python UDF after a large join. The team proposes increasing executor memory and adding more executors.

## What You Need to Do

Create an evidence-driven debugging sequence and explain which hypotheses you would test before changing cluster size.

## Solution

### Step 1 — Start at the slowest stage

Use the Stages tab to inspect task-time distribution, shuffle read/write, spill, and GC. Extreme task durations suggest skew or unusually large partitions.

### Step 2 — Inspect the SQL plan

Look for the join strategy, `Exchange`, Python evaluation, and whether filters/projections reach the scan. Determine whether the UDF is forcing expensive Python processing over a large row set.

### Step 3 — Test the skew hypothesis

Inspect key frequencies and task distribution. If one key is hot, evaluate broadcast, AQE skew handling, or selective salting depending on the join and data sizes.

### Step 4 — Test the memory hypothesis

Inspect Executors and Storage. Determine whether caching is consuming resources or whether large partitions/Python workers are driving memory overhead.

### Step 5 — Redesign before scaling

Replace native-capable UDFs, reduce data before the join, remove unnecessary cache, or address skew as supported by evidence.

### Step 6 — Measure

Only after targeted fixes should you compare executor sizing. Record the evidence and measured result in a performance investigation report.

## Why This Solution Works

Adding resources can increase cost without fixing skew, Python overhead, excessive data movement, or cache pressure. Spark UI and physical plans connect symptoms to causes and make the remediation testable.

## Key Takeaway

Production debugging is hypothesis-driven: UI evidence → plan evidence → targeted change → measurement.

# Question 37 — Design a Robust Adaptive Join Pipeline

**Difficulty:** Advanced

**Topics:** Topics 07, 09, 12, 13, 15 — joins, skew, Catalyst, AQE, UI

## Problem

A fact-to-dimension pipeline has variable daily data. On some days the dimension becomes small after filtering; on other days it is larger. The fact table also develops skew around a small set of keys. The team has hard-coded a broadcast hint and a fixed high shuffle partition count.

## What You Need to Do

Design a more robust strategy that uses Catalyst and AQE while retaining explicit controls only where justified.

## Solution

### Step 1 — Remove assumptions that are no longer stable

A hard-coded broadcast strategy may become unsafe when the dimension grows. A fixed high shuffle count may create excessive tiny tasks on smaller days.

### Step 2 — Make the plan optimizer-friendly

Filter and project before the join so Catalyst has the best information and the smallest possible inputs.

### Step 3 — Enable and observe AQE

AQE can use runtime statistics to switch join strategies, coalesce post-shuffle partitions, and optimize supported skewed joins.

### Step 4 — Handle residual hot keys

If a particular join key remains severely skewed, evaluate selective salting rather than salting all records.

### Step 5 — Verify on multiple data shapes

Run small, normal, and skewed scenarios. Compare initial/final plans, task distributions, shuffle metrics, and memory behavior in the UI.

## Why This Solution Works

Production data distributions change. Static hints and rigid partition counts can become incorrect as the workload changes, while AQE uses runtime information to adapt supported parts of execution. It still cannot replace good data modeling and targeted skew handling.

## Key Takeaway

Design for workload variability: optimizer-friendly transformations plus AQE, with manual interventions only where evidence shows they are needed.

# Question 38 — Create a Complete Performance Investigation

**Difficulty:** Advanced

**Topics:** Topics 04, 07, 08, 09, 10, 11, 12, 13, 14, 15 — full-module synthesis

## Problem

A gold pipeline performs filtering, two joins, an aggregation, a reusable intermediate branch, and a partitioned object-store write. It recently slowed down after data growth. The only facts available initially are that total runtime increased and output file count also increased.

## What You Need to Do

Write the investigation workflow you would follow from first principles through remediation, explicitly naming the evidence you would gather and the trade-offs you would evaluate.

## Solution

### Step 1 — Reproduce and establish a baseline

Run the same workload under controlled conditions. Record wall time and relevant Spark UI metrics, but do not invent numbers.

### Step 2 — Map execution

Use the Jobs and Stages tabs to find the slowest job/stage and inspect task-time distribution, shuffle read/write, spill, and GC.

### Step 3 — Read the plan

Use `explain("formatted")` to identify scans, filters, projections, exchanges, join strategies, aggregates, and Python evaluation. Look for missing pushdown or unnecessary exchanges.

### Step 4 — Investigate distribution

Check partition counts and key distributions. Determine whether skew, too many/few partitions, or an oversized partition explains stragglers.

### Step 5 — Investigate reuse

If a branch is reused, evaluate cache/persist. Inspect Storage and Executors to ensure the cache is not creating memory pressure.

### Step 6 — Investigate custom computation

Replace built-in-capable Python UDFs and reduce Python-worker work. Verify the plan after the change.

### Step 7 — Investigate AQE

Compare adaptive behavior, initial/final plans, partition coalescing, runtime join switching, and supported skew handling.

### Step 8 — Fix storage layout

Address the increased output file count with deliberate output partitioning and file sizing. Avoid `coalesce(1)` as a generic fix.

### Step 9 — Validate correctness and tests

Run the existing DataFrame, schema, edge-case, integration, and plan regression tests. Ensure performance changes did not alter business results.

### Step 10 — Measure one change at a time

Document symptom, evidence, hypothesis, fix, trade-off, and measured result. Keep a rollback path for production.

## Why This Solution Works

Spark performance is emergent from data distribution, execution planning, resource allocation, computation model, and storage layout. A systematic workflow prevents optimizing the wrong layer and provides evidence for every production change.

## Key Takeaway

The production Spark skill is not memorizing knobs; it is building an evidence chain from symptom to execution mechanism to measured intervention.

# Question 39 — Design a Fault-Tolerant, Testable PySpark Application

**Difficulty:** Advanced

**Topics:** Topics 01, 02, 04, 14, 15, 16 — architecture, deployment, lineage, I/O, debugging, testing

## Problem

You must build a daily PySpark application that reads source data, performs pure transformations, writes a date-partitioned result, and runs in both local development and a cluster. It must be testable and diagnosable after failures.

## What You Need to Do

Describe the application architecture, execution boundaries, testing strategy, and operational controls using only the module concepts.

## Solution

### Step 1 — Separate entry point from business logic

Create a thin job entry point responsible for arguments, SparkSession creation, reads, writes, and orchestration. Put business transformations into pure `DataFrame → DataFrame` functions.

### Step 2 — Make configuration environment-aware

Use Spark configuration and submission settings for local versus cluster execution, UTC session time zone, resources, and Python dependency distribution. Avoid embedding secrets in code.

### Step 3 — Design the transformation path

Keep transformations lazy and structured. Use built-ins where possible, inspect plans for major queries, and avoid driver-side collection of large data.

### Step 4 — Design the write contract

Use explicit schemas on ingestion, deliberate malformed-record handling, date-partitioned output, and an idempotent partition overwrite strategy when supported. Control output partitioning to avoid small files.

### Step 5 — Build tests

Use a session-scoped local fixture, explicit test schemas, DataFrame/schema equality, edge-case tests, SQL/UDF tests, focused integration tests, and targeted plan regressions.

### Step 6 — Build the debugging path

Use Spark UI tabs, event logs/History Server, driver/executor logs, and a slowest-stage → hypothesis → one-change → measure workflow.

### Step 7 — Explain fault tolerance correctly

Spark can recompute lost partition results from lineage and retry tasks, but durable output correctness and object-store write semantics remain separate application concerns.

## Why This Solution Works

A production Spark application is a system, not a single transformation script. Separating computation, configuration, I/O, tests, and operations makes failures easier to isolate and allows the same business logic to run across environments.

## Key Takeaway

Production readiness comes from architecture: pure transformations, thin entry points, explicit contracts, observable execution, and layered tests.

# Question 40 — Prove a Performance Fix Without Losing Correctness

**Difficulty:** Advanced

**Topics:** Topics 05, 09, 12, 13, 15, 16 — transformations, skew, plans, AQE, UI, testing

## Problem

A team replaces a slow join implementation with a combination of pre-filtering, a native DataFrame expression, and AQE. The new run appears faster in one sample, but the team has not proved that the result is correct or that the improvement generalizes.

## What You Need to Do

Design a validation protocol that proves both correctness and performance improvement before the change is promoted.

## Solution

### Step 1 — Lock down functional behavior

Run the old and new transformations against the same small deterministic inputs, including NULLs, duplicates, hot keys, empty input, and representative boundary cases. Use DataFrame and schema equality with appropriate ordering/tolerance semantics.

### Step 2 — Inspect the plans

Compare `explain("formatted")` output and identify the intended differences: reduced data before the join, native expressions, relevant exchanges, and adaptive behavior. Avoid asserting irrelevant plan text.

### Step 3 — Exercise representative data shapes

Test normal, small, and skewed distributions. A performance fix that only works for one distribution is not a robust production improvement.

### Step 4 — Collect UI evidence

Compare the slowest stage, task-time distribution, shuffle read/write, spill, GC, and relevant SQL operator metrics. Do not invent benchmark values; record the values observed in the environment.

### Step 5 — Add regression protection

Turn important correctness and plan properties into automated tests so later refactors cannot silently remove the optimization.

### Step 6 — Document the trade-off

Record what improved, what resource or complexity cost was introduced, which data assumptions the optimization depends on, and when the team should revisit it.

## Why This Solution Works

A Spark optimization is production-ready only when it preserves the data contract and improves the measured workload without depending on accidental data shape. Combining deterministic tests, plan inspection, runtime evidence, and regression tests provides that evidence chain.

## Key Takeaway

A performance optimization is not proven by one faster run; prove correctness, mechanism, workload robustness, and repeatability.

## Final Coverage Summary

| Topic | Questions |
|---|---|
| Topic 01 — Distributed computing | Q1, Q21, Q29, Q35, Q40 |
| Topic 02 — SparkSession, configuration, deployment | Q2, Q28, Q40 |
| Topic 03 — RDDs vs DataFrames | Q3 |
| Topic 04 — transformations, actions, lazy evaluation | Q4, Q11, Q40 |
| Topic 05 — DataFrame API | Q5, Q20, Q32, Q40 |
| Topic 06 — Spark SQL and temporary views | Q6, Q12, Q20, Q34, Q39 |
| Topic 07 — joins, shuffle, broadcast | Q13, Q14, Q21, Q23, Q24, Q31, Q34, Q38, Q39 |
| Topic 08 — partitioning, repartition, coalesce | Q7, Q15, Q22, Q31, Q33, Q36, Q39 |
| Topic 09 — data skew and salting | Q16, Q21, Q23, Q24, Q31, Q38, Q39 |
| Topic 10 — caching and persistence | Q8, Q11, Q25, Q35, Q39 |
| Topic 11 — UDFs, pandas UDFs, built-ins | Q17, Q26, Q32, Q35, Q38 |
| Topic 12 — Catalyst and explain plans | Q18, Q14, Q26, Q27, Q32, Q33, Q38, Q39 |
| Topic 13 — AQE | Q24, Q27, Q31, Q33, Q38, Q39 |
| Topic 14 — data sources, save modes, bucketing | Q10, Q19, Q22, Q28, Q33, Q36, Q40 |
| Topic 15 — Spark UI and debugging | Q21, Q22, Q25, Q26, Q28, Q29, Q31, Q32, Q35, Q38, Q39, Q40 |
| Topic 16 — testing PySpark code | Q9, Q20, Q30, Q37, Q40 |

## Requirement Validation

- Exactly **40** numbered questions.
- **10 Basic:** Q1–Q10.
- **10 Moderate:** Q11–Q20.
- **10 Hard:** Q21–Q30.
- **10 Advanced:** Q31–Q40.
- Every question contains **Problem**, **What You Need to Do**, **Solution**, **Why This Solution Works**, and **Key Takeaway**.
- At least 8 questions are debugging-oriented.
- At least 8 questions explicitly require performance reasoning.
- At least 4 questions involve PySpark testing.
- Multiple questions combine 4+ major topics, especially Q31, Q35, Q38, Q39, and Q40.
- Topics 01–16 are represented in the coverage table.

## Learning Loop

`Read → Predict → Implement → Explain Plan → Run Small → Inspect → Debug → Optimize → Measure → Explain`
