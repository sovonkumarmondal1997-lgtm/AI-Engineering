# AWS Data Engineering Deep Dive — Interview Practice

## Purpose

This interview bank prepares the learner for Data Engineer, Senior Data Engineer, AWS Data Engineer, Cloud Data Engineer, Data Platform Engineer, Analytics Engineer, and production architecture interviews based specifically on the AWS Data Engineering Deep Dive curriculum. It emphasizes explanation, engineering judgment, architecture, troubleshooting, security, observability, cost, governance, reliability, performance, and service-selection trade-offs rather than certification-style memorization.

## How to Use This Interview Bank

Use each question as a simulated interview conversation:

1. Read only the **Interview Question** and **Problem / Scenario** first.
2. Answer aloud before reading the model answer.
3. Explain **what, why, how, trade-offs, failure modes, and production implications**.
4. For troubleshooting questions, state the evidence you would collect before proposing a fix.
5. For architecture questions, clarify requirements before naming services.
6. Use the **Strong Interview Answer** section to practice concise senior-level communication.
7. Use the follow-ups to practice defending decisions under interviewer challenge.

## Difficulty Progression

- **Basic:** Understand and explain.
- **Moderate:** Apply and combine.
- **Hard:** Troubleshoot and optimize.
- **Advanced:** Architect and defend.

## Interview Answer Pattern

A strong answer should move from requirements and evidence to a justified decision, then cover operational consequences:

**Question → Scenario → Expected Approach → Solution → Explanation → Production Considerations → Concise Interview Answer → Follow-ups**

---

# Level 1 — Basic Interview Questions

## Question 01 — Choose Athena or Redshift for an S3 analytics workload

**Difficulty:** Basic

**Primary Topics:** AWS Data Services, Athena, Redshift, S3

### Interview Question

An analytics team has several terabytes of curated Parquet data in S3 and runs ad-hoc queries with highly variable demand. Would you start with Athena or Redshift, and why?

### Problem / Scenario

The team wants SQL access without committing to a continuously provisioned warehouse. Some workloads may later become repeated, performance-sensitive reporting.

### What the Interviewer Is Evaluating

- Workload characterization
- Serverless query trade-offs
- S3 lake integration
- Cost and performance reasoning

### Expected Approach

1. Clarify query frequency, concurrency, latency, data size, and workload stability.
2. Use Athena when direct S3 querying and variable demand dominate.
3. Consider Redshift when repeated warehouse-style workloads, predictable performance, or serving requirements justify it.
4. Define a migration/serving path rather than choosing by service name.

### Solution / Model Answer

Athena is a strong starting point when the data already lives in S3 and the workload is ad-hoc or intermittent. It queries the lake directly through the catalog and avoids managing a persistent warehouse. I would optimize the S3 data as Parquet, use appropriate partitioning or partition projection, and control scanned bytes. I would move or serve workloads through Redshift when concurrency, predictable latency, repeated transformations, or warehouse-specific capabilities become the dominant requirements.

### How to Solve the Problem

#### Step 1 — Characterize

The key decision variables are query pattern, concurrency, latency, data layout, and operational requirements.

#### Step 2 — Optimize the lake

Use columnar files, sensible partitioning, and query pruning so Athena scans only what is needed.

#### Step 3 — Define the boundary

If the workload becomes consistently warehouse-oriented, evaluate Redshift rather than forcing Athena to solve every serving problem.

### Example

```sql
SELECT customer_segment, SUM(revenue)
FROM curated.orders
WHERE order_date >= DATE '2026-01-01'
GROUP BY customer_segment;
```

### Why This Is the Correct Approach

A service decision should follow workload characteristics rather than familiarity with a particular AWS service.

### Production Considerations

- **Security:** Use least-privilege access to S3 and catalog resources.
- **Cost:** Measure bytes scanned and query patterns before scaling the platform.
- **Performance:** Optimize file layout and pruning; use Redshift when sustained warehouse performance is justified.
- **Observability:** Track query failures, latency, and scanned data.

### Strong Interview Answer

> I’d start with Athena for an S3-native, ad-hoc workload because it minimizes infrastructure management. I’d optimize the lake layout and measure scanned bytes and latency. If the workload becomes high-concurrency, predictable, or warehouse-centric, I’d evaluate Redshift and make that trade-off explicit.

### Common Weak Answers

- Choosing Redshift simply because the dataset is large.
- Ignoring file format and partitioning.
- Ignoring concurrency and latency requirements.

### Follow-Up Questions an Interviewer May Ask

1. What would make you move the workload to Redshift?
2. How would you reduce Athena cost?
3. How would Glue Catalog fit into this architecture?

## Question 02 — Explain the role of the Glue Data Catalog

**Difficulty:** Basic

**Primary Topics:** Glue Data Catalog, S3, Athena, Lake Formation

### Interview Question

An S3 data lake contains raw, curated, and Iceberg data. Explain what the Glue Data Catalog contributes and what it does not provide by itself.

### Problem / Scenario

The analytics team needs a shared metadata layer for tables and partitions and assumes that registering a table automatically controls every user's access.

### What the Interviewer Is Evaluating

- Metadata versus authorization
- Table/schema/partition concepts
- Athena and Glue integration
- Governance boundaries

### Expected Approach

1. Describe the catalog as metadata about datasets.
2. Explain databases, tables, schemas, and partitions.
3. Explain how query engines use catalog metadata.
4. Separate discovery/cataloging from authorization and governance.

### Solution / Model Answer

The Glue Data Catalog provides a centralized metadata layer describing datasets, including tables, schemas, and partition information. Athena can use that metadata to query S3 data, and Glue ETL can use it as part of processing. The catalog is not automatically equivalent to authorization. Lake Formation and IAM/resource policies can govern access, while DataZone can add discovery, business metadata, and data-product workflows.

### How to Solve the Problem

#### Step 1 — Identify metadata

Determine what physical data the table represents and what schema/partition information is registered.

#### Step 2 — Use the metadata

Athena and Glue can resolve datasets through the catalog instead of hard-coding every physical location.

#### Step 3 — Separate concerns

Cataloging answers what and where; authorization and governance answer who may access it and under what conditions.

### Example

```text
Glue Catalog table -> S3/Iceberg location
Athena/Glue -> Catalog metadata
Lake Formation/IAM -> access control
```

### Why This Is the Correct Approach

The catalog is a metadata control plane; treating it as the entire governance model causes architectural and security confusion.

### Production Considerations

- **Security:** Do not assume catalog visibility grants data access.
- **Reliability:** Keep schema and partition metadata consistent with physical data.
- **Governance:** Use Lake Formation/DataZone where the curriculum calls for authorization and discovery.

### Strong Interview Answer

> The Glue Data Catalog is the shared metadata layer for data assets. It describes schemas, tables, partitions, and locations so services such as Athena and Glue can discover and process data. I would not equate catalog metadata with authorization; access control is a separate concern.

### Common Weak Answers

- Saying Glue Catalog is the data itself.
- Saying a catalog entry automatically grants access.
- Using crawlers blindly for every schema-management problem.

### Follow-Up Questions an Interviewer May Ask

1. How would you handle schema evolution?
2. Where would Lake Formation fit?
3. How would Iceberg change catalog considerations?

## Question 03 — Why use S3 Tables for an Iceberg workload?

**Difficulty:** Basic

**Primary Topics:** S3 Tables, Apache Iceberg, S3

### Interview Question

A team wants managed table-oriented storage for an Iceberg lakehouse and wants less operational work around table maintenance. Explain when S3 Tables is a reasonable choice.

### Problem / Scenario

The team is comparing general-purpose S3 plus Iceberg with S3 Tables and wants to understand the operational boundary.

### What the Interviewer Is Evaluating

- Iceberg table concepts
- Managed maintenance
- Storage-model trade-offs
- Operational reasoning

### Expected Approach

1. Clarify whether the workload is table-centric and Iceberg-oriented.
2. Compare general-purpose S3 object management with table-oriented capabilities.
3. Evaluate managed maintenance and integration requirements.
4. Check governance, access, compatibility, and cost before adoption.

### Solution / Model Answer

S3 Tables is relevant when the workload is explicitly table-oriented and uses Apache Iceberg, and when managed table maintenance can reduce operational burden. I would evaluate the table-bucket/namespace/table model, maintenance behavior such as compaction and snapshot management, and how the chosen AWS analytics services integrate. I would still compare it with general-purpose S3 plus Iceberg based on requirements rather than assuming one is universally better.

### How to Solve the Problem

#### Step 1 — Clarify table requirements

Identify whether Iceberg tables and managed maintenance are central to the workload.

#### Step 2 — Compare operations

Assess who owns compaction, snapshot, and unreferenced-file maintenance.

#### Step 3 — Validate integrations

Confirm that the required analytics, catalog, security, and governance path is supported.

### Example

```text
S3 Tables
  -> table bucket
  -> namespace
  -> Iceberg table
  -> managed maintenance
```

### Why This Is the Correct Approach

The value is operational and architectural fit, not simply a different S3 storage class.

### Production Considerations

- **Security:** Apply the appropriate S3/table access controls and encryption.
- **Cost:** Compare storage and request/maintenance economics with general-purpose S3.
- **Operations:** Define ownership of maintenance, lifecycle, and recovery.

### Strong Interview Answer

> I’d choose S3 Tables when an Iceberg table workload benefits from the table-oriented model and managed maintenance. I’d still validate integrations, governance, operational ownership, and cost against general-purpose S3 plus Iceberg.

### Common Weak Answers

- Treating S3 Tables as a generic replacement for every S3 bucket.
- Ignoring Iceberg semantics.
- Ignoring maintenance and governance requirements.

### Follow-Up Questions an Interviewer May Ask

1. What maintenance does the platform reduce?
2. When would general-purpose S3 plus Iceberg be preferable?
3. How would you validate the integration path?

## Question 04 — When should you use Glue ETL rather than another processing option?

**Difficulty:** Basic

**Primary Topics:** Glue ETL, Spark, DynamicFrames, DataFrames, EMR

### Interview Question

A batch pipeline reads Parquet from S3, transforms it with Spark, and writes curated output. Explain why Glue ETL could be a good fit and what you would evaluate before productionizing it.

### Problem / Scenario

The pipeline is scheduled and mostly managed Spark ETL; the team wants to avoid unnecessary cluster operations.

### What the Interviewer Is Evaluating

- Managed ETL reasoning
- Spark processing model
- Incremental processing
- Operational trade-offs

### Expected Approach

1. Characterize the transformation and runtime requirements.
2. Use managed Glue ETL when serverless Spark ETL fits the workload.
3. Consider bookmarks/incremental state, workers, Auto Scaling, and execution class where relevant.
4. Compare with EMR when deeper runtime or infrastructure control is required.

### Solution / Model Answer

Glue ETL is a strong fit for managed Spark-based batch transformations when the team wants AWS-managed execution rather than operating clusters. I would consider DataFrames versus DynamicFrames, incremental processing and bookmarks, worker sizing, Auto Scaling, and output formats such as Parquet or Iceberg. If the workload needs more runtime or infrastructure control, EMR may be a better choice.

### How to Solve the Problem

#### Step 1 — Characterize

Determine whether the job is ordinary managed ETL or needs specialized runtime control.

#### Step 2 — Design incrementality

Use bookmarks or explicit state/watermarks where supported by the workload.

#### Step 3 — Tune and observe

Size workers, inspect Spark behavior, and monitor execution rather than guessing capacity.

### Example

```python
from awsglue.context import GlueContext
# GlueContext is typically used with the managed Glue Spark runtime.
```

### Why This Is the Correct Approach

Glue is valuable when it removes cluster-operations work without removing the Spark processing model needed by the pipeline.

### Production Considerations

- **Reliability:** Make incremental processing and reruns idempotent.
- **Performance:** Use appropriate workers and investigate skew, shuffle, and file layout.
- **Cost:** Evaluate execution class, runtime, and worker utilization.
- **Data Quality:** Use Glue Data Quality where validation gates are part of the pipeline.

### Strong Interview Answer

> I’d use Glue ETL when the workload is a good fit for managed Spark. I’d explicitly design incremental processing, worker sizing, data quality, observability, and rerun behavior. I’d move toward EMR when the workload requires materially more runtime or infrastructure control.

### Common Weak Answers

- Assuming Glue is always cheaper than EMR.
- Using bookmarks as a substitute for idempotency.
- Ignoring Spark execution characteristics.

### Follow-Up Questions an Interviewer May Ask

1. How would you troubleshoot a Glue job that doubled in runtime?
2. When would EMR be a better fit?
3. How would you quarantine bad records?

## Question 05 — Reduce Athena cost without changing the business result

**Difficulty:** Basic

**Primary Topics:** Athena, Parquet, partitioning, partition projection, CTAS

### Interview Question

Athena queries over a large S3 dataset are returning correct results but scanning far more data than expected. What would you inspect first?

### Problem / Scenario

Analysts use SQL against a curated lake. Query latency and cost have increased as data volume has grown.

### What the Interviewer Is Evaluating

- Query-cost reasoning
- Data layout
- Partition pruning
- Columnar storage

### Expected Approach

1. Inspect query scan metrics and SQL predicates.
2. Check file format and compression.
3. Check partitioning/pruning or partition projection where appropriate.
4. Use CTAS or other layout improvements to create optimized analytical datasets.
5. Validate with before/after measurements.

### Solution / Model Answer

I would start with evidence: bytes scanned, query plan, SQL predicates, and the physical layout. I would verify that data is stored in an efficient columnar format such as Parquet, that filters enable partition pruning, and that partition projection is appropriate for the dataset. For repeatedly queried data, I could use CTAS to create a better analytical layout. Then I would compare scanned bytes and latency before and after.

### How to Solve the Problem

#### Step 1 — Measure

Use Athena execution information to establish the cost driver.

#### Step 2 — Inspect layout

Check Parquet, compression, file sizes, partitions, and projection configuration.

#### Step 3 — Rewrite strategically

Use CTAS or other supported transformations when the physical layout is the bottleneck.

### Example

```sql
CREATE TABLE curated_orders
WITH (format='PARQUET') AS
SELECT * FROM raw_orders
WHERE order_date >= DATE '2026-01-01';
```

### Why This Is the Correct Approach

Athena cost is strongly influenced by how much data a query must scan; better physical layout and pruning reduce unnecessary work.

### Production Considerations

- **Cost:** Measure scanned data rather than relying on intuition.
- **Performance:** Use pruning and efficient file layout.
- **Reliability:** Validate that the optimized dataset preserves semantics.
- **Observability:** Track recurring query behavior and cost trends.

### Strong Interview Answer

> I’d first quantify bytes scanned, then inspect SQL predicates and the S3 layout. I’d optimize Parquet, partition pruning or projection, and use CTAS when a curated analytical layout is justified. I’d validate the improvement with measured scan volume and latency.

### Common Weak Answers

- Adding partitions blindly.
- Assuming Athena cost is fixed regardless of data scanned.
- Ignoring query predicates and file layout.

### Follow-Up Questions an Interviewer May Ask

1. When is partition projection preferable?
2. What would EXPLAIN tell you?
3. How would you handle an Iceberg table instead?

## Question 06 — Explain the difference between Redshift Serverless and provisioned Redshift

**Difficulty:** Basic

**Primary Topics:** Redshift, Redshift Serverless, RA3, workload management

### Interview Question

A team needs a warehouse for recurring analytical workloads but wants to avoid choosing the wrong operating model. How would you compare Redshift Serverless with provisioned Redshift?

### Problem / Scenario

The organization expects analytical SQL workloads but is uncertain about predictability, capacity control, and operational ownership.

### What the Interviewer Is Evaluating

- Warehouse deployment models
- Workload characteristics
- Capacity and operations
- Cost/performance trade-offs

### Expected Approach

1. Clarify workload predictability, concurrency, and operational requirements.
2. Explain Serverless as a managed capacity model.
3. Explain provisioned clusters as a more explicit capacity/control model.
4. Compare performance, scaling, operational effort, and cost based on workload evidence.

### Solution / Model Answer

Redshift Serverless is useful when the team wants a managed warehouse experience with capacity managed through the Serverless model. Provisioned Redshift provides explicit cluster-oriented capacity and more direct infrastructure control. I would choose based on workload predictability, concurrency, performance requirements, operational preferences, and measured economics rather than assuming Serverless is always cheaper or provisioned is always faster.

### How to Solve the Problem

#### Step 1 — Characterize workload

Determine whether demand is intermittent, predictable, spiky, or continuously high.

#### Step 2 — Compare controls

Evaluate how much capacity and workload-management control the team needs.

#### Step 3 — Validate economics

Measure actual workload behavior and cost rather than relying on a generic claim.

### Example

```text
Intermittent / variable analytics -> consider Serverless
Predictable sustained workload / explicit capacity control -> consider provisioned
```

### Why This Is the Correct Approach

The correct Redshift model depends on workload shape and required operational control.

### Production Considerations

- **Cost:** Model sustained and burst demand.
- **Performance:** Evaluate concurrency and latency requirements.
- **Operations:** Choose the operating model that matches the team's ability and need to manage capacity.

### Strong Interview Answer

> I’d compare Serverless and provisioned Redshift by workload shape, concurrency, latency, capacity control, and operational burden. I would validate the choice with representative workloads rather than a blanket cost assumption.

### Common Weak Answers

- Choosing solely on the word 'serverless'.
- Ignoring concurrency.
- Ignoring workload management requirements.

### Follow-Up Questions an Interviewer May Ask

1. Where does Spectrum fit?
2. How would you optimize distribution and sort keys?
3. When would Athena be enough?

## Question 07 — Kinesis Data Streams versus Firehose

**Difficulty:** Basic

**Primary Topics:** Kinesis Data Streams, Firehose, S3

### Interview Question

An application emits events continuously. Explain when you would choose Kinesis Data Streams versus Firehose, and whether they can be used together.

### Problem / Scenario

The team needs both a durable streaming path and delivery into an S3 analytics lake.

### What the Interviewer Is Evaluating

- Streaming service roles
- Consumer control
- Managed delivery
- Architecture composition

### Expected Approach

1. Determine whether custom consumers/replay/control are required.
2. Use Data Streams when applications need stream semantics and consumer control.
3. Use Firehose for managed delivery to supported destinations.
4. Combine them when a stream is the source and managed delivery is a useful sink path.

### Solution / Model Answer

Kinesis Data Streams is the stream-oriented service when producers and consumers need explicit control over records, shards, retention, partition keys, and consumer behavior. Firehose is focused on managed delivery, buffering, transformations, and destination-oriented ingestion. They can be combined: Data Streams can provide the streaming source while Firehose handles downstream delivery where supported.

### How to Solve the Problem

#### Step 1 — Identify control needs

Ask whether the team needs custom consumers, replay, or explicit stream behavior.

#### Step 2 — Choose delivery model

Use Firehose when managed buffering and destination delivery reduce operational work.

#### Step 3 — Compose

Use both when stream processing and managed delivery solve different parts of the architecture.

### Example

```text
Producers -> Kinesis Data Streams -> consumers
                       \-> delivery path where appropriate
```

### Why This Is the Correct Approach

Streams and Firehose solve related but distinct problems; confusing them leads to poor architecture decisions.

### Production Considerations

- **Reliability:** Design retries, partial failures, and downstream idempotency.
- **Performance:** Watch shard utilization and consumer lag for Streams.
- **Cost:** Match provisioned/on-demand and delivery architecture to throughput.

### Strong Interview Answer

> I’d use Data Streams when I need stream semantics and consumer control, and Firehose when managed delivery is the main requirement. They are complementary rather than mutually exclusive.

### Common Weak Answers

- Calling Firehose a general-purpose stream-processing platform.
- Ignoring partition keys and hot shards.
- Assuming Streams and Firehose have identical semantics.

### Follow-Up Questions an Interviewer May Ask

1. How would you investigate iterator age?
2. When would MSK be preferable?
3. How would you replay data?

## Question 08 — Why choose EMR Serverless, EMR on EC2, or EMR on EKS?

**Difficulty:** Basic

**Primary Topics:** EMR, EMR Serverless, EMR on EC2, EMR on EKS, Spark

### Interview Question

A Spark workload needs to run in AWS. Explain how you would choose among the three EMR deployment models covered in the curriculum.

### Problem / Scenario

The platform team wants to balance operational simplicity, runtime control, and integration with existing Kubernetes infrastructure.

### What the Interviewer Is Evaluating

- EMR deployment-model trade-offs
- Spark workload characteristics
- Operational control
- Cost and scaling

### Expected Approach

1. Clarify workload duration, customization, and infrastructure requirements.
2. Choose Serverless for managed, workload-oriented execution when suitable.
3. Choose EC2 when cluster and infrastructure control are important.
4. Choose EKS when Kubernetes integration is a first-class requirement.
5. Validate security, logging, scaling, and cost.

### Solution / Model Answer

EMR Serverless minimizes cluster operations and is attractive for workload-oriented Spark processing. EMR on EC2 gives more explicit control over cluster capacity, node configuration, and infrastructure. EMR on EKS is appropriate when Kubernetes is already a strategic compute control plane and the organization wants Spark integrated with it. The decision should follow workload and operational requirements.

### How to Solve the Problem

#### Step 1 — Assess control

Determine how much control is required over nodes, bootstrap/configuration, and runtime.

#### Step 2 — Assess platform context

Check whether Kubernetes is already an operational dependency.

#### Step 3 — Assess operations

Balance management effort against flexibility and scaling behavior.

### Example

```text
Managed simplicity -> EMR Serverless
Infrastructure control -> EMR on EC2
Kubernetes integration -> EMR on EKS
```

### Why This Is the Correct Approach

EMR is a family of deployment choices; the architecture should reflect operational constraints rather than treating EMR as one homogeneous runtime.

### Production Considerations

- **Security:** Use IAM roles, encryption, network controls, and appropriate service integrations.
- **Cost:** Consider idle capacity and auto-termination versus managed execution.
- **Operations:** Choose the model the team can reliably operate and observe.

### Strong Interview Answer

> I’d choose EMR Serverless for managed workload execution, EMR on EC2 when infrastructure control matters, and EMR on EKS when Kubernetes integration is a real requirement. I’d make the decision using workload customization, scaling, security, operations, and cost.

### Common Weak Answers

- Choosing based only on familiarity.
- Ignoring Kubernetes operational overhead.
- Ignoring cluster lifecycle costs.

### Follow-Up Questions an Interviewer May Ask

1. How does Glue compare with EMR?
2. How would you integrate Iceberg and the Glue Catalog?
3. How would you troubleshoot a slow Spark job?

## Question 09 — What is the role of Step Functions in a data pipeline?

**Difficulty:** Basic

**Primary Topics:** Step Functions, Glue, EventBridge, orchestration

### Interview Question

A pipeline must run a Glue transformation, validate the result, and execute downstream work only when the preceding steps succeed. Explain how you would orchestrate it.

### Problem / Scenario

The pipeline should have retries and explicit failure handling rather than relying on shell scripts or implicit dependencies.

### What the Interviewer Is Evaluating

- Workflow orchestration
- State-machine thinking
- Retries/Catch
- AWS service integration

### Expected Approach

1. Represent the workflow as explicit states.
2. Use Task states for work and Choice/Parallel/Map where needed.
3. Add Retry and Catch policies based on failure classes.
4. Emit useful execution evidence for operations.

### Solution / Model Answer

Step Functions provides explicit workflow orchestration. I would model the Glue job and downstream validation as states, use retries for transient failures, Catch for terminal handling, and Choice for conditional paths. For parallel work I would use Parallel or Map when appropriate. EventBridge can trigger the workflow, while MWAA is a different choice when Airflow's DAG ecosystem is the stronger requirement.

### How to Solve the Problem

#### Step 1 — Model dependencies

Translate the pipeline into explicit states and transitions.

#### Step 2 — Classify failures

Retry transient failures and route non-retryable failures to controlled error handling.

#### Step 3 — Observe

Make state transitions and execution outcomes visible to operators.

### Example

```json
{
  "StartAt": "RunGlue",
  "States": {
    "RunGlue": {"Type": "Task", "Resource": "arn:aws:states:::glue:startJobRun.sync", "End": true}
  }
}
```

### Why This Is the Correct Approach

Explicit orchestration makes dependencies, retries, failure handling, and operational state visible.

### Production Considerations

- **Reliability:** Use bounded retries, Catch paths, and idempotent tasks.
- **Observability:** Track execution status and failed states.
- **Cost:** Avoid unnecessary retries and uncontrolled parallelism.

### Strong Interview Answer

> I’d model the pipeline as a Step Functions state machine, use service integrations for Glue, classify transient versus terminal failures, and make the workflow observable. I’d choose MWAA instead when the workload genuinely benefits from Airflow's DAG ecosystem.

### Common Weak Answers

- Using retries without bounds.
- Putting all logic inside the state machine.
- Confusing event routing with workflow orchestration.

### Follow-Up Questions an Interviewer May Ask

1. When would you choose MWAA?
2. How would you use EventBridge?
3. How would you handle a partial Map failure?

## Question 10 — Explain the purpose of DMS CDC

**Difficulty:** Basic

**Primary Topics:** AWS DMS, CDC, PostgreSQL WAL, replication slots

### Interview Question

A PostgreSQL source must continuously replicate changes into an AWS analytics environment. Explain what DMS CDC does and what you would monitor.

### Problem / Scenario

The team wants full load plus ongoing changes and has observed replication lag.

### What the Interviewer Is Evaluating

- Full load versus CDC
- Logical replication concepts
- Replication lag
- Operational monitoring

### Expected Approach

1. Separate initial full load from CDC.
2. Explain that PostgreSQL CDC depends on logical replication/WAL behavior.
3. Identify replication lag and WAL retention as operational concerns.
4. Define validation and recovery procedures.

### Solution / Model Answer

DMS can perform a full load followed by CDC so the target is initially populated and then receives source changes. For PostgreSQL, logical replication and WAL-related settings are important. Replication slots can retain WAL while changes await consumption, so I would monitor CDC lag and source WAL growth and have an operational plan for stalled tasks.

### How to Solve the Problem

#### Step 1 — Baseline

Complete and validate the initial full load.

#### Step 2 — Understand CDC

Track the source's logical replication/WAL path and DMS task state.

#### Step 3 — Control lag

Measure lag, investigate target bottlenecks, and prevent unbounded WAL retention.

### Example

```text
PostgreSQL -> WAL/logical replication -> DMS CDC -> target
```

### Why This Is the Correct Approach

CDC is not just a configuration checkbox; source log retention, replication state, target throughput, and validation determine operational safety.

### Production Considerations

- **Reliability:** Make CDC restart and recovery behavior explicit.
- **Observability:** Monitor task state, latency/lag, and source WAL behavior.
- **Data Quality:** Validate counts, keys, ordering assumptions, and target consistency.

### Strong Interview Answer

> I’d treat DMS as a full-load-plus-CDC system. For PostgreSQL I’d pay particular attention to logical replication, WAL retention, replication slots, task lag, and target throughput, then validate that the target remains consistent.

### Common Weak Answers

- Saying CDC means zero latency.
- Ignoring PostgreSQL WAL growth.
- Assuming DMS automatically proves target correctness.

### Follow-Up Questions an Interviewer May Ask

1. What causes WAL growth?
2. How would you validate CDC completeness?
3. When would zero-ETL or Debezium be preferable?


---

# Level 2 — Moderate Interview Questions

## Question 11 — Design an S3 → Glue → Athena incremental lakehouse

**Difficulty:** Moderate

**Primary Topics:** S3, Glue Catalog, Glue ETL, Athena, Iceberg

### Interview Question

Design an incremental analytics path for e-commerce orders landing in S3. The business wants curated data available to Athena without reprocessing the entire history every day.

### Problem / Scenario

Orders arrive as files throughout the day. The curated layer should support reliable reruns and analyst queries.

### What the Interviewer Is Evaluating

- Incremental architecture
- Catalog strategy
- Iceberg/Parquet
- Idempotency and reruns

### Expected Approach

1. Define raw and curated zones.
2. Choose incremental state using bookmarks or explicit watermarks as appropriate.
3. Write curated Parquet/Iceberg data with a stable table design.
4. Expose metadata through Glue Catalog and query with Athena.
5. Add quality and observability gates.

### Solution / Model Answer

A practical design is S3 landing → Glue Catalog metadata → Glue ETL incremental processing → curated Parquet or Iceberg → Athena. For append-oriented files, bookmarks may help; for more complex change semantics, explicit watermarks or Iceberg MERGE patterns may be more appropriate. The design must make reruns idempotent and keep metadata aligned with the physical data.

### How to Solve the Problem

#### Step 1 — Ingest

Land immutable source data in S3 with deterministic paths and metadata.

#### Step 2 — Process

Use Glue incremental state and transform only the required scope.

#### Step 3 — Publish

Write curated tables and register/maintain metadata for Athena.

#### Step 4 — Validate

Run data-quality checks and publish only valid output.

### Example

```text
Sources -> S3 raw -> Glue ETL -> Curated Parquet/Iceberg -> Glue Catalog -> Athena
```

### Why This Is the Correct Approach

Incremental processing is an architectural property: state, idempotency, output semantics, and validation matter as much as the scheduler.

### Production Considerations

- **Security:** Use role-based access and encryption.
- **Reliability:** Make reruns safe and isolate bad batches.
- **Performance:** Use columnar storage and pruning.
- **Data Quality:** Gate publication on critical quality checks.
- **Observability:** Track job state, records processed, and failures.

### Strong Interview Answer

> I’d use S3 for durable landing, Glue for incremental transformation and metadata integration, and Athena for serverless querying. The key production concerns are deterministic incremental state, idempotent writes, data quality, and measurable query cost.

### Common Weak Answers

- Relying on a crawler for all incrementality.
- Reprocessing all history every run.
- Ignoring duplicate/replay behavior.

### Follow-Up Questions an Interviewer May Ask

1. When would you use Iceberg instead of plain Parquet?
2. How would you backfill one month?
3. Where would Lake Formation fit?

## Question 12 — Build a Glue Data Quality quarantine pattern

**Difficulty:** Moderate

**Primary Topics:** Glue ETL, Glue Data Quality, DQDL, S3, Athena

### Interview Question

A daily customer dataset contains malformed records and invalid business fields. Design a Glue Data Quality pattern that prevents bad data from silently entering the curated layer.

### Problem / Scenario

The team wants both automated validation and an operational way to investigate failures.

### What the Interviewer Is Evaluating

- Data-quality architecture
- DQ rules
- Quality gates
- Quarantine design

### Expected Approach

1. Define critical versus non-critical rules.
2. Run data quality before publication.
3. Separate valid output from rejected/quarantined records.
4. Persist quality results and operational evidence.
5. Define remediation and rerun behavior.

### Solution / Model Answer

I would run Glue Data Quality checks against the incoming dataset before publishing curated output. Critical rules should act as quality gates. Failed records or batches should be quarantined rather than silently dropped, with enough metadata to reproduce and remediate the issue. The pipeline should fail or route to an exception path when critical thresholds are violated.

### How to Solve the Problem

#### Step 1 — Define rules

Translate business expectations into measurable quality rules.

#### Step 2 — Gate publication

Do not publish curated data when critical checks fail.

#### Step 3 — Quarantine

Persist invalid records and reason codes for investigation.

#### Step 4 — Recover

Fix the source or transformation and rerun safely.

### Example

```text
Raw -> Glue ETL -> DQ checks -> {curated, quarantine}
```

### Why This Is the Correct Approach

A quality system must create an explicit decision boundary between trusted and untrusted data.

### Production Considerations

- **Data Quality:** Use critical rules as gates and preserve failure evidence.
- **Reliability:** Make reruns safe and avoid silently losing records.
- **Observability:** Record rule outcomes and batch-level quality trends.

### Strong Interview Answer

> I’d treat Data Quality as a publication gate, not just a report. Valid data proceeds to curated storage; invalid data is quarantined with evidence and a remediation path.

### Common Weak Answers

- Logging a failed rule but publishing the data anyway.
- Dropping bad records without evidence.
- Using only schema checks for business-quality problems.

### Follow-Up Questions an Interviewer May Ask

1. How would you choose rule thresholds?
2. How would you backfill after remediation?
3. How would Step Functions orchestrate the quality gate?

## Question 13 — Use Athena CTAS to create an optimized analytical dataset

**Difficulty:** Moderate

**Primary Topics:** Athena, CTAS, Parquet, partitioning, S3

### Interview Question

Analysts repeatedly query a large raw dataset but only use a subset of columns and a stable date range. How would you use CTAS to improve the analytical workload?

### Problem / Scenario

The raw dataset is wide and stored in a less efficient layout. The team wants to materialize a curated query-friendly representation.

### What the Interviewer Is Evaluating

- CTAS
- Physical data layout
- Projection/pruning
- Cost optimization

### Expected Approach

1. Identify frequently queried columns and predicates.
2. Create a columnar curated dataset with CTAS.
3. Choose partitioning that supports actual access patterns.
4. Validate scan volume and result equivalence.
5. Manage lifecycle and repeatability.

### Solution / Model Answer

CTAS can materialize a query result into a new table, making it useful for creating curated Parquet datasets with a better schema and layout. I would select only necessary columns, use partitions based on real query predicates, and validate the resulting scan volume and correctness. CTAS is a physical-layout optimization, not a substitute for a complete data lifecycle strategy.

### How to Solve the Problem

#### Step 1 — Profile

Identify stable access patterns and expensive scans.

#### Step 2 — Materialize

Use CTAS to produce a compact analytical representation.

#### Step 3 — Optimize

Choose partitioning and column selection based on measured query behavior.

#### Step 4 — Validate

Compare semantics, bytes scanned, and latency.

### Example

```sql
CREATE TABLE analytics.orders_daily
WITH (format='PARQUET', partitioned_by=ARRAY['order_date']) AS
SELECT order_id, customer_id, total_amount, order_date
FROM raw.orders;
```

### Why This Is the Correct Approach

Materialization is justified when repeated analytical access benefits from a more efficient physical representation.

### Production Considerations

- **Cost:** Reduce unnecessary scanned data.
- **Performance:** Use columnar storage and useful partitioning.
- **Reliability:** Make the materialization process repeatable and validated.

### Strong Interview Answer

> I’d profile the recurring query pattern, use CTAS to create a narrow Parquet dataset, partition it only where that improves real queries, and validate both correctness and scan reduction.

### Common Weak Answers

- Partitioning every column.
- Selecting all raw columns into the curated table.
- Assuming CTAS automatically solves every performance problem.

### Follow-Up Questions an Interviewer May Ask

1. What are the partition limits you would verify?
2. When would Iceberg be better?
3. How would you refresh the table incrementally?

## Question 14 — Diagnose a Redshift table with poor query performance

**Difficulty:** Moderate

**Primary Topics:** Redshift, distribution styles, sort keys, ATO, WLM

### Interview Question

A Redshift workload has become slower as the fact table grows. Explain how you would investigate distribution, sorting, workload management, and query behavior.

### Problem / Scenario

Queries join a large fact table to dimensions and sometimes scan much more data than expected.

### What the Interviewer Is Evaluating

- MPP layout
- Distribution and skew
- Sort keys
- Workload management

### Expected Approach

1. Inspect query plans and table distribution.
2. Check for data skew and poor distribution choices.
3. Evaluate sort order and pruning.
4. Inspect workload queues/priorities and concurrency.
5. Change one bottleneck at a time and validate.

### Solution / Model Answer

I would begin with evidence from query plans and Redshift system information, then inspect distribution and skew. Poor distribution can cause expensive data movement, while poor sort order can increase scanning. I would also inspect workload-management behavior and concurrency. If appropriate, Automatic Table Optimization can help manage table layout, but I would still validate the resulting workload.

### How to Solve the Problem

#### Step 1 — Observe

Identify whether the bottleneck is scan, redistribution, queueing, or compute.

#### Step 2 — Inspect layout

Check distribution style/key, skew, and sort behavior.

#### Step 3 — Inspect workload

Check queues, priorities, concurrency, and competing workloads.

#### Step 4 — Validate

Benchmark representative queries after each targeted change.

### Example

```sql
EXPLAIN
SELECT c.segment, SUM(f.amount)
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.segment;
```

### Why This Is the Correct Approach

Redshift performance is a combination of physical data layout, query shape, and workload management.

### Production Considerations

- **Performance:** Reduce unnecessary redistribution and scanning.
- **Cost:** Avoid overprovisioning before proving the bottleneck.
- **Reliability:** Use controlled changes and regression testing.
- **Observability:** Use query plans and system metrics/views.

### Strong Interview Answer

> I’d diagnose the bottleneck rather than immediately resize. I’d inspect distribution skew, sort behavior, query plans, and workload queues, then make a targeted change and benchmark it.

### Common Weak Answers

- Resizing immediately without diagnosis.
- Assuming sort keys alone fix joins.
- Ignoring workload queueing.

### Follow-Up Questions an Interviewer May Ask

1. When would AUTO distribution be reasonable?
2. How does Spectrum change the architecture?
3. What would you monitor after the change?

## Question 15 — Design Kinesis Streams → Firehose → S3

**Difficulty:** Moderate

**Primary Topics:** Kinesis Data Streams, Firehose, S3, Parquet

### Interview Question

Design a streaming ingestion path for clickstream events that must be available for near-real-time delivery into an S3 analytics lake.

### Problem / Scenario

Producers emit high-volume events. The lake should receive buffered objects in a query-friendly format, while another consumer may need the stream directly.

### What the Interviewer Is Evaluating

- Streaming architecture
- Partitioning
- Managed delivery
- S3 analytics layout

### Expected Approach

1. Use Data Streams when direct stream consumers are required.
2. Choose partition keys carefully.
3. Use Firehose for managed delivery and buffering where appropriate.
4. Write an analytics-friendly format and layout.
5. Monitor lag, delivery errors, and downstream quality.

### Solution / Model Answer

I would use Kinesis Data Streams when the platform needs explicit stream consumption and retention behavior. Firehose can then provide a managed delivery path into S3, including buffering and supported transformations/format conversion. The partition-key strategy must avoid hot shards, while the S3 destination should be designed for efficient analytics rather than raw event dumping.

### How to Solve the Problem

#### Step 1 — Ingest

Choose a partition-key strategy that distributes traffic.

#### Step 2 — Consume

Use KCL/Lambda/custom consumers when application processing is required.

#### Step 3 — Deliver

Use Firehose for managed S3 delivery where its semantics fit.

#### Step 4 — Operate

Monitor stream lag, delivery failures, and downstream data quality.

### Example

```text
Clickstream producers -> Kinesis Data Streams -> consumers
                                      -> Firehose -> S3
```

### Why This Is the Correct Approach

The architecture separates stream semantics from managed delivery and allows different consumers to use the same event path.

### Production Considerations

- **Reliability:** Handle retries and downstream idempotency.
- **Performance:** Avoid hot shards and monitor iterator age.
- **Cost:** Choose capacity mode and delivery buffering intentionally.
- **Data Quality:** Validate event schema and completeness.

### Strong Interview Answer

> I’d use Streams for controlled event ingestion and consumer processing, with Firehose for managed delivery to S3. I’d design partitioning, buffering, schema validation, observability, and replay behavior together.

### Common Weak Answers

- Using one partition key for all events.
- Treating Firehose as a substitute for every custom consumer.
- Ignoring partial producer failures.

### Follow-Up Questions an Interviewer May Ask

1. How would you diagnose a hot shard?
2. When would MSK be better?
3. How would you replay a time window?

## Question 16 — Govern cross-account lake access with Lake Formation

**Difficulty:** Moderate

**Primary Topics:** Lake Formation, Glue Catalog, Athena, cross-account governance

### Interview Question

An analytics account needs governed access to selected tables owned by another AWS account. How would you reason about discovery, authorization, and cross-account sharing?

### Problem / Scenario

The organization wants analysts to query approved datasets without granting broad S3 access.

### What the Interviewer Is Evaluating

- Lake Formation governance
- Catalog versus authorization
- Cross-account sharing
- Fine-grained access

### Expected Approach

1. Identify the data owner and consumer accounts.
2. Use catalog/governance mechanisms for shared datasets.
3. Grant only the required table/column/row access where supported.
4. Ensure underlying S3/KMS permissions and integration are consistent.
5. Test from the consumer identity.

### Solution / Model Answer

Lake Formation should be treated as a governance and authorization layer around cataloged data, not merely a discovery mechanism. I would define ownership, register/govern the data location, use appropriate Lake Formation permissions and cross-account sharing mechanisms, and ensure that IAM, KMS, S3, and query-service integration do not contradict the intended policy. I would validate access using the actual consumer role.

### How to Solve the Problem

#### Step 1 — Separate concerns

Define discovery metadata independently from authorization.

#### Step 2 — Grant narrowly

Share only the datasets and fine-grained permissions required.

#### Step 3 — Align layers

Ensure IAM, S3, KMS, and Lake Formation policies are mutually consistent.

#### Step 4 — Test

Validate both allowed and denied paths.

### Example

```text
Producer account -> Lake Formation governed catalog/data
Consumer account -> approved shared dataset -> Athena
```

### Why This Is the Correct Approach

Cross-account governance succeeds only when metadata, authorization, encryption, and service integration align.

### Production Considerations

- **Security:** Use least privilege and test denied access.
- **Governance:** Define ownership and approved data products/datasets.
- **Reliability:** Avoid policy changes that silently break production consumers.

### Strong Interview Answer

> I’d use Lake Formation for governed data access, explicitly separate discovery from authorization, and align cross-account catalog, S3, KMS, and IAM behavior. Then I’d test the consumer role against both permitted and denied datasets.

### Common Weak Answers

- Granting the consumer broad S3 access.
- Assuming a catalog share automatically solves every authorization layer.
- Ignoring KMS permissions.

### Follow-Up Questions an Interviewer May Ask

1. How would LF-Tags help at scale?
2. How would Athena consume the shared data?
3. What would you check after an AccessDenied?

## Question 17 — Make a private Glue job reach S3 without unnecessary public routing

**Difficulty:** Moderate

**Primary Topics:** VPC, S3 Gateway Endpoint, Glue, IAM, KMS

### Interview Question

A Glue job runs in private subnets and cannot read its S3 input. The security team does not want a public internet path. Walk through your design and troubleshooting approach.

### Problem / Scenario

The job has a valid IAM role but times out while accessing S3.

### What the Interviewer Is Evaluating

- Private networking
- VPC endpoints
- Routing
- IAM/KMS distinction

### Expected Approach

1. Verify the subnet route tables and S3 endpoint configuration.
2. Check security controls and DNS where relevant.
3. Verify the Glue role's S3 permissions.
4. Check KMS permissions for encrypted objects.
5. Use logs to distinguish network timeout from authorization failure.

### Solution / Model Answer

I would first determine whether the failure is network reachability or authorization. For S3, a gateway endpoint can provide private VPC access without requiring an internet gateway or NAT for the S3 path. I would verify route tables, endpoint policy, S3 bucket policy, IAM role permissions, and KMS permissions if the objects are encrypted. Logs and the exact error determine which layer is failing.

### How to Solve the Problem

#### Step 1 — Network

Check subnet route tables and the S3 gateway endpoint.

#### Step 2 — Policy

Check endpoint, bucket, and IAM policies for the required actions.

#### Step 3 — Encryption

If SSE-KMS is used, verify KMS key-policy/IAM permissions.

#### Step 4 — Validate

Retest from the same job role and inspect logs.

### Example

```text
Private subnet -> S3 gateway endpoint -> S3
IAM + S3 policy + endpoint policy + KMS policy control access
```

### Why This Is the Correct Approach

A timeout and AccessDenied are different classes of failure; diagnosing the wrong layer wastes time.

### Production Considerations

- **Security:** Keep the data plane private and use least privilege.
- **Networking:** Prefer the appropriate VPC endpoint pattern for the service.
- **Observability:** Use job/network/service logs to classify the failure.

### Strong Interview Answer

> I’d separate connectivity from authorization. For S3 I’d verify the gateway endpoint and route tables first, then IAM, bucket and endpoint policies, and KMS if encryption is involved. I’d validate with the actual Glue role and evidence from logs.

### Common Weak Answers

- Adding NAT immediately.
- Assuming IAM is the only policy involved.
- Treating KMS failure as a network failure.

### Follow-Up Questions an Interviewer May Ask

1. When would an interface endpoint be relevant?
2. What can an endpoint policy restrict?
3. How would you prove the route is private?

## Question 18 — Orchestrate Glue, Data Quality, and Athena with Step Functions

**Difficulty:** Moderate

**Primary Topics:** Step Functions, Glue ETL, Glue Data Quality, Athena, EventBridge

### Interview Question

Design a workflow that starts when a new curated batch is available, runs a Glue job, performs data-quality validation, and then allows Athena consumers to use the published dataset.

### Problem / Scenario

The workflow must stop publication when critical quality checks fail and should retry transient failures.

### What the Interviewer Is Evaluating

- Workflow design
- Quality gates
- Event-driven orchestration
- Retry/Catch

### Expected Approach

1. Use EventBridge for the triggering event where appropriate.
2. Model Glue and quality checks as explicit states.
3. Use Retry for transient errors and Catch for terminal paths.
4. Publish only after successful quality validation.
5. Record execution evidence and route failures for remediation.

### Solution / Model Answer

EventBridge can route the triggering event to a Step Functions state machine. The workflow can run Glue ETL, evaluate quality, and branch based on the result. Critical failures should stop or quarantine publication. Retry policies should be bounded and targeted at transient errors, while Catch paths should preserve enough context for operators.

### How to Solve the Problem

#### Step 1 — Trigger

Use an event pattern that identifies the intended batch.

#### Step 2 — Process

Run the transformation and wait for its completion.

#### Step 3 — Validate

Execute quality checks and branch on critical failures.

#### Step 4 — Publish

Only expose the trusted dataset after the gate passes.

### Example

```text
S3/Event -> EventBridge -> Step Functions
                    -> Glue -> DQ gate -> Publish
```

### Why This Is the Correct Approach

Event routing and workflow orchestration are complementary: EventBridge starts or routes work; Step Functions manages stateful execution.

### Production Considerations

- **Reliability:** Use bounded retries and idempotent tasks.
- **Data Quality:** Treat critical rules as publication gates.
- **Observability:** Track execution state and quality outcomes.
- **Cost:** Avoid repeated full processing through uncontrolled retries.

### Strong Interview Answer

> I’d use EventBridge for the event trigger and Step Functions for the workflow. Glue performs transformation, Data Quality acts as a gate, and only successful executions publish trusted data. I’d add bounded retries and explicit failure handling.

### Common Weak Answers

- Putting all orchestration into EventBridge rules.
- Publishing before the quality gate.
- Retrying permanent data errors indefinitely.

### Follow-Up Questions an Interviewer May Ask

1. Would MWAA be better here?
2. How would you handle duplicate events?
3. How would you quarantine a failed batch?

## Question 19 — Build a DMS CDC-to-Iceberg analytics path

**Difficulty:** Moderate

**Primary Topics:** DMS, CDC, S3, Iceberg, Glue Catalog, Athena

### Interview Question

A PostgreSQL operational database must feed an S3/Iceberg analytical environment continuously. Explain a practical architecture and the main correctness risks.

### Problem / Scenario

The source changes continuously and analysts expect current-enough data without repeatedly copying the entire source.

### What the Interviewer Is Evaluating

- CDC architecture
- WAL/replication
- S3 targets
- Iceberg merge/update semantics
- Validation

### Expected Approach

1. Choose DMS full load plus CDC when appropriate.
2. Land CDC in a durable S3 representation.
3. Transform CDC events into the target table semantics.
4. Use Iceberg operations where updates/deletes are required.
5. Validate completeness, ordering assumptions, and recovery behavior.

### Solution / Model Answer

DMS can perform an initial full load and continue changes to S3. The downstream layer then has to interpret change records correctly and apply them to the Iceberg table, using the appropriate merge/update/delete semantics. The design must account for duplicate delivery, ordering assumptions, schema changes, checkpoints, and recovery. PostgreSQL WAL retention must also be monitored because a stalled replication path can retain source WAL.

### How to Solve the Problem

#### Step 1 — Land

Use DMS to establish the initial state and CDC stream into durable storage.

#### Step 2 — Interpret

Map insert/update/delete events to the target table semantics.

#### Step 3 — Apply

Use Iceberg transaction semantics and idempotent processing.

#### Step 4 — Validate

Compare source/target counts, keys, checkpoints, and CDC lag.

### Example

```text
PostgreSQL -> DMS full load + CDC -> S3 CDC landing -> processing -> Iceberg -> Glue Catalog -> Athena
```

### Why This Is the Correct Approach

CDC landing and analytical table maintenance are separate correctness problems; solving one does not guarantee the other.

### Production Considerations

- **Reliability:** Checkpoint CDC processing and design restart/replay behavior.
- **Data Quality:** Validate keys, change application, and completeness.
- **Observability:** Monitor DMS lag, WAL growth, processing lag, and failed batches.
- **Security:** Use least-privilege roles and encryption.

### Strong Interview Answer

> I’d separate DMS's source replication responsibility from the downstream Iceberg merge responsibility. DMS lands the initial and changed data; a controlled processing layer applies those changes idempotently to Iceberg. I’d monitor CDC lag and PostgreSQL WAL growth and validate target correctness.

### Common Weak Answers

- Writing every CDC record directly as a final table without semantics.
- Ignoring deletes and updates.
- Ignoring source WAL retention.

### Follow-Up Questions an Interviewer May Ask

1. How would you recover after a downstream outage?
2. When would zero-ETL be preferable?
3. How would you handle schema evolution?

## Question 20 — Publish a governed data product with DataZone

**Difficulty:** Moderate

**Primary Topics:** DataZone, Glue Catalog, Lake Formation, Athena, governance

### Interview Question

An enterprise wants analysts to discover a certified sales dataset, understand its business meaning, request access, and then query it. How would you use DataZone with the underlying AWS data platform?

### Problem / Scenario

The organization wants business metadata and subscription workflows without replacing the underlying storage/query systems.

### What the Interviewer Is Evaluating

- Data discovery
- Data products
- Business metadata
- Governance integration

### Expected Approach

1. Publish the dataset as a governed data asset/data product.
2. Add business metadata, glossary terms, and ownership.
3. Use subscription/approval workflows for access.
4. Keep actual authorization aligned with Lake Formation/IAM and data-service controls.
5. Provide Athena/query access after approval.

### Solution / Model Answer

DataZone can provide a business-facing catalog and data-product experience over technical assets. I would publish the sales dataset with business context, ownership, glossary terms, and quality expectations, then use subscription workflows for discovery and access requests. The actual data authorization still needs to be enforced by the underlying governance and access-control layers such as Lake Formation and IAM.

### How to Solve the Problem

#### Step 1 — Describe

Make the dataset understandable to consumers through business metadata.

#### Step 2 — Govern

Define ownership, approval, and subscription workflow.

#### Step 3 — Authorize

Ensure the approved consumer receives actual technical access.

#### Step 4 — Measure

Track usage, quality, ownership, and lifecycle.

### Example

```text
Producer -> Glue Catalog/Lake Formation -> DataZone data product
Consumer -> discover -> subscribe/request -> approved technical access -> Athena
```

### Why This Is the Correct Approach

DataZone is an enterprise discovery/governance experience, not a replacement for the data plane.

### Production Considerations

- **Governance:** Define ownership, glossary, certification, and approval paths.
- **Security:** Ensure subscription approval maps to real authorization.
- **Data Quality:** Expose quality expectations and certification status.

### Strong Interview Answer

> I’d use DataZone for discovery, business metadata, and data-product/subscription workflows, while keeping technical authorization in the underlying AWS data and governance layers. The goal is to connect business discovery to enforceable access.

### Common Weak Answers

- Saying DataZone stores all the data.
- Treating a subscription as equivalent to an IAM grant.
- Ignoring Lake Formation integration.

### Follow-Up Questions an Interviewer May Ask

1. How would you handle a subscription that still gets AccessDenied?
2. What business metadata would you require?
3. How does this differ from a custom catalog?


---

# Level 3 — Hard Interview Questions

## Question 21 — Athena costs suddenly double: diagnose from evidence

**Difficulty:** Hard

**Primary Topics:** Athena, partition projection, Parquet, Iceberg, CloudWatch/Cost Explorer

### Interview Question

Athena query costs have doubled week over week even though query volume is roughly flat. Walk me through your investigation.

### Problem / Scenario

The data volume grew modestly, but scanned bytes and cost increased disproportionately.

### What the Interviewer Is Evaluating

- Evidence-based troubleshooting
- Query plans
- Data layout
- Cost attribution

### Expected Approach

1. Confirm cost and scan-volume changes.
2. Identify which queries or workgroups changed.
3. Inspect partitions/projection and file layout.
4. Use EXPLAIN and query history to identify inefficient scans.
5. Fix the highest-impact cause and validate.

### Solution / Model Answer

I would correlate Cost Explorer/workload evidence with Athena query execution data and bytes scanned. Then I would identify whether SQL changes, missing partition predicates, partition-projection configuration, file layout, or an Iceberg maintenance issue caused more data to be read. I would use EXPLAIN and representative queries to isolate the root cause, then measure the fix.

### How to Solve the Problem

#### Step 1 — Scope

Find the workgroup, query class, or dataset responsible for the increase.

#### Step 2 — Compare

Compare SQL, scan volume, partitions, and file counts before and after.

#### Step 3 — Diagnose

Determine whether the issue is pruning, layout, query design, or table maintenance.

#### Step 4 — Validate

Re-run representative queries and confirm scan and cost reduction.

### Example

```sql
EXPLAIN
SELECT *
FROM curated.events
WHERE event_date >= DATE '2026-10-01';
```

### Why This Is the Correct Approach

The key is to diagnose the cost driver from measured scan behavior rather than simply adding partitions.

### Production Considerations

- **Cost:** Use actual scan and spend evidence.
- **Performance:** Inspect query plans and data layout.
- **Reliability:** Ensure optimization does not change semantics.
- **Observability:** Use query history and cost telemetry.

### Strong Interview Answer

> I’d correlate spend with bytes scanned and query identity, then inspect predicates, partitioning/projection, file layout, and EXPLAIN output. I’d fix the highest-volume root cause and verify the improvement quantitatively.

### Common Weak Answers

- Blaming AWS pricing without checking scan volume.
- Partitioning every field.
- Optimizing without identifying the offending queries.

### Follow-Up Questions an Interviewer May Ask

1. What if the query volume did not change but file count did?
2. How would Iceberg maintenance affect this?
3. How would you prevent recurrence?

## Question 22 — A Glue job goes from 20 minutes to two hours

**Difficulty:** Hard

**Primary Topics:** Glue ETL, Spark, partitions, skew, Data Quality, CloudWatch

### Interview Question

A Glue Spark job that normally completes in 20 minutes now takes two hours. Walk me through a production investigation.

### Problem / Scenario

Input volume increased only moderately, but the runtime change is dramatic.

### What the Interviewer Is Evaluating

- Spark troubleshooting
- Skew/shuffle
- Input growth
- Worker configuration
- Observability

### Expected Approach

1. Compare current and historical input size and file counts.
2. Inspect Spark stages, shuffle, skew, and task duration.
3. Check schema and transformation changes.
4. Check worker utilization and Auto Scaling behavior.
5. Validate downstream data-quality or I/O bottlenecks.
6. Apply one targeted fix and benchmark.

### Solution / Model Answer

I would not immediately add workers. I would compare input partitions and file sizes, inspect Spark stages for skew and shuffle amplification, check whether schema or transformation changes introduced expensive work, and inspect Glue logs/metrics. If the bottleneck is compute or parallelism, I would tune workers or partitioning; if it is skew, I would address the key distribution. I would then validate with a representative run.

### How to Solve the Problem

#### Step 1 — Baseline

Compare runtime, input bytes, file count, and historical execution evidence.

#### Step 2 — Locate

Identify the slow Spark stage and whether a small number of tasks dominate.

#### Step 3 — Classify

Separate skew, shuffle, I/O, schema, or capacity problems.

#### Step 4 — Fix

Apply the smallest change that addresses the measured bottleneck.

### Example

```text
CloudWatch/Glue metrics -> slow stage -> skew/shuffle/I/O/capacity -> targeted fix
```

### Why This Is the Correct Approach

Senior troubleshooting is about locating the bottleneck before changing infrastructure.

### Production Considerations

- **Performance:** Inspect skew, shuffle, partitioning, and worker utilization.
- **Cost:** Avoid scaling workers blindly.
- **Observability:** Use job logs/metrics and Spark execution evidence.
- **Data Quality:** Check whether validation is now the dominant stage.

### Strong Interview Answer

> I’d compare historical and current executions, identify the slow stage, and determine whether the cause is skew, shuffle, I/O, schema change, or capacity. Only then would I tune workers or partitioning, followed by a measured validation run.

### Common Weak Answers

- Doubling workers immediately.
- Assuming more data is the only explanation.
- Ignoring skew and shuffle.

### Follow-Up Questions an Interviewer May Ask

1. How would you recognize skew?
2. When would Auto Scaling help?
3. What if the slow stage is Data Quality?

## Question 23 — Kinesis iterator age keeps increasing

**Difficulty:** Hard

**Primary Topics:** Kinesis Data Streams, shards, partition keys, KCL, Lambda, EFO

### Interview Question

A Kinesis consumer's iterator age has increased continuously for an hour. What would you investigate, and how would you decide on the fix?

### Problem / Scenario

The producer rate is stable but the consumer is falling behind.

### What the Interviewer Is Evaluating

- Streaming diagnosis
- Consumer throughput
- Hot shards
- Downstream bottlenecks

### Expected Approach

1. Check per-shard throughput and distribution.
2. Identify hot partition keys.
3. Measure consumer processing time and batch behavior.
4. Check Lambda concurrency or consumer capacity where relevant.
5. Check downstream dependencies.
6. Scale or rebalance only after identifying the bottleneck.

### Solution / Model Answer

Iterator age increasing means the consumer is not keeping up with the incoming stream. I would inspect shard-level utilization and partition-key distribution for hot shards, then measure consumer processing time, batch size, concurrency, and downstream latency. If a single key is hot, scaling the total consumer pool may not solve the problem; the partitioning strategy may need correction.

### How to Solve the Problem

#### Step 1 — Measure lag

Establish whether lag is isolated to specific shards or global.

#### Step 2 — Inspect producers

Check partition-key distribution and partial failures/retries.

#### Step 3 — Inspect consumers

Measure processing time, concurrency, batching, and downstream calls.

#### Step 4 — Fix

Rebalance keys, scale consumers, optimize processing, or address downstream bottlenecks.

### Example

```text
Iterator age rising -> inspect shard distribution + consumer throughput + downstream latency
```

### Why This Is the Correct Approach

Streaming lag is a symptom; the root cause can be partitioning, consumer capacity, processing cost, or downstream backpressure.

### Production Considerations

- **Reliability:** Preserve ordering assumptions when changing partitioning.
- **Performance:** Eliminate hot shards and reduce per-record processing cost.
- **Cost:** Scale only the constrained component.
- **Observability:** Monitor iterator age, shard metrics, and consumer errors.

### Strong Interview Answer

> I’d first determine whether lag is shard-local or global. Then I’d inspect partition-key skew, consumer processing time, concurrency, and downstream latency. I’d fix the actual bottleneck rather than simply increasing capacity.

### Common Weak Answers

- Scaling everything without checking hot shards.
- Ignoring downstream latency.
- Treating iterator age as the root cause.

### Follow-Up Questions an Interviewer May Ask

1. How would EFO change the diagnosis?
2. How would you replay a backlog?
3. When would MSK be a better fit?

## Question 24 — Redshift query performance degrades as data grows

**Difficulty:** Hard

**Primary Topics:** Redshift, distribution, sort keys, ATO, WLM, Spectrum

### Interview Question

A fact-table workload was fast at 5 TB but is now slow at 30 TB. How would you determine whether the problem is table layout, query design, or workload management?

### Problem / Scenario

The workload has recurring joins, aggregations, and occasional S3 external-table access.

### What the Interviewer Is Evaluating

- MPP diagnosis
- Data distribution
- Sort pruning
- Workload management
- Spectrum boundary

### Expected Approach

1. Inspect EXPLAIN and system metrics.
2. Check distribution skew and data movement.
3. Check sort order and scan volume.
4. Check queues/priorities/concurrency.
5. Determine whether Spectrum is appropriate or whether data should be loaded into Redshift.
6. Benchmark targeted changes.

### Solution / Model Answer

I would first classify the bottleneck: redistribution, scan, compute, queueing, or external S3 access. Distribution skew can create expensive data movement; poor sort alignment can increase scans; WLM can create queue latency. For external data, I would also determine whether Spectrum remains appropriate or whether frequently queried data should be loaded into Redshift. Each change needs measured validation.

### How to Solve the Problem

#### Step 1 — Classify

Use query plans and system evidence to isolate the dominant cost.

#### Step 2 — Inspect layout

Check distribution and sort behavior.

#### Step 3 — Inspect workload

Check WLM queues, priorities, and concurrency.

#### Step 4 — Choose storage boundary

Decide whether data belongs in Redshift or remains external.

#### Step 5 — Validate

Benchmark representative queries.

### Example

```sql
EXPLAIN
SELECT d.region, SUM(f.amount)
FROM fact_sales f
JOIN dim_customer d ON f.customer_id=d.customer_id
GROUP BY d.region;
```

### Why This Is the Correct Approach

Scale changes the cost of poor physical design, so the diagnosis must account for distribution, sorting, workload management, and storage boundaries.

### Production Considerations

- **Performance:** Reduce data movement and unnecessary scanning.
- **Cost:** Avoid moving all data into Redshift without a workload justification.
- **Reliability:** Test layout changes safely.
- **Observability:** Use plans and workload metrics.

### Strong Interview Answer

> I’d classify the bottleneck using EXPLAIN and system evidence, then inspect distribution skew, sort pruning, WLM queueing, and external scans. I’d only change table design or storage placement after proving the bottleneck.

### Common Weak Answers

- Immediately resizing.
- Ignoring distribution skew.
- Loading every S3 dataset into Redshift.

### Follow-Up Questions an Interviewer May Ask

1. How would ATO help?
2. What would make Spectrum the better choice?
3. How would you validate a distribution-key change?

## Question 25 — DMS CDC lag and PostgreSQL WAL growth occur together

**Difficulty:** Hard

**Primary Topics:** DMS, PostgreSQL WAL, replication slots, CDC, observability

### Interview Question

A PostgreSQL source is showing rapid WAL growth while the DMS CDC task is lagging. Walk me through your diagnosis and immediate risk controls.

### Problem / Scenario

The source database is production-critical and cannot tolerate unbounded WAL growth.

### What the Interviewer Is Evaluating

- CDC mechanics
- Replication slots
- Lag diagnosis
- Operational risk
- Recovery

### Expected Approach

1. Confirm DMS task state and CDC lag.
2. Inspect replication-slot/WAL retention behavior.
3. Determine whether the target or DMS task is bottlenecked.
4. Avoid destructive slot changes without understanding recovery implications.
5. Restore CDC throughput and validate source health.
6. Plan recovery if a gap exists.

### Solution / Model Answer

PostgreSQL logical replication can retain WAL through replication slots while changes await consumption. I would establish whether the DMS task is stopped, throttled, blocked by the target, or otherwise unable to consume changes. The immediate risk is source storage pressure from retained WAL. I would restore consumption or deliberately follow a documented recovery path, rather than deleting or manipulating replication state blindly.

### How to Solve the Problem

#### Step 1 — Establish state

Check DMS task status, CDC latency, and source replication state.

#### Step 2 — Assess WAL risk

Measure WAL growth and available source storage.

#### Step 3 — Find bottleneck

Determine whether DMS, network, target throughput, or downstream processing is responsible.

#### Step 4 — Recover safely

Restore consumption or execute a documented re-baseline/reload strategy if continuity is lost.

### Example

```text
PostgreSQL -> logical replication slot/WAL -> DMS CDC
Lag -> WAL retention -> source storage risk
```

### Why This Is the Correct Approach

WAL growth is a consequence of an unresolved CDC consumption problem, so the diagnosis must protect the source while restoring replication.

### Production Considerations

- **Reliability:** Avoid irreversible replication changes without a recovery plan.
- **Observability:** Monitor DMS CDC latency and PostgreSQL WAL/slot state.
- **Performance:** Address the actual throughput bottleneck.
- **Cost:** Prevent emergency storage and reprocessing growth.

### Strong Interview Answer

> I’d treat this as both a CDC incident and a source-database capacity incident. I’d correlate DMS lag with replication-slot/WAL retention, identify why consumption slowed, protect source storage, and restore or re-baseline CDC using a controlled recovery plan.

### Common Weak Answers

- Deleting the replication slot immediately.
- Treating WAL growth as unrelated to CDC lag.
- Ignoring the source's remaining storage.

### Follow-Up Questions an Interviewer May Ask

1. How would you validate CDC completeness after recovery?
2. When would you choose zero-ETL?
3. How would DMS Serverless affect the architecture?

## Question 26 — Lake Formation subscription approved but Athena gets AccessDenied

**Difficulty:** Hard

**Primary Topics:** Lake Formation, DataZone, Athena, IAM, S3, KMS

### Interview Question

A user successfully subscribes to a DataZone data product but Athena returns AccessDenied. How would you diagnose the mismatch?

### Problem / Scenario

The data product is governed by Lake Formation and the underlying S3 data is encrypted.

### What the Interviewer Is Evaluating

- Governance-to-enforcement path
- Identity propagation
- Lake Formation permissions
- S3/KMS layers

### Expected Approach

1. Verify the identity used by Athena.
2. Check DataZone subscription/approval state.
3. Check Lake Formation permissions and data filters.
4. Check IAM/S3 access and KMS permissions.
5. Test each layer with evidence and avoid broad grants as a shortcut.

### Solution / Model Answer

A DataZone subscription is a governance workflow; it does not mean every underlying authorization layer is automatically correct. I would identify the actual consumer principal, verify the subscription and approved entitlement, inspect Lake Formation grants/data filters, then check S3 and KMS policies. The exact AccessDenied message and service logs should determine which layer is failing.

### How to Solve the Problem

#### Step 1 — Identity

Confirm the principal actually making the Athena request.

#### Step 2 — Governance

Confirm the DataZone subscription and Lake Formation grant state.

#### Step 3 — Data plane

Check S3 and KMS permissions required for the access path.

#### Step 4 — Validate

Retest using the intended consumer role and capture the resulting evidence.

### Example

```text
DataZone subscription -> governance intent
Lake Formation/IAM/S3/KMS -> enforceable access
Athena -> query
```

### Why This Is the Correct Approach

The incident is caused by treating business approval and technical authorization as the same operation.

### Production Considerations

- **Security:** Never solve AccessDenied by granting broad permissions.
- **Governance:** Keep business subscription and technical authorization aligned.
- **Observability:** Use service logs and policy evaluation evidence.

### Strong Interview Answer

> I’d trace the request from the consumer identity through DataZone approval, Lake Formation grants, and the underlying S3/KMS controls. I’d fix the narrowest missing permission and retest with the real consumer principal.

### Common Weak Answers

- Granting s3:* to the user.
- Assuming DataZone alone grants data access.
- Ignoring KMS.

### Follow-Up Questions an Interviewer May Ask

1. How would LF-Tags help?
2. What if S3 access works but Athena still fails?
3. How would you audit the access decision?

## Question 27 — Private Glue job times out only for one dataset

**Difficulty:** Hard

**Primary Topics:** VPC, S3 Gateway Endpoint, Glue, KMS, endpoint policies

### Interview Question

A private Glue job can read one S3 prefix but times out on another prefix. The IAM role appears correct. What would you investigate?

### Problem / Scenario

The second dataset is encrypted differently and may have different bucket or endpoint policies.

### What the Interviewer Is Evaluating

- Layered networking diagnosis
- S3/KMS authorization
- Endpoint policies
- Evidence-driven troubleshooting

### Expected Approach

1. Compare the physical buckets/prefixes and encryption configuration.
2. Check route and endpoint reachability.
3. Compare S3 bucket policies and endpoint policy conditions.
4. Check KMS key policy/grants for the second dataset.
5. Use CloudWatch/Glue logs to distinguish timeout from AccessDenied.

### Solution / Model Answer

I would compare the working and failing paths rather than redesigning the network. If the S3 route is shared, the difference is likely policy, bucket, encryption, or dataset-specific configuration. I would inspect the S3 gateway endpoint and route table first, then bucket policy, IAM, endpoint policy, and KMS key policy. If the symptom is a true timeout, I would verify connectivity; if access reaches S3 but is denied, I would follow the authorization evidence.

### How to Solve the Problem

#### Step 1 — Compare

Use the working dataset as a control case.

#### Step 2 — Network

Verify both datasets use the expected S3 path and route.

#### Step 3 — Policy

Compare bucket, endpoint, IAM, and KMS policies.

#### Step 4 — Validate

Retest with the same job role and capture exact error behavior.

### Example

```text
Working dataset = control
Failing dataset -> compare S3 policy + KMS + endpoint conditions
```

### Why This Is the Correct Approach

Control-case comparison is faster and safer than changing shared infrastructure when only one dataset fails.

### Production Considerations

- **Security:** Preserve dataset-specific least privilege.
- **Networking:** Avoid adding NAT just to mask an authorization problem.
- **Observability:** Use exact service errors and logs.

### Strong Interview Answer

> I’d compare the working and failing paths. If networking is shared, I’d focus on dataset-specific S3, endpoint, IAM, and KMS policies and use logs to distinguish reachability from authorization.

### Common Weak Answers

- Adding NAT immediately.
- Assuming all S3 prefixes have identical policy behavior.
- Ignoring KMS.

### Follow-Up Questions an Interviewer May Ask

1. What if the failing dataset is in another account?
2. How would you test the endpoint policy?
3. What does an S3 gateway endpoint change?

## Question 28 — EventBridge event does not start the Step Functions workflow

**Difficulty:** Hard

**Primary Topics:** EventBridge, Step Functions, event patterns, IAM, observability

### Interview Question

A producer reports that an event was emitted, but the Step Functions workflow never starts. Walk through the troubleshooting process.

### Problem / Scenario

The event is expected to trigger a state machine through an EventBridge rule.

### What the Interviewer Is Evaluating

- Event-driven troubleshooting
- Event pattern matching
- Target configuration
- IAM and observability

### Expected Approach

1. Confirm the event reached the intended event bus.
2. Check the rule's event pattern.
3. Check whether the rule is enabled and has the correct target.
4. Verify target invocation permissions.
5. Inspect delivery/failure evidence and replay a controlled test event.

### Solution / Model Answer

I would trace the event path end to end: source → event bus → rule match → target invocation → Step Functions execution. A common failure is a pattern mismatch, especially for nested fields or source/detail-type values. I would then check rule state, target configuration, invocation permissions, and available EventBridge/Step Functions evidence. I would use a controlled test event that matches the intended contract.

### How to Solve the Problem

#### Step 1 — Trace

Prove each hop rather than assuming the producer's log means EventBridge accepted the event.

#### Step 2 — Match

Compare the actual event envelope with the rule pattern.

#### Step 3 — Invoke

Verify the rule target and required permissions.

#### Step 4 — Validate

Send a known-good test event and observe the execution.

### Example

```json
{
  "source": ["example.orders"],
  "detail-type": ["OrderCreated"]
}
```

### Why This Is the Correct Approach

Event-driven systems fail at boundaries; the fastest diagnosis follows the event through each boundary.

### Production Considerations

- **Reliability:** Define and test event contracts.
- **Security:** Use least-privilege target invocation permissions.
- **Observability:** Retain enough event and execution evidence to trace failures.

### Strong Interview Answer

> I’d trace the event from the bus to the rule, verify the pattern against the actual event, then check the target and invocation permissions. Finally I’d send a known-good test event and confirm a Step Functions execution appears.

### Common Weak Answers

- Only checking Step Functions.
- Changing the rule randomly.
- Assuming an emitted application event proves EventBridge matched it.

### Follow-Up Questions an Interviewer May Ask

1. How would you handle duplicate events?
2. When would EventBridge Scheduler be better?
3. How would you replay an event safely?

## Question 29 — Iceberg small files and maintenance are degrading Athena

**Difficulty:** Hard

**Primary Topics:** Iceberg, S3 Tables, Athena, Glue, compaction, VACUUM/OPTIMIZE

### Interview Question

An Iceberg table receives frequent small writes. Athena performance is degrading and storage contains many old snapshots and files. How would you approach the problem?

### Problem / Scenario

The table is operationally correct but increasingly expensive and slow to query.

### What the Interviewer Is Evaluating

- Iceberg maintenance
- File-size management
- Snapshot lifecycle
- Athena performance

### Expected Approach

1. Measure file counts, sizes, snapshots, and query behavior.
2. Use the table's supported maintenance mechanisms.
3. Consider compaction and snapshot/unreferenced-file cleanup.
4. Validate that maintenance does not conflict with concurrent workloads.
5. Measure query and storage improvements.

### Solution / Model Answer

I would first quantify the small-file and snapshot problem. Iceberg tables can accumulate many small data files and historical metadata when write patterns are highly fragmented. I would use the supported maintenance mechanisms for the chosen platform, such as OPTIMIZE/compaction and VACUUM where applicable, and for S3 Tables evaluate managed maintenance. The goal is to improve file locality and metadata efficiency while retaining the required recovery/time-travel window.

### How to Solve the Problem

#### Step 1 — Measure

Quantify file count, average size, snapshot age, and query impact.

#### Step 2 — Maintain

Use compaction and cleanup capabilities supported by the chosen table platform.

#### Step 3 — Protect history

Keep the retention window required by recovery and governance needs.

#### Step 4 — Validate

Compare query latency, scan behavior, and storage after maintenance.

### Example

```sql
OPTIMIZE my_catalog.my_db.orders REWRITE DATA USING BIN_PACK
VACUUM my_catalog.my_db.orders
```

### Why This Is the Correct Approach

Maintenance must balance performance with retention and recovery requirements; deleting history blindly is not an optimization.

### Production Considerations

- **Performance:** Reduce small-file overhead and metadata work.
- **Reliability:** Preserve required snapshots and recovery guarantees.
- **Cost:** Balance maintenance compute with query/storage savings.

### Strong Interview Answer

> I’d measure the file and snapshot problem first, then apply supported compaction and cleanup while preserving the required retention window. I’d validate both query performance and storage economics afterward.

### Common Weak Answers

- Deleting all snapshots immediately.
- Assuming compaction is free.
- Ignoring concurrent writers and recovery requirements.

### Follow-Up Questions an Interviewer May Ask

1. How does S3 Tables change the maintenance model?
2. When would VACUUM be risky?
3. How would you schedule maintenance?

## Question 30 — Reduce NAT costs for a private AWS data platform

**Difficulty:** Hard

**Primary Topics:** VPC, gateway endpoints, interface endpoints, PrivateLink, S3, Glue, cost

### Interview Question

A private data platform has unexpectedly high NAT Gateway spend. It primarily accesses S3 and several AWS service APIs. How would you reduce the cost without weakening security?

### Problem / Scenario

The architecture intentionally avoids public subnets for data processing.

### What the Interviewer Is Evaluating

- Private networking
- Endpoint selection
- Cost optimization
- Security

### Expected Approach

1. Inventory traffic currently traversing NAT.
2. Use S3 gateway endpoints for S3 traffic where appropriate.
3. Evaluate interface endpoints for services that require them.
4. Check endpoint policies and DNS/routing.
5. Measure NAT reduction and endpoint cost trade-offs.

### Solution / Model Answer

I would first measure which destinations account for NAT traffic. S3 is a prime candidate for a gateway endpoint, which can provide private S3 access from the VPC without NAT for that path. For other AWS APIs, I would evaluate interface endpoints where appropriate. I would not eliminate NAT blindly; I would compare endpoint costs, availability, regional behavior, and application requirements.

### How to Solve the Problem

#### Step 1 — Measure

Identify top NAT destinations and bytes/flows.

#### Step 2 — Replace

Route S3 through a gateway endpoint where supported.

#### Step 3 — Evaluate

Use interface endpoints for appropriate AWS services and PrivateLink patterns.

#### Step 4 — Validate

Confirm traffic follows the intended private route and quantify cost impact.

### Example

```text
Private subnet -> S3 gateway endpoint -> S3
Private subnet -> interface endpoint -> supported AWS service
NAT -> retained only for traffic that actually needs it
```

### Why This Is the Correct Approach

Cost optimization should remove unnecessary network paths while preserving the intended security boundary.

### Production Considerations

- **Cost:** Compare NAT savings against endpoint charges.
- **Security:** Keep traffic private and enforce endpoint policies.
- **Networking:** Verify route tables and DNS for each endpoint.

### Strong Interview Answer

> I’d start with traffic evidence, then move S3 traffic to a gateway endpoint and evaluate interface endpoints for other AWS services. I’d retain NAT only where required and measure the resulting cost and connectivity behavior.

### Common Weak Answers

- Deleting NAT without inventorying dependencies.
- Assuming every service uses a gateway endpoint.
- Ignoring interface endpoint costs.

### Follow-Up Questions an Interviewer May Ask

1. What are the limitations of S3 gateway endpoints?
2. When is PrivateLink relevant?
3. How would you prove the data path stayed private?


---

# Level 4 — Advanced Interview Questions

## Question 31 — Design a governed enterprise serverless lakehouse

**Difficulty:** Advanced

**Primary Topics:** S3, S3 Tables, Glue, Athena, Lake Formation, DataZone, KMS, CloudWatch

### Interview Question

Design an enterprise lakehouse for sales, finance, and operations data. It must support governed discovery, analytics, quality controls, and secure access with minimal infrastructure management.

### Problem / Scenario

Multiple producer teams publish datasets while analysts and downstream AI/analytics teams need discoverable, governed data products.

### What the Interviewer Is Evaluating

- End-to-end architecture
- Governance
- Data products
- Security
- Operations
- Cost

### Expected Approach

1. Start with data domains, consumers, SLAs, and security classifications.
2. Choose S3/S3 Tables/Iceberg storage patterns.
3. Use Glue Catalog and Glue ETL for metadata/processing.
4. Use Data Quality gates before publication.
5. Use Lake Formation for enforceable access controls.
6. Use DataZone for discovery, business metadata, and data-product workflows.
7. Add KMS, private networking, observability, and cost controls.

### Solution / Model Answer

I would build a domain-oriented lakehouse with S3/S3 Tables and Iceberg for durable analytical storage, Glue Catalog for technical metadata, Glue ETL for managed transformations, and Athena for serverless query workloads. Lake Formation would enforce governed access, while DataZone would provide the business-facing catalog and subscription/data-product experience. KMS and private networking would protect the data plane, and CloudWatch/CloudTrail/Cost Explorer would provide operational and financial visibility. Quality gates would prevent untrusted data from being published.

### How to Solve the Problem

#### Step 1 — Requirements

Define domains, consumers, freshness, retention, PII/security classes, and access patterns.

#### Step 2 — Storage and processing

Use S3/Iceberg and managed Glue processing with clear raw-to-curated boundaries.

#### Step 3 — Governance

Combine Glue metadata, Lake Formation authorization, and DataZone business discovery.

#### Step 4 — Operate

Add quality, observability, encryption, private networking, and cost attribution.

#### Step 5 — Scale

Use standardized data-product contracts and reusable access patterns.

### Example

```text
Sources -> S3/S3 Tables -> Glue ETL/DQ -> Iceberg curated tables
                         -> Glue Catalog/Lake Formation
                         -> Athena
DataZone -> discovery/subscription/business metadata
```

### Why This Is the Correct Approach

The architecture separates physical storage, processing, technical metadata, authorization, and business discovery so each layer has a clear responsibility.

### Production Considerations

- **Security:** Use least privilege, KMS, private endpoints, and governed access.
- **Governance:** Define ownership, business metadata, data products, and fine-grained authorization.
- **Reliability:** Use quality gates and repeatable pipelines.
- **Observability:** Monitor jobs, queries, access, and cost.
- **Cost:** Prefer managed/serverless paths where workload characteristics justify them.

### Strong Interview Answer

> I’d separate the platform into storage, processing, metadata, authorization, discovery, and operations. S3/Iceberg provides the lakehouse foundation; Glue handles processing and catalog integration; Lake Formation controls access; DataZone provides business discovery; Athena serves ad-hoc analytics. KMS, private networking, quality gates, and CloudWatch/CloudTrail/Cost Explorer make it production-ready.

### Common Weak Answers

- Putting governance entirely in DataZone.
- Giving analysts direct broad S3 access.
- Ignoring data quality and cost telemetry.

### Follow-Up Questions an Interviewer May Ask

1. Where would Redshift fit?
2. How would you handle cross-account sharing?
3. How would you make the platform cost-accountable per domain?

## Question 32 — Design a recoverable PostgreSQL CDC → Iceberg platform

**Difficulty:** Advanced

**Primary Topics:** DMS, PostgreSQL WAL, S3, Iceberg, Glue, Athena, observability

### Interview Question

Design a production CDC platform that moves PostgreSQL operational data into an Iceberg lakehouse for analytics. It must survive downstream outages and support recovery without silently losing changes.

### Problem / Scenario

The source is business-critical, and CDC lag can create WAL growth risk.

### What the Interviewer Is Evaluating

- CDC architecture
- Recovery
- Idempotency
- Iceberg
- Operational safety

### Expected Approach

1. Separate full load from CDC.
2. Land CDC durably before applying it to curated tables.
3. Design checkpoints and replay semantics.
4. Apply changes idempotently to Iceberg.
5. Monitor DMS lag and source WAL retention.
6. Define recovery/reconciliation procedures.

### Solution / Model Answer

I would use DMS for full load plus CDC and land the change stream durably in S3. A downstream processing layer would transform and apply inserts, updates, and deletes into Iceberg using idempotent transaction logic. The raw CDC landing provides a replay boundary if the curated processing layer fails. Operationally, I would monitor DMS task health, CDC latency, replication-slot/WAL behavior, and downstream processing lag. Recovery would include a clear decision between replaying the durable CDC window and re-baselining from the source.

### How to Solve the Problem

#### Step 1 — Establish baseline

Perform and validate full load before relying on CDC.

#### Step 2 — Create replay boundary

Persist CDC durably so downstream outages do not automatically imply data loss.

#### Step 3 — Apply safely

Use deterministic keys, checkpoints, and idempotent Iceberg operations.

#### Step 4 — Operate

Monitor DMS, WAL, CDC lag, processing lag, and table health.

#### Step 5 — Recover

Define replay/reconciliation and full re-baseline criteria.

### Example

```text
PostgreSQL -> DMS full load + CDC -> durable S3 CDC landing
                                      -> processing -> Iceberg -> Athena
```

### Why This Is the Correct Approach

The key architectural property is a durable replay boundary between source replication and analytical table application.

### Production Considerations

- **Reliability:** Design explicit checkpoints, replay, and reconciliation.
- **Data Quality:** Validate change completeness and target state.
- **Security:** Encrypt source/landing/curated data and use least privilege.
- **Observability:** Correlate source WAL, DMS lag, processing lag, and target freshness.

### Strong Interview Answer

> I’d put a durable S3 CDC landing boundary between DMS and the Iceberg table. That lets me recover downstream processing without asking the source to resend everything. I’d apply changes idempotently, monitor WAL and CDC lag, and define clear replay versus re-baseline criteria.

### Common Weak Answers

- Writing CDC directly into the final table with no replay boundary.
- Ignoring delete semantics.
- Deleting source replication state during an incident.

### Follow-Up Questions an Interviewer May Ask

1. How would you prove no changes were lost?
2. When would zero-ETL remove complexity?
3. How would Debezium/MSK change the design?

## Question 33 — Design a Kinesis/MSK streaming platform with replay

**Difficulty:** Advanced

**Primary Topics:** Kinesis, Firehose, MSK, Kafka, Debezium, S3, Iceberg

### Interview Question

Design a streaming platform for clickstream and operational events. The platform must support managed delivery to S3, custom consumers, and a Kafka-compatible CDC path for selected sources.

### Problem / Scenario

The company has both straightforward analytics delivery and teams that need richer Kafka ecosystem capabilities.

### What the Interviewer Is Evaluating

- Streaming architecture
- Kinesis versus MSK
- CDC
- Replay
- Schema evolution

### Expected Approach

1. Classify event types and consumer requirements.
2. Use Kinesis where AWS-managed stream semantics fit.
3. Use Firehose for managed delivery to S3 where appropriate.
4. Use MSK/Debezium where Kafka ecosystem and CDC flexibility justify it.
5. Define schema and replay strategy.
6. Monitor lag, hot shards/partitions, consumer health, and delivery.

### Solution / Model Answer

I would not force one streaming service onto every workload. Kinesis Data Streams is attractive for AWS-native managed streaming with explicit shard/consumer behavior, and Firehose can provide managed delivery to S3. MSK is appropriate when Kafka compatibility, ecosystem tooling, or Debezium-based CDC is a requirement. The platform should standardize event contracts, retention/replay boundaries, schema evolution, and observability while allowing these paths to coexist.

### How to Solve the Problem

#### Step 1 — Classify

Separate ordinary event streaming from CDC and Kafka-specific requirements.

#### Step 2 — Select

Use Kinesis for managed AWS-native streams and MSK where Kafka ecosystem control is material.

#### Step 3 — Deliver

Use Firehose for managed destination delivery where its semantics fit.

#### Step 4 — Operate

Define replay, schema, idempotency, lag, and failure procedures.

### Example

```text
Events -> Kinesis -> Firehose -> S3/Iceberg
CDC -> Debezium -> MSK -> consumers / S3/Iceberg
```

### Why This Is the Correct Approach

The architecture is a portfolio decision: managed simplicity and Kafka ecosystem flexibility solve different requirements.

### Production Considerations

- **Reliability:** Define replay, ordering, idempotency, and schema evolution.
- **Performance:** Monitor hot partitions/shards and consumer lag.
- **Cost:** Use the simplest streaming service that satisfies requirements.
- **Security:** Secure brokers, streams, data destinations, and network paths.

### Strong Interview Answer

> I’d use Kinesis plus Firehose for AWS-native managed event delivery and MSK/Debezium where Kafka or CDC requirements justify the added operational surface. I’d standardize event contracts and replay semantics across both paths.

### Common Weak Answers

- Choosing MSK because Kafka is popular.
- Using Firehose for workloads requiring custom stream semantics.
- Ignoring schema evolution.

### Follow-Up Questions an Interviewer May Ask

1. How would you choose Kinesis versus MSK for a new team?
2. How would you replay a failed day?
3. How would you handle a hot partition?

## Question 34 — Design a secure private AWS data platform

**Difficulty:** Advanced

**Primary Topics:** KMS, VPC, VPC Endpoints, PrivateLink, Glue, S3, Secrets Manager, Lake Formation

### Interview Question

Design a data platform in which processing and data access remain private, data is encrypted, and application secrets are not embedded in jobs.

### Problem / Scenario

The security team prohibits unnecessary public internet access and requires auditable least-privilege controls.

### What the Interviewer Is Evaluating

- Private architecture
- Encryption
- Identity
- Secrets
- Policy layering

### Expected Approach

1. Place compute in appropriate private subnets.
2. Use gateway/interface endpoints for supported AWS services.
3. Use KMS with deliberate key policies and grants.
4. Use Secrets Manager for credentials/secrets.
5. Align IAM, resource, endpoint, Lake Formation, and KMS policies.
6. Use CloudTrail/CloudWatch evidence to operate the environment.

### Solution / Model Answer

I would use private subnets for data-processing workloads, VPC endpoints for supported AWS service access, and PrivateLink where the service pattern requires it. S3 traffic can use a gateway endpoint; other service APIs may use interface endpoints. KMS customer-managed keys can provide controlled encryption, with key policies and IAM designed together. Secrets Manager should hold secrets rather than environment files or code. Finally, Lake Formation governs data access while CloudTrail and CloudWatch provide audit and operational evidence.

### How to Solve the Problem

#### Step 1 — Network

Design routes and endpoints so required data-plane traffic stays private.

#### Step 2 — Identity

Use IAM roles and least privilege rather than embedded credentials.

#### Step 3 — Encryption

Define KMS key ownership, policies, and service use.

#### Step 4 — Secrets

Retrieve credentials through Secrets Manager.

#### Step 5 — Govern

Align Lake Formation, S3, endpoint, IAM, and KMS policies.

#### Step 6 — Operate

Monitor access and failures through CloudTrail and CloudWatch.

### Example

```text
Private subnets
 -> gateway/interface endpoints -> AWS services
 -> KMS encryption
 -> Lake Formation/IAM authorization
 -> CloudTrail/CloudWatch evidence
```

### Why This Is the Correct Approach

Security is a system of aligned controls; a private subnet alone does not make a platform secure.

### Production Considerations

- **Security:** Least privilege, encryption, key-policy discipline, private traffic, and secret isolation.
- **Networking:** Choose endpoint type based on service and access pattern.
- **Observability:** Audit control-plane activity and monitor operational failures.
- **Cost:** Balance NAT elimination against interface-endpoint costs.

### Strong Interview Answer

> I’d make privacy, identity, encryption, and auditability explicit layers. Private subnets and endpoints protect network paths; IAM/Lake Formation govern access; KMS protects data; Secrets Manager protects credentials; CloudTrail and CloudWatch provide evidence.

### Common Weak Answers

- Putting secrets in job arguments or source code.
- Assuming private subnets automatically provide service connectivity.
- Using broad KMS permissions.

### Follow-Up Questions an Interviewer May Ask

1. What if an AWS service has no gateway endpoint?
2. How would you restrict an endpoint?
3. How would you troubleshoot a private timeout?

## Question 35 — Design an enterprise DataZone data-product operating model

**Difficulty:** Advanced

**Primary Topics:** DataZone, Glue Catalog, Lake Formation, Athena, Redshift, governance

### Interview Question

An enterprise has dozens of data domains and wants a governed self-service model for discovering, publishing, subscribing to, and using data products. Design the operating model.

### Problem / Scenario

The platform must support both technical metadata and business ownership without centralizing every access decision in one team.

### What the Interviewer Is Evaluating

- Data-product strategy
- Business metadata
- Technical governance
- Self-service operating model

### Expected Approach

1. Define domain ownership and product responsibilities.
2. Use DataZone for discovery, business metadata, publishing, and subscription workflows.
3. Use Glue Catalog for technical metadata and Lake Formation for enforceable access governance.
4. Define certification, quality, lifecycle, and ownership standards.
5. Measure adoption, quality, access, and operational outcomes.

### Solution / Model Answer

I would establish domain-owned data products with a common enterprise contract. DataZone would be the business-facing discovery and subscription layer, while Glue Catalog remains the technical metadata system and Lake Formation enforces access. Each product should have an owner, description, glossary terms, quality expectations, freshness, access policy, lifecycle, and support path. Self-service should mean standardized workflows, not uncontrolled permissions.

### How to Solve the Problem

#### Step 1 — Define ownership

Make every product accountable to a domain owner.

#### Step 2 — Standardize metadata

Require technical and business metadata before publication.

#### Step 3 — Govern access

Use subscription approval plus enforceable Lake Formation/IAM controls.

#### Step 4 — Operate products

Track quality, freshness, usage, incidents, and lifecycle.

#### Step 5 — Scale

Automate the common path while keeping exceptional approvals explicit.

### Example

```text
Domain owner -> publish data product -> DataZone discovery
Consumer -> subscribe -> governance approval -> technical access -> Athena/Redshift
```

### Why This Is the Correct Approach

The operating model scales because discovery, ownership, authorization, and serving are connected but not conflated.

### Production Considerations

- **Governance:** Use clear ownership and approval boundaries.
- **Data Quality:** Certification should reflect measurable quality expectations.
- **Security:** Subscriptions must map to enforceable technical permissions.
- **Operations:** Define support and lifecycle responsibilities per product.

### Strong Interview Answer

> I’d make each domain accountable for a data product, use DataZone for discovery and subscriptions, Glue Catalog for technical metadata, and Lake Formation for enforcement. The enterprise platform provides standards and automation; domains own the data and its quality.

### Common Weak Answers

- Centralizing all ownership in the platform team.
- Treating DataZone as the enforcement layer.
- Publishing datasets without ownership or quality expectations.

### Follow-Up Questions an Interviewer May Ask

1. How would you handle PII?
2. How would a product become certified?
3. How would you measure whether self-service is working?

## Question 36 — Design an event-driven data platform with controlled retries

**Difficulty:** Advanced

**Primary Topics:** EventBridge, Step Functions, Glue, Data Quality, S3, observability

### Interview Question

Design an event-driven platform where new data arrivals trigger processing, quality validation, and downstream publication. It must tolerate duplicate events and transient AWS failures.

### Problem / Scenario

Events may arrive more than once and a downstream service can occasionally fail.

### What the Interviewer Is Evaluating

- Event-driven architecture
- Idempotency
- Workflow orchestration
- Retry/Catch
- Observability

### Expected Approach

1. Use EventBridge for event routing and contract matching.
2. Use Step Functions for stateful workflow execution.
3. Make each processing step idempotent.
4. Use bounded retries for transient failures and Catch paths for terminal failures.
5. Record execution identifiers and input versions.
6. Monitor both event delivery and workflow execution.

### Solution / Model Answer

I would separate event routing from workflow state. EventBridge receives and routes the event, while Step Functions executes the processing graph. The workflow must be idempotent because duplicate events are normal in distributed systems. Retries should be bounded and targeted to transient errors; data-quality or validation failures should follow a non-retry path. The input batch identifier and execution context should be carried through the workflow so operators can correlate events with outputs.

### How to Solve the Problem

#### Step 1 — Contract

Define the event fields needed to identify the dataset and batch.

#### Step 2 — Route

Use EventBridge patterns to select the correct workflow.

#### Step 3 — Execute

Use Step Functions to sequence Glue, quality, and publication.

#### Step 4 — Protect

Make writes idempotent and separate transient from terminal failures.

#### Step 5 — Observe

Correlate event, execution, batch, and output identifiers.

### Example

```json
{
  "StartAt": "Process",
  "States": {
    "Process": {"Type": "Task", "Retry": [{"ErrorEquals": ["States.Timeout"], "MaxAttempts": 3}], "End": true}
  }
}
```

### Why This Is the Correct Approach

Event-driven systems become reliable when routing, state, idempotency, and failure classification are designed together.

### Production Considerations

- **Reliability:** Bound retries and design idempotent processing.
- **Observability:** Correlate event and workflow IDs.
- **Cost:** Avoid retry storms and uncontrolled parallel execution.
- **Data Quality:** Treat invalid data as a business/validation failure, not a transient infrastructure failure.

### Strong Interview Answer

> I’d use EventBridge for routing and Step Functions for stateful execution. Every processing step would be idempotent, retries would target transient errors only, and terminal failures would go to explicit handling. I’d carry batch identifiers through the workflow for operational correlation.

### Common Weak Answers

- Retrying every failure.
- Assuming events are delivered exactly once.
- Putting business validation errors into infrastructure retry loops.

### Follow-Up Questions an Interviewer May Ask

1. How would you deduplicate events?
2. When would Distributed Map be useful?
3. When would MWAA be preferable?

## Question 37 — Build a cost-optimized AWS data platform

**Difficulty:** Advanced

**Primary Topics:** Cost Explorer, CloudWatch, Athena, Glue, Redshift, Kinesis, EMR, VPC

### Interview Question

An AWS data platform has rising spend across Athena, Glue, Redshift, Kinesis, EMR, NAT, and CloudWatch. Design a cost-engineering approach without degrading required SLAs.

### Problem / Scenario

The platform has no reliable unit-economics model and teams disagree about which service is responsible for the increase.

### What the Interviewer Is Evaluating

- Cost attribution
- Unit economics
- Workload optimization
- Trade-offs
- Observability

### Expected Approach

1. Establish resource/team/service attribution.
2. Use Cost Explorer and workload telemetry to identify drivers.
3. Map each major service to a measurable unit.
4. Optimize the highest-value drivers first.
5. Validate that savings do not violate SLA, security, or reliability.
6. Create ongoing budgets and anomaly controls.

### Solution / Model Answer

I would first make cost attributable by service, workload, and owning domain. Then I would correlate Cost Explorer with service telemetry: Athena bytes scanned, Glue runtime/worker use, Redshift capacity/query behavior, Kinesis throughput, EMR runtime, NAT traffic, and CloudWatch log volume. I would define unit economics such as cost per TB processed or cost per analytical workload, optimize the largest drivers, and measure the trade-off. Cost optimization should be continuous, not a one-time cleanup.

### How to Solve the Problem

#### Step 1 — Attribute

Tag and categorize costs so teams can see ownership.

#### Step 2 — Measure

Connect spend to workload metrics and business units.

#### Step 3 — Optimize

Target data layout, compute capacity, network paths, and retention based on evidence.

#### Step 4 — Govern

Use budgets, alerts, and review thresholds.

#### Step 5 — Validate

Confirm savings while preserving SLA and security requirements.

### Example

```text
Cost Explorer -> identify driver
Service telemetry -> explain driver
Optimization -> measured before/after
Budget/anomaly controls -> prevent recurrence
```

### Why This Is the Correct Approach

Cost data alone says where money went; operational telemetry explains why.

### Production Considerations

- **Cost:** Use unit economics and measurable optimization.
- **Performance:** Avoid savings that create unacceptable latency.
- **Reliability:** Do not remove redundancy or recovery capacity blindly.
- **Security:** Do not weaken private networking or encryption solely for savings.

### Strong Interview Answer

> I’d combine Cost Explorer with service-level telemetry and assign cost ownership. Then I’d optimize the largest measurable drivers—data scanned, compute utilization, network paths, retention, or capacity—and validate both savings and SLA impact.

### Common Weak Answers

- Cutting resources uniformly.
- Optimizing based only on absolute spend.
- Removing security controls to save money.

### Follow-Up Questions an Interviewer May Ask

1. How would you reduce Athena spend?
2. How would you attack NAT cost?
3. How would you allocate shared Redshift cost?

## Question 38 — Diagnose a multi-layer production incident

**Difficulty:** Advanced

**Primary Topics:** Glue, KMS, VPC, Lake Formation, CloudWatch, CloudTrail, Athena

### Interview Question

A nightly pipeline fails after a security-policy change. The Glue job cannot publish curated data, Athena users report AccessDenied, and the team also sees longer runtimes. Walk through your incident response.

### Problem / Scenario

The change affected permissions and possibly network or encryption paths. Operators need to restore service without masking the root cause.

### What the Interviewer Is Evaluating

- Multi-layer incident response
- Evidence collection
- Security troubleshooting
- Performance isolation
- Recovery

### Expected Approach

1. Establish incident scope and recent changes.
2. Use CloudWatch logs/metrics and CloudTrail to identify policy changes and failures.
3. Separate network, IAM/Lake Formation, KMS, and compute symptoms.
4. Restore the minimum required access safely.
5. Validate pipeline output and query access.
6. Perform root-cause and regression analysis.

### Solution / Model Answer

I would treat the security-policy change as a leading hypothesis but not assume it explains every symptom. CloudTrail can establish what changed and when; CloudWatch/Glue logs can show whether the job is failing at access, encryption, network, or processing stages. I would compare a known-good role/path, identify the narrow missing permission or policy condition, restore it with least privilege, then rerun validation. The runtime regression would be analyzed separately unless evidence links it to the same change.

### How to Solve the Problem

#### Step 1 — Scope

Identify affected datasets, jobs, users, and the exact deployment/policy change.

#### Step 2 — Collect evidence

Use CloudTrail for control-plane change history and CloudWatch/Glue evidence for runtime symptoms.

#### Step 3 — Separate layers

Distinguish IAM/Lake Formation, KMS, networking, and Spark performance failures.

#### Step 4 — Recover

Apply the smallest safe policy correction and validate end to end.

#### Step 5 — Learn

Document root cause, prevention, and monitoring improvements.

### Example

```text
CloudTrail -> what changed?
CloudWatch/Glue -> where did execution fail?
Policies/KMS/VPC -> which control caused it?
Validation -> is the platform healthy again?
```

### Why This Is the Correct Approach

Senior incident response separates correlated symptoms from causal evidence and avoids broad emergency permissions.

### Production Considerations

- **Security:** Restore least-privilege access; avoid wildcard emergency grants.
- **Observability:** Correlate control-plane changes with runtime telemetry.
- **Reliability:** Use controlled rollback and validation.
- **Performance:** Treat runtime degradation as a separate hypothesis until evidence connects it.

### Strong Interview Answer

> I’d correlate the security change with CloudTrail and runtime evidence, then isolate whether the failures are IAM/Lake Formation, KMS, networking, or Spark-related. I’d restore the narrowest required permission, validate the pipeline and consumer access, and investigate any independent performance regression rather than assuming one cause explains everything.

### Common Weak Answers

- Rolling back everything without evidence.
- Granting AdministratorAccess.
- Assuming all symptoms have one root cause.

### Follow-Up Questions an Interviewer May Ask

1. How would you prove the KMS key policy is involved?
2. What would you look for in CloudTrail?
3. How would you prevent recurrence?

## Question 39 — Choose DMS, Zero-ETL, or Debezium for a migration

**Difficulty:** Advanced

**Primary Topics:** DMS, Zero-ETL, Debezium, MSK, Redshift, S3, Iceberg

### Interview Question

An enterprise wants to migrate operational database changes into analytics. Compare DMS, zero-ETL, and Debezium-based architecture and defend your choice for three different workload scenarios.

### Problem / Scenario

Scenario A needs a managed S3 CDC landing path. Scenario B needs a tightly integrated near-real-time analytics destination. Scenario C requires Kafka ecosystem control and custom CDC processing.

### What the Interviewer Is Evaluating

- CDC service selection
- Managed versus flexible architecture
- Destination requirements
- Operational trade-offs

### Expected Approach

1. Define source, target, latency, transformation, replay, and ecosystem requirements.
2. Choose DMS where managed migration/CDC and broad target patterns fit.
3. Choose zero-ETL where the supported managed source/destination integration directly matches the requirement.
4. Choose Debezium/MSK where Kafka ecosystem and custom CDC control justify operational complexity.
5. Define validation and recovery for each choice.

### Solution / Model Answer

DMS is attractive for managed full-load-plus-CDC migration and can target S3 and other supported destinations. Zero-ETL is compelling when the source/destination pair and managed near-real-time integration match the business requirement and reduce pipeline engineering. Debezium with MSK is appropriate when Kafka ecosystem control, custom transformations, or event-stream integration is central. The choice depends on supported integration, latency, transformation needs, operational ownership, and recovery requirements.

### How to Solve the Problem

#### Step 1 — Scenario A

For S3 CDC landing, prefer a managed DMS path when its target semantics and operational requirements fit.

#### Step 2 — Scenario B

For a supported managed source-to-analytics integration, evaluate zero-ETL to remove custom pipeline layers.

#### Step 3 — Scenario C

For Kafka-centric CDC and event-stream control, evaluate Debezium/MSK.

#### Step 4 — Validate

For all choices, define correctness, schema evolution, replay, monitoring, and recovery.

### Example

```text
Decision axes:
managed operations | target integration | latency | transformation | Kafka ecosystem | recovery | cost
```

### Why This Is the Correct Approach

The right answer is not the service with the most features; it is the architecture that minimizes total operational complexity for the required semantics.

### Production Considerations

- **Reliability:** Define replay, validation, and failure recovery.
- **Security:** Use encrypted, least-privilege paths and private connectivity where required.
- **Operations:** Compare who owns brokers, connectors, tasks, and upgrades.
- **Cost:** Include both service spend and engineering/operational cost.

### Strong Interview Answer

> I’d choose DMS when managed full-load/CDC and the required target are the main need, zero-ETL when a supported managed integration directly matches the destination and latency requirement, and Debezium/MSK when Kafka-centric flexibility is worth the operational overhead. I’d defend the decision using latency, transformation, recovery, security, and total operating cost.

### Common Weak Answers

- Choosing zero-ETL without checking supported integrations.
- Choosing Debezium without accounting for Kafka operations.
- Assuming DMS solves downstream table semantics automatically.

### Follow-Up Questions an Interviewer May Ask

1. How would you handle schema evolution?
2. How would you recover from CDC lag?
3. What evidence would change your service choice?

## Question 40 — Design the target AWS Data Engineering platform and defend every major choice

**Difficulty:** Advanced

**Primary Topics:** AWS service landscape, S3/Iceberg, Glue, Athena, Lake Formation, Redshift, Kinesis/MSK, EMR, orchestration, DMS, observability, KMS/VPC, DataZone

### Interview Question

You are the senior engineer responsible for designing an AWS data platform for an enterprise with batch ingestion, CDC, streaming, lakehouse analytics, warehouse workloads, governed data products, and strict security/cost requirements. Walk through the architecture and defend the major service choices.

### Problem / Scenario

The platform must support multiple teams and workloads without turning every use case into a bespoke stack.

### What the Interviewer Is Evaluating

- Staff-level architecture
- Service selection
- Cross-domain trade-offs
- Security/governance
- Reliability
- Cost

### Expected Approach

1. Clarify workload classes and SLAs.
2. Design separate but interoperable batch, CDC, streaming, lakehouse, and warehouse paths.
3. Use S3/Iceberg and Glue as appropriate for the lakehouse foundation.
4. Use Athena and Redshift according to workload characteristics.
5. Use Kinesis/MSK based on streaming requirements.
6. Use DMS/zero-ETL/Debezium based on CDC scenario.
7. Use Step Functions/EventBridge/MWAA according to orchestration needs.
8. Use Lake Formation/DataZone for governance/discovery.
9. Add KMS/private networking/Secrets Manager and CloudWatch/CloudTrail/Cost Explorer.
10. Define recovery, testing, ownership, and cost controls.

### Solution / Model Answer

My target platform would use a common S3/Iceberg lakehouse foundation with Glue Catalog and managed Glue processing for many batch workloads. Athena would serve ad-hoc lake queries, while Redshift would serve workloads requiring warehouse-style performance, concurrency, or serving characteristics. Kinesis and Firehose would cover AWS-native event streaming and managed delivery; MSK/Debezium would be reserved for Kafka-centric or CDC requirements that justify that complexity. DMS, zero-ETL, or Debezium would be selected per migration scenario. Step Functions/EventBridge/MWAA would be chosen based on orchestration style. Lake Formation would enforce data access and DataZone would provide enterprise discovery and data-product workflows. KMS, private endpoints, Secrets Manager, CloudWatch, CloudTrail, and cost controls would be platform-wide capabilities.

### How to Solve the Problem

#### Step 1 — Classify workloads

Separate batch, CDC, streaming, interactive analytics, warehouse, and governance requirements.

#### Step 2 — Build shared foundations

Standardize storage, catalog, identity, encryption, networking, and observability.

#### Step 3 — Choose services by workload

Use managed services where they reduce operations, but retain EMR/MSK/Kafka control where requirements justify it.

#### Step 4 — Design governance

Connect technical metadata, enforceable access, business discovery, and ownership.

#### Step 5 — Design operations

Define SLAs, quality gates, alerts, cost ownership, and recovery procedures.

#### Step 6 — Defend trade-offs

Explain why each service exists and why alternatives were not selected.

### Example

```text
Batch/CDC/Streaming sources
        -> S3/Iceberg + Glue Catalog/ETL
        -> Athena / Redshift
        -> Data products / analytics

Kinesis/Firehose or MSK -> streaming lakehouse
DMS/Zero-ETL/Debezium -> CDC paths
EventBridge/Step Functions/MWAA -> orchestration
Lake Formation + DataZone -> governance/discovery
KMS + VPC endpoints + Secrets Manager -> security
CloudWatch + CloudTrail + Cost Explorer -> operations
```

### Why This Is the Correct Approach

The strongest architecture is not the one with the most AWS services; it is the smallest coherent platform that covers the workload classes with explicit boundaries, governance, recovery, and cost ownership.

### Production Considerations

- **Architecture:** Use clear layers and service boundaries.
- **Scalability:** Separate workload classes and scale independently where needed.
- **Reliability:** Define replay, retries, idempotency, quality gates, and recovery.
- **Security:** Use least privilege, encryption, private networking, and governed access.
- **Observability:** Instrument data freshness, pipeline state, service health, audit events, and cost.
- **Cost:** Use workload-appropriate managed services and explicit unit economics.
- **Governance:** Give domains ownership while centralizing standards and controls.

### Strong Interview Answer

> I’d start by classifying workloads rather than choosing services. I’d build a shared S3/Iceberg and metadata foundation, use Athena and Redshift according to serving requirements, Kinesis/MSK according to streaming needs, DMS/zero-ETL/Debezium according to CDC requirements, and Step Functions/EventBridge/MWAA according to orchestration needs. Lake Formation and DataZone provide technical governance and business discovery. KMS, private networking, observability, and cost controls are platform-wide capabilities. Every choice would be justified against latency, scale, operational complexity, security, recovery, and cost.

### Common Weak Answers

- Designing a service catalog instead of an architecture.
- Using one service for every workload.
- Ignoring ownership, recovery, security, or cost.
- Defending choices with vendor features instead of workload requirements.

### Follow-Up Questions an Interviewer May Ask

1. What would you remove if the platform were too complex?
2. How would you phase the implementation?
3. Which workload would you prototype first and why?
4. How would you prove the architecture is production-ready?



---

# Interview Coverage Matrix

| Topic | Basic | Moderate | Hard | Advanced | Question IDs |
|---|---:|---:|---:|---:|---|
| AWS Service Landscape | ✓ | ✓ | — | ✓ | Q01, Q06, Q07, Q08, Q18, Q31, Q33, Q40 |
| S3 Tables | ✓ | — | ✓ | ✓ | Q03, Q29, Q31 |
| Glue Catalog | ✓ | ✓ | — | ✓ | Q02, Q11, Q16, Q19, Q20, Q31, Q32, Q35, Q40 |
| Glue ETL / DQ | ✓ | ✓ | ✓ | ✓ | Q04, Q12, Q18, Q22, Q31, Q36, Q38, Q40 |
| Athena | ✓ | ✓ | ✓ | ✓ | Q01, Q02, Q05, Q11, Q13, Q21, Q29, Q31, Q32, Q38, Q40 |
| Lake Formation | ✓ | ✓ | ✓ | ✓ | Q02, Q16, Q20, Q26, Q31, Q34, Q35, Q40 |
| Redshift | ✓ | ✓ | ✓ | ✓ | Q01, Q06, Q14, Q24, Q40 |
| Kinesis / Firehose / MSK | ✓ | ✓ | ✓ | ✓ | Q07, Q15, Q23, Q33, Q40 |
| EMR | ✓ | — | ✓ | ✓ | Q08, Q24, Q40 |
| Step Functions / EventBridge / MWAA | ✓ | ✓ | ✓ | ✓ | Q09, Q18, Q28, Q36, Q40 |
| DMS / Zero-ETL | ✓ | ✓ | ✓ | ✓ | Q10, Q19, Q25, Q32, Q39, Q40 |
| CloudWatch / CloudTrail / Cost | ✓ | — | ✓ | ✓ | Q05, Q21, Q22, Q23, Q24, Q25, Q28, Q30, Q31, Q37, Q38, Q40 |
| KMS / VPC / Private Networking | — | ✓ | ✓ | ✓ | Q17, Q26, Q27, Q30, Q34, Q38, Q40 |
| DataZone / Unified Studio | — | ✓ | ✓ | ✓ | Q20, Q26, Q31, Q35, Q40 |

## Interview Question Distribution

| Difficulty | Questions |
|---|---:|
| Basic | 10 |
| Moderate | 10 |
| Hard | 10 |
| Advanced | 10 |
| **Total** | **40** |

## Cross-Topic Coverage

The question set deliberately combines the curriculum's major engineering boundaries:

- S3 + Glue + Athena
- Glue + Iceberg + Data Quality
- Redshift + distribution/sorting/workload management + Spectrum
- Kinesis + Firehose + S3
- Kinesis + MSK + Debezium
- DMS + PostgreSQL WAL + Iceberg
- Step Functions + EventBridge + Glue + Data Quality
- Lake Formation + Athena + DataZone
- KMS + VPC endpoints + Glue + S3
- EMR + Spark + Iceberg + Glue Catalog
- CloudWatch + CloudTrail + Cost Explorer with production diagnosis

## Interview Preparation Strategy

### Before the interview

- Be able to draw the major AWS data-platform reference architectures from memory.
- Know the responsibility boundary of every major service in this module.
- Practice choosing a service from workload requirements rather than from a memorized feature list.
- Be able to explain catalog versus authorization, event routing versus workflow orchestration, streaming versus managed delivery, and business discovery versus technical enforcement.
- Practice troubleshooting from **symptom → evidence → root cause → fix → validation**.
- Practice cost discussions using measurable drivers rather than unsupported price claims.

### During architecture questions

Start with:

1. Requirements and constraints.
2. Data sources and expected volume/rate.
3. Latency and freshness.
4. Storage and data model.
5. Processing.
6. Catalog and governance.
7. Serving/query requirements.
8. Security and network boundaries.
9. Observability and cost.
10. Failure recovery and operational ownership.

Then defend the selected services and explicitly state the important trade-offs.

### During troubleshooting questions

Avoid jumping directly to a fix. Establish:

- What changed?
- What is the exact symptom?
- Which component is the first failing boundary?
- What metrics/logs/trails prove that?
- Is the problem network, authorization, compute, data quality, throughput, or orchestration?
- What is the smallest safe remediation?
- How will you validate recovery?
- What guardrail prevents recurrence?

### During senior-level interviews

A strong answer sounds like engineering judgment:

> “I would first clarify the workload and constraints. Then I would identify the service boundary that best fits those requirements, explain the trade-off against the closest alternative, and design observability and recovery into the solution. I would validate the decision with a representative workload rather than relying on a generic service comparison.”

## Final Self-Assessment

You are interview-ready for this module when you can:

- Explain all 14 topic areas without relying on memorized definitions.
- Draw an S3/Iceberg/Glue/Athena lakehouse and explain each layer.
- Defend Athena versus Redshift for a given workload.
- Explain S3 Tables versus general-purpose S3 plus Iceberg.
- Explain Glue Catalog versus Lake Formation versus DataZone.
- Diagnose a slow Glue job using Spark and service evidence.
- Diagnose Kinesis lag and distinguish hot-shard problems from consumer/downstream bottlenecks.
- Explain EMR Serverless versus EMR on EC2 versus EMR on EKS.
- Choose Step Functions versus MWAA and EventBridge versus workflow orchestration.
- Explain DMS full load + CDC, PostgreSQL WAL/replication-slot risks, and recovery.
- Compare DMS, zero-ETL, and Debezium using workload requirements.
- Troubleshoot KMS/VPC endpoint/private-subnet access problems without resorting to broad permissions.
- Design governed DataZone/Lake Formation data products.
- Connect CloudWatch, CloudTrail, and Cost Explorer evidence during incidents.
- Discuss security, reliability, performance, governance, and cost as first-class architecture concerns.
- Answer follow-up challenges without changing the original decision unless new evidence changes the requirements.

## Final Quality Audit

- [x] Exactly 10 Basic questions.
- [x] Exactly 10 Moderate questions.
- [x] Exactly 10 Hard questions.
- [x] Exactly 10 Advanced questions.
- [x] Exactly 40 questions total.
- [x] All 14 AWS Data Engineering Deep Dive topics represented.
- [x] Every question presents the interview question before the solution.
- [x] Scenario-based reasoning is used throughout.
- [x] Hard and Advanced levels contain substantial troubleshooting and cross-topic reasoning.
- [x] Advanced questions require architecture and service-selection defense.
- [x] Strong Interview Answer included for every question.
- [x] Common weak-answer patterns included for every question.
- [x] Follow-up questions included for every question.
- [x] Architecture, security, observability, cost, governance, reliability, and performance are covered.
- [x] The question set is interview-oriented rather than a certification question bank.
- [x] No additional Markdown artifacts are required for this interview bank.
