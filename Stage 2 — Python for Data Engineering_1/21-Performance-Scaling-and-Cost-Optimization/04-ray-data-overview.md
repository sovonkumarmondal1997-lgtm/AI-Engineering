# Claude Code Prompt — Build `04-ray-data-overview.md`

## ROLE

Act as a **Senior Data Engineer with 10+ years of production industry experience**, specializing in:

- Large-scale data engineering
- Distributed systems
- Python data platforms
- Apache Spark
- Dask
- Ray and Ray Data
- ML/data preprocessing pipelines
- Batch inference systems
- Distributed compute
- Performance engineering
- Production data pipelines
- Cloud and Kubernetes-based data platforms

You are also an expert technical educator.

Your job is to create a **production-oriented learning module** that teaches Ray and Ray Data from **fundamentals → intermediate → advanced concepts**, using simple explanations first and progressively introducing distributed-systems terminology, architecture, trade-offs, implementation details, and production patterns.

---

# TASK

You are working inside:

```text
21-Performance-Scaling-and-Cost-Optimization/
```

The target file is:

```text
04-ray-data-overview.md
```

Your task is to **write/update ONLY**:

```text
04-ray-data-overview.md
```

### ABSOLUTE FILE-SCOPE RULE

Do **NOT** modify, create, rename, delete, or reorganize any other file or folder.

Do not modify:

```text
README.md
01-estimating-data-size-and-memory-footprint.md
02-predicate-pushdown-and-projection-pruning.md
03-parallel-dataframes-with-dask.md
05-numba-and-cython-for-hot-loops.md
06-benchmarking-pipelines.md
07-compute-cost-optimization.md
practice-questions.md
```

Only:

```text
04-ray-data-overview.md
```

may be changed.

---

# SOURCE OF TRUTH

The authoritative source is the **Module 2.21 — Performance, Scaling, and Cost Optimization roadmap**.

The roadmap places Ray Data in:

```text
Phase B — Scale Out Python
```

after Dask and before Numba/Cython.

The overall optimization ladder is:

```text
1. Do less work
        ↓
2. Use a better engine
        ↓
3. Use more cores
        ↓
4. Use more machines → Dask / Ray / Spark
        ↓
5. Compile hot loops
```

Therefore, do NOT teach Ray as simply "another Python library."

Teach it as a **distributed execution system used when a workload genuinely benefits from distributed Python execution**, especially ML/data workloads.

The roadmap explicitly positions Ray as:

> A general distributed Python framework widely used for ML and AI workloads.

And Ray Data as the component for:

- large-scale data loading
- preprocessing
- batch inference
- bridging data engineering and ML

This positioning must remain clear throughout the file.

---

# PRIMARY LEARNING OBJECTIVE

By the end of this file, the learner must be able to:

1. Explain what Ray is.
2. Explain why Ray exists.
3. Understand Ray's distributed execution model.
4. Explain **tasks**.
5. Explain **actors**.
6. Explain Ray's distributed **object store**.
7. Start Ray locally.
8. Use the Ray dashboard.
9. Understand Ray Data datasets.
10. Read Parquet with Ray Data.
11. Read CSV with Ray Data.
12. Understand image ingestion with Ray Data.
13. Transform data using `map_batches`.
14. Understand batches represented as:
    - pandas DataFrames
    - PyArrow Tables
    - NumPy arrays
15. Understand Ray Data's streaming execution model.
16. Understand blocks and stage-to-stage data flow.
17. Understand back pressure.
18. Understand CPU and GPU resource allocation.
19. Understand mixed CPU/GPU pipelines.
20. Understand stateful batch processing.
21. Understand actor pools.
22. Understand why models should be loaded once per actor rather than once per batch.
23. Understand ML preprocessing workloads.
24. Understand batch inference workloads.
25. Understand embedding-generation workloads.
26. Understand feeding training jobs.
27. Write Ray Data outputs to Parquet.
28. Understand lakehouse-table integration at an architectural level.
29. Understand orchestration integration.
30. Understand Ray cluster deployment at an awareness level.
31. Understand Kubernetes-based Ray deployment at an awareness level.
32. Understand autoscaling.
33. Compare Ray Data against Spark.
34. Compare Ray Data against Dask.
35. Know when Ray Data is the correct choice.
36. Know when Ray Data is the wrong choice.
37. Understand why Ray Data is **not a SQL engine**.
38. Recognize when heavy relational workloads belong in:
    - Spark
    - DuckDB
    - a warehouse
39. Build a complete production-style Ray Data pipeline.
40. Measure throughput, batch size, actor count, and memory behavior.
41. Reason about resource utilization and performance.
42. Make an engineering decision between Ray Data, Spark, and Dask.

Do not skip any of these roadmap concepts.

---

# IMPORTANT PREREQUISITE BOUNDARY

This module is part of Stage 2 and assumes the learner has already studied:

- Python
- pandas
- PyArrow
- Parquet
- distributed-computing fundamentals
- concurrency and parallelism
- Spark
- Dask
- data pipeline architecture
- orchestration
- testing
- observability

Do **not** completely reteach those subjects.

However, if a prerequisite is necessary to understand Ray, give a **short contextual explanation** before using it.

For example:

> "A distributed task means a unit of work that Ray can schedule on another worker process or machine."

Do not turn prerequisite concepts into separate full modules.

---

# TEACHING PHILOSOPHY

Teach every concept using this progression:

```text
WHAT
 ↓
WHY
 ↓
HOW
 ↓
CODE
 ↓
WHAT HAPPENS INTERNALLY
 ↓
PERFORMANCE IMPLICATION
 ↓
FAILURE MODES
 ↓
PRODUCTION USE
 ↓
WHEN NOT TO USE IT
```

Use simple language first.

Then introduce the correct engineering terminology.

For every important concept, answer:

- What is it?
- Why does it exist?
- What problem does it solve?
- How does it work?
- What happens internally?
- What does the code look like?
- What happens to memory?
- What happens to CPU/GPU resources?
- What happens when the workload becomes larger?
- What can go wrong?
- When should a production engineer use it?
- When should they avoid it?

---

# REQUIRED DOCUMENT STRUCTURE

Build the Markdown file using a logical progression similar to:

```text
1. Module Overview
2. Why Ray Exists
3. Ray vs Traditional Python Execution
4. Ray Architecture
5. Ray Core Fundamentals
6. Ray Tasks
7. Ray Actors
8. Ray Object Store
9. Starting Ray Locally
10. Ray Dashboard
11. Ray Data Overview
12. Ray Data Dataset / Block Model
13. Reading Parquet
14. Reading CSV
15. Reading Images
16. map_batches
17. Batch Formats
18. Streaming Execution
19. Back Pressure
20. CPU and GPU Resources
21. Mixed CPU + GPU Pipelines
22. Actor Pools
23. Stateful Batch Processing
24. ML Preprocessing
25. Batch Inference
26. Embedding Generation
27. Feeding Training Jobs
28. Writing Parquet Outputs
29. Lakehouse Integration
30. Orchestration Integration
31. Ray Cluster Deployment
32. Kubernetes and Autoscaling Awareness
33. Ray Data vs Spark vs Dask
34. Ray Data Limitations
35. Production Design Patterns
36. Complete End-to-End Project
37. Performance Tuning Exercise
38. Failure Injection and Debugging
39. Production Decision Framework
40. Checkpoint
41. Practice / Interview Questions
42. Final Roadmap Coverage Audit
```

You may adjust the exact headings if necessary, but **all roadmap concepts must be covered**.

---

# SECTION 1 — MODULE OVERVIEW

Start by explaining:

### What is Ray?

Explain Ray as a distributed Python framework.

Use a simple conceptual model such as:

```text
Python program
      ↓
Ray
      ↓
Tasks / Actors
      ↓
Distributed workers
      ↓
CPU / GPU resources
      ↓
Results / Objects
```

Explain why normal Python/pandas processing eventually encounters limitations.

Explain why distributed execution becomes useful.

Then explain:

```text
Ray Core
    ↓
Ray Data
    ↓
ML / AI data workloads
    ↓
Batch inference / embeddings / training pipelines
```

Make the bridge between Data Engineering and ML explicit.

---

# SECTION 2 — WHY RAY EXISTS

Explain the problem Ray solves.

Compare:

```text
Single Python process
        ↓
multiprocessing
        ↓
Dask
        ↓
Spark
        ↓
Ray
```

Do not make this a generic distributed-computing lecture.

Focus specifically on Ray's strengths:

- Python-native distributed execution
- tasks
- actors
- stateful workers
- CPU/GPU scheduling
- ML/AI-oriented workflows
- batch inference
- model-serving/preprocessing ecosystem
- custom Python logic

Explain that Ray is particularly useful when Python and ML/AI workloads are first-class requirements.

---

# SECTION 3 — RAY CORE ARCHITECTURE

Explain the major components conceptually.

At minimum cover:

```text
Driver
Workers
Tasks
Actors
Object references
Distributed object store
Scheduler
Resources
Ray cluster
```

Create an architecture diagram in ASCII/Markdown if useful.

For example:

```text
                 Driver
                   |
             Ray Scheduler
             /           \
        Worker A       Worker B
          |               |
       Task 1          Actor A
          |               |
      Object Ref      Model State
          \               /
           Distributed Object Store
```

Explain what each component does.

---

# SECTION 4 — RAY TASKS

Teach tasks from absolute basics.

Explain:

- normal Python function
- Ray remote function
- task submission
- asynchronous execution
- object references
- retrieving results

Use concrete code.

Example concept:

```python
import ray

ray.init()

@ray.remote
def square(x):
    return x * x

future = square.remote(10)

result = ray.get(future)

print(result)
```

Explain every line.

Then progressively show:

- multiple tasks
- parallel task execution
- passing arguments
- returning results
- task dependencies
- task failures
- resource requirements

Show:

```python
@ray.remote(num_cpus=2)
def process_partition(data):
    ...
```

Explain what the resource annotation means.

Do not just provide code; explain the execution model.

---

# SECTION 5 — RAY ACTORS

Explain actors as:

> Stateful workers that keep state between method calls.

Start with a simple example.

```python
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value
```

Then:

```python
counter = Counter.remote()

print(ray.get(counter.increment.remote()))
print(ray.get(counter.increment.remote()))
```

Explain why this is different from tasks.

Explicitly compare:

| Task | Actor |
|---|---|
| Usually stateless | Stateful |
| Function-oriented | Object-oriented |
| Work is submitted | Worker keeps state |
| Good for independent computation | Good for reusable state/resources |
| Model reload may happen repeatedly if poorly designed | Model can remain loaded |

Connect actors directly to model-based batch processing.

---

# SECTION 6 — DISTRIBUTED OBJECT STORE

Explain:

- what an object reference is
- where large objects live
- why the object store exists
- how workers exchange data
- serialization/deserialization
- memory implications
- object lifetime
- large-object problems
- avoiding unnecessary copies

Use simple examples.

Explain:

```python
ref = some_task.remote(...)
```

does not immediately return the actual Python value.

It returns an object reference.

Then explain:

```python
result = ray.get(ref)
```

retrieves the actual value.

Discuss why excessive `ray.get()` calls can hurt pipeline design.

Also explain why large objects can create memory pressure.

---

# SECTION 7 — STARTING RAY LOCALLY

Show how to start Ray locally.

Cover:

```python
ray.init()
```

Explain:

- local mode
- local Ray runtime
- CPU discovery
- resource discovery
- shutdown

Show useful inspection concepts such as:

```python
ray.cluster_resources()
ray.available_resources()
```

Explain what these are useful for.

Include a small runnable local exercise.

---

# SECTION 8 — RAY DASHBOARD

Teach the dashboard.

Explain:

- why dashboards matter
- task execution
- workers
- actors
- resource utilization
- memory
- failures
- object store behavior

Show how the learner can start Ray and inspect the dashboard.

Do not invent unsupported UI details.

Describe dashboard capabilities conceptually and instruct the learner to inspect the actual version installed.

Make dashboard observation part of the practical lab.

---

# SECTION 9 — RAY DATA FUNDAMENTALS

Now transition from Ray Core to Ray Data.

Explain:

```text
Ray Core
   ↓
distributed execution primitives

Ray Data
   ↓
distributed data processing abstraction
```

Explain what a Ray Data Dataset is.

Explain:

- datasets
- blocks
- distributed data
- lazy/streaming execution
- reading data
- transformations
- execution stages

Make the relationship clear:

```text
Source files
    ↓
Ray Data Dataset
    ↓
Blocks
    ↓
Transformations
    ↓
Streaming execution
    ↓
Output
```

---

# SECTION 10 — READING PARQUET

Teach reading Parquet.

Use realistic code such as:

```python
import ray

ds = ray.data.read_parquet("data/products/")
```

Then explain:

- what happens
- how files are discovered
- how data becomes blocks
- distributed reading
- schema
- columnar storage
- why Parquet is useful for Ray Data

Show how to inspect the dataset.

Do not rely on deprecated APIs.

Use APIs appropriate to the currently installed Ray version.

---

# SECTION 11 — READING CSV

Show CSV ingestion.

Explain:

- why CSV is convenient
- why CSV is generally less efficient than Parquet
- parsing overhead
- schema inference
- distributed ingestion
- when CSV is appropriate

Example:

```python
ds = ray.data.read_csv("data/products.csv")
```

Then compare:

```text
CSV
 ↓
parse text
 ↓
construct typed values

Parquet
 ↓
columnar binary representation
 ↓
selective efficient reading
```

---

# SECTION 12 — READING IMAGES

The roadmap explicitly requires image ingestion.

Teach:

- why image workloads are different
- binary/object data
- image decoding
- batch processing
- ML preprocessing

Use a small example showing how image datasets can be loaded and transformed.

Do not create an unnecessarily complex computer-vision curriculum.

The goal is to establish why Ray Data is useful for ML-oriented data pipelines.

---

# SECTION 13 — `map_batches`

This is one of the most important concepts.

Teach:

```python
ds.map_batches(...)
```

from basics to advanced usage.

Explain:

- why batch processing exists
- batch size
- function-based transformations
- batch format
- output format
- parallelism
- memory implications
- CPU/GPU resources

Show examples with:

### pandas

```python
def transform(batch):
    ...
    
ds.map_batches(transform, batch_format="pandas")
```

### PyArrow

Show the equivalent concept.

### NumPy

Show the equivalent concept where appropriate.

Explain when each representation is useful.

---

# SECTION 14 — STREAMING EXECUTION

This is a mandatory intermediate concept.

Explain Ray Data's streaming execution model.

Start with:

```text
Traditional materialization:

Input
 ↓
load everything
 ↓
materialize everything
 ↓
transform
 ↓
output
```

Then:

```text
Ray Data streaming:

Input
 ↓
Block 1 → Transform → Output
Block 2 → Transform → Output
Block 3 → Transform → Output
       ...
```

Explain why streaming can:

- reduce peak memory
- overlap stages
- improve pipeline throughput
- allow large datasets to be processed without fully materializing everything

Explain that streaming does **not** mean "no memory usage."

Discuss:

- block sizes
- buffers
- operator state
- intermediate data
- back pressure

---

# SECTION 15 — BACK PRESSURE

Explain back pressure in simple terms.

Use a producer/consumer analogy.

For example:

```text
Fast producer
      ↓
████████████████
      ↓
Slow consumer
```

Eventually buffers fill.

Back pressure prevents the producer from continuing indefinitely.

Then relate it to:

```text
Read
 ↓
Preprocess
 ↓
Inference
 ↓
Write
```

If inference is slower than reading:

```text
Reader → Preprocessor → Inference
   fast       fast          slow
```

the system must avoid unlimited buffering.

Explain how this matters for:

- memory
- throughput
- stability
- GPU utilization

---

# SECTION 16 — RESOURCE MANAGEMENT

Teach resource-aware execution.

Cover:

```text
CPU
GPU
memory awareness
resource annotations
resource scheduling
```

Show examples such as:

```python
ds.map_batches(
    preprocess,
    num_cpus=2,
)
```

And GPU-oriented processing where appropriate.

Explain:

```text
CPU preprocessing
       ↓
GPU inference
       ↓
CPU postprocessing
```

This mixed-resource pipeline is explicitly required by the roadmap.

Explain why resource allocation matters.

Discuss:

- under-utilization
- oversubscription
- GPU starvation
- CPU bottlenecks
- batch-size interactions
- memory pressure

---

# SECTION 17 — ACTOR POOLS

This is a critical Ray Data concept.

Explain the problem first.

Bad pattern:

```text
Batch 1 → load model → inference → destroy
Batch 2 → load model → inference → destroy
Batch 3 → load model → inference → destroy
```

Explain why this is inefficient.

Then show:

```text
Actor 1
  └── model loaded once
      ├── batch 1
      ├── batch 4
      └── batch 7

Actor 2
  └── model loaded once
      ├── batch 2
      ├── batch 5
      └── batch 8

Actor 3
  └── model loaded once
      ├── batch 3
      ├── batch 6
      └── batch 9
```

Explain actor pools as stateful batch processors.

Teach the appropriate Ray Data pattern for actor-based batch processing using the current supported Ray APIs.

Do not invent API signatures.

If APIs vary by Ray version, explicitly state that the learner should verify the installed version's documentation/API.

---

# SECTION 18 — MODEL LOADING PATTERN

Explicitly teach this production principle:

> Load the model once per actor, not once per batch.

Show the incorrect implementation.

Then show the corrected actor-based design.

Explain:

- model initialization cost
- memory reuse
- model warm-up
- concurrency
- actor count
- CPU/GPU allocation
- batch size

Explain how actor count affects:

```text
parallelism
memory usage
model copies
GPU utilization
startup cost
```

This should be one of the key takeaways of the file.

---

# SECTION 19 — ML PREPROCESSING

Show realistic ML preprocessing examples.

Examples may include:

- text normalization
- tokenization preparation
- feature extraction
- image preprocessing
- structured feature transformations

Keep the focus on Ray Data rather than teaching ML itself.

Show:

```text
Parquet
 ↓
Ray Data
 ↓
CPU preprocessing
 ↓
batch transformation
 ↓
model-ready records
 ↓
Parquet / training system
```

Explain why Ray Data is useful here.

---

# SECTION 20 — BATCH INFERENCE

Build a realistic batch inference pipeline.

For example:

```text
Product descriptions
        ↓
Parquet
        ↓
Ray Data
        ↓
Text cleaning
        ↓
Model actor pool
        ↓
Predictions
        ↓
Parquet
```

Explain:

- loading the model
- actor reuse
- batching
- CPU/GPU allocation
- output schema
- throughput
- memory
- failure handling

Provide runnable code.

Prefer a lightweight model or deterministic demonstration if external model downloads would make the example unreliable.

---

# SECTION 21 — EMBEDDING GENERATION

The roadmap explicitly connects Ray Data with embedding generation.

Explain the architecture:

```text
Documents
   ↓
Ray Data
   ↓
Batch preprocessing
   ↓
Embedding model actors
   ↓
Embeddings
   ↓
Parquet / vector pipeline
```

Do not turn this into a complete vector database module.

Focus on:

- distributed preprocessing
- model reuse
- batch inference
- throughput
- resource allocation

Explain that deeper embedding workflows belong to later AI/data modules.

---

# SECTION 22 — FEEDING TRAINING JOBS

Explain how Ray Data can prepare data for training workloads.

Conceptually:

```text
Raw Data
   ↓
Ray Data
   ↓
Cleaning
   ↓
Feature preparation
   ↓
Training-ready data
   ↓
Training system
```

Discuss:

- preprocessing
- batching
- sharding/partitioning concepts
- output formats
- avoiding unnecessary materialization

Keep this at the appropriate architecture level.

---

# SECTION 23 — WRITING OUTPUTS

Teach writing Ray Data results.

At minimum demonstrate Parquet output.

Example concept:

```python
ds.write_parquet("output/products/")
```

Explain:

- output partitions/files
- parallel writes
- schema
- downstream consumption
- small-file considerations
- lakehouse integration considerations

Also explain conceptually how Ray Data can feed lakehouse/table-oriented workflows without turning this file into a complete lakehouse module.

---

# SECTION 24 — ORCHESTRATION INTEGRATION

The roadmap requires integration with orchestration from Module 2.13.

Show a conceptual pipeline:

```text
Orchestrator
      ↓
Ray Data job
      ↓
Read data interval
      ↓
Preprocess
      ↓
Batch inference
      ↓
Write results
      ↓
Success / failure
```

Explain:

- data interval
- idempotency
- retries
- logging
- output locations
- job boundaries
- resource configuration

If an exact orchestration framework is demonstrated, keep it consistent with the roadmap's existing ecosystem.

Do not redesign Module 2.13.

---

# SECTION 25 — RAY CLUSTERS

Teach cluster concepts at an awareness level.

Explain:

```text
Ray head/control components
        ↓
Worker nodes
        ↓
CPU/GPU resources
        ↓
Tasks / actors
```

Explain:

- local cluster
- multi-node cluster
- scheduling
- resource discovery
- workers
- scaling

Do not turn this into a Kubernetes administration module.

---

# SECTION 26 — KUBERNETES AND AUTOSCALING

The roadmap explicitly requires awareness of deploying Ray clusters, including Kubernetes with an operator, and autoscaling.

Explain conceptually:

```text
Kubernetes
    ↓
Ray cluster
    ↓
Head / worker pods
    ↓
CPU/GPU resources
    ↓
Autoscaling
```

Explain:

- why Kubernetes is used
- worker scaling
- resource requests/limits
- GPU nodes
- autoscaling
- operational complexity

Keep this as **architecture/deployment awareness**, not an exhaustive Kubernetes tutorial.

Do not invent exact operator manifests unless you can verify the current API.

---

# SECTION 27 — RAY DATA VS DASK VS SPARK

This is a mandatory advanced section.

Create a serious engineering comparison.

Use a table similar to:

| Dimension | Ray Data | Dask | Spark |
|---|---|---|---|
| Primary strength | | | |
| Python-native custom logic | | | |
| ML/AI workloads | | | |
| GPU workloads | | | |
| SQL/relational ETL | | | |
| Large joins | | | |
| Aggregations | | | |
| Stateful model processing | | | |
| Batch inference | | | |
| Ecosystem | | | |
| Operational maturity | | | |
| Best fit | | | |
| Poor fit | | | |

Explain the decision framework rather than declaring one universally superior.

Use examples such as:

### Workload A

Large SQL-style ETL with joins and aggregations.

Which engine?

Explain why.

### Workload B

Python-heavy ML preprocessing with GPU inference.

Which engine?

Explain why.

### Workload C

Pandas-like transformations that need distributed execution.

Which engine?

Explain why.

### Workload D

Single-machine dataset that fits comfortably in memory.

Explain why distributed Ray may be unnecessary.

---

# SECTION 28 — RAY DATA LIMITATIONS

Explicitly teach that:

> Ray Data is not a SQL engine.

Explain why this matters.

Discuss workloads where Ray Data may be a poor fit:

- heavy relational joins
- complex SQL transformations
- large aggregations
- warehouse-centric analytics
- workloads better handled by Spark
- workloads that fit efficiently in DuckDB/Polars on one machine

Explain the decision:

```text
Can a better single-node engine solve it?
        ↓
YES → don't distribute unnecessarily

NO
 ↓
Does distributed Python/custom logic dominate?
        ↓
YES → consider Dask/Ray

Does SQL-style relational processing dominate?
        ↓
YES → consider Spark/warehouse
```

---

# SECTION 29 — PERFORMANCE ENGINEERING

Because this file belongs to the Performance, Scaling, and Cost Optimization module, performance must not be treated as an afterthought.

Teach how to measure:

- throughput
- rows/sec
- batches/sec
- latency per batch
- CPU utilization
- GPU utilization
- memory usage
- actor utilization
- startup/model-load overhead

Show how to benchmark:

```text
baseline
   ↓
change batch size
   ↓
measure
   ↓
change actor count
   ↓
measure
   ↓
compare
```

Do not optimize blindly.

Use the module's performance loop:

```text
Estimate
→ Baseline
→ Profile
→ Change one thing
→ Verify correctness
→ Measure again
→ Price
→ Document
```

---

# SECTION 30 — BATCH SIZE TUNING

Teach why batch size matters.

Explain the trade-off:

```text
Small batches
    ↓
lower memory
higher overhead
possibly lower throughput

Large batches
    ↓
better amortization
higher memory
possible OOM
```

Discuss:

- CPU workloads
- GPU workloads
- model inference
- memory pressure
- throughput

Create a practical experiment where the learner measures several batch sizes.

---

# SECTION 31 — ACTOR COUNT TUNING

Explain how actor count affects:

```text
parallelism
model copies
memory
CPU/GPU utilization
startup overhead
throughput
```

Give a practical experiment.

For example:

```text
1 actor
2 actors
4 actors
```

Measure:

```text
runtime
throughput
peak memory
resource utilization
```

The learner must write a conclusion rather than simply selecting the fastest number.

---

# SECTION 32 — FAILURE MODES

Include realistic failures.

At minimum demonstrate or explain:

### Failure 1 — Model loaded per batch

Explain the performance problem.

### Failure 2 — Huge batch

Show how memory pressure can occur.

### Failure 3 — Too many actors

Explain resource oversubscription and memory multiplication.

### Failure 4 — GPU starvation

Explain how slow CPU preprocessing can leave GPUs idle.

### Failure 5 — Excessive materialization

Explain unnecessary memory pressure.

### Failure 6 — Using Ray Data for heavy relational workloads

Explain why architecture selection is wrong.

### Failure 7 — Poor output layout

Explain small-file/output management concerns.

### Failure 8 — Distributed execution overhead dominates

Explain why a single-node engine can sometimes win.

For each failure explain:

```text
Symptom
→ Root cause
→ Diagnosis
→ Fix
→ Prevention
```

---

# SECTION 33 — DEBUGGING WORKFLOW

Teach a practical debugging workflow.

For example:

```text
1. Confirm correctness
2. Measure runtime
3. Inspect Ray dashboard
4. Check CPU utilization
5. Check GPU utilization
6. Check memory
7. Inspect batch size
8. Inspect actor count
9. Inspect stage throughput
10. Identify bottleneck
11. Change one variable
12. Benchmark again
```

Explain how to reason from observations rather than guesses.

---

# SECTION 34 — COMPLETE END-TO-END HANDS-ON PROJECT

Build the roadmap's required project under the conceptual path:

```text
workloads/ray/
```

Do not create this directory unless the user explicitly asks for project files; inside this learning document, provide the project specification and commands/code necessary for the learner to implement it.

The project must:

1. Read product descriptions from Parquet.
2. Clean text in CPU batches.
3. Compute embeddings using a small model inside an actor pool.
4. Use CPU if no GPU is available.
5. Use GPU if available.
6. Write embeddings/results to Parquet.
7. Tune batch size.
8. Tune actor count.
9. Measure throughput.
10. Measure memory.
11. Observe the Ray dashboard.
12. Compare with Spark pandas UDFs.
13. Compare:
    - code complexity
    - throughput
    - resource usage
14. Trigger the pipeline from an orchestration task with a data interval.
15. Produce a decision note choosing Ray Data, Spark, or Dask for three workloads.

Provide the complete implementation path.

---

# SECTION 35 — SPARK COMPARISON PROJECT

The roadmap explicitly requires comparison against Spark pandas UDFs.

Teach the learner how to construct a fair comparison.

Control:

- same input data
- same transformation
- same output
- same correctness requirements
- comparable resource allocation
- comparable warm/cold conditions

Measure:

```text
runtime
throughput
CPU
memory
GPU if applicable
code complexity
operational complexity
```

Explain why benchmarks must be fair.

Do not manufacture benchmark numbers.

The learner must run the benchmark and record real results.

---

# SECTION 36 — PRODUCTION DECISION FRAMEWORK

Create a practical decision tree.

Example:

```text
Does the dataset fit comfortably on one machine?
        |
       YES
        ↓
Can Polars / DuckDB solve it efficiently?
        |
       YES → Use single-node engine
        |
       NO
        ↓
Is the workload pandas-like/custom Python?
        |
       YES → Consider Dask
        |
       NO
        ↓
Is it ML/AI-heavy, GPU-heavy, or model-inference-heavy?
        |
       YES → Consider Ray Data
        |
       NO
        ↓
Is it SQL-heavy with joins/aggregations?
        |
       YES → Consider Spark / warehouse
```

Make clear that this is a heuristic, not an absolute law.

---

# SECTION 37 — PRODUCTION DESIGN PRINCIPLES

End the technical material with principles such as:

1. Do not distribute work unnecessarily.
2. Measure before scaling.
3. Use streaming to control memory.
4. Use batching to amortize overhead.
5. Load expensive models once per actor.
6. Match resources to the workload.
7. Monitor CPU/GPU utilization.
8. Control actor count.
9. Control batch size.
10. Avoid excessive materialization.
11. Choose engines based on workload characteristics.
12. Keep outputs operationally manageable.
13. Integrate Ray jobs cleanly with orchestration.
14. Benchmark before claiming performance improvements.

---

# CODE QUALITY REQUIREMENTS

All code must be:

- Python 3.12+ compatible where supported.
- Clear and readable.
- Runnable or explicitly labeled as conceptual.
- Incremental.
- Production-oriented.
- Properly explained.

Use realistic project structures when useful.

Example:

```text
ray-data-lab/
├── data/
├── src/
│   ├── ingest.py
│   ├── preprocess.py
│   ├── inference.py
│   └── pipeline.py
├── tests/
└── pyproject.toml
```

Do not introduce unnecessary frameworks.

---

# VERSION / API ACCURACY

Ray APIs evolve.

Before writing an API example:

- Prefer current stable Ray APIs.
- Avoid deprecated APIs.
- Do not invent function signatures.
- If an API differs between Ray versions, explain the version sensitivity.
- Use the installed environment/version when available.
- If you cannot verify an exact API, clearly mark the example as conceptual rather than presenting uncertain code as authoritative.

Do not silently teach outdated Ray APIs.

---

# EXPLANATION STYLE

The learner should be able to understand the module even if Ray is new to them.

For difficult concepts, use this pattern:

### Simple explanation

Explain it in plain English.

### Engineering explanation

Give the correct technical definition.

### Example

Show a concrete scenario.

### Code

Show the implementation.

### Internal behavior

Explain what Ray is doing.

### Performance implication

Explain why it matters.

### Production consideration

Explain how an engineer should use it.

---

# REQUIRED DIAGRAMS

Use Markdown/ASCII diagrams wherever they improve understanding.

At minimum include diagrams for:

1. Ray architecture.
2. Task execution.
3. Actor execution.
4. Object store.
5. Ray Data pipeline.
6. Streaming execution.
7. Back pressure.
8. CPU/GPU pipeline.
9. Actor pool.
10. End-to-end batch inference architecture.
11. Ray vs Dask vs Spark decision flow.

Do not add diagrams merely for decoration.

---

# PRACTICAL CHECKPOINTS

After each major section, add small checks such as:

```text
Checkpoint:
- Can you explain what a Ray task is?
- Can you explain the difference between a task and actor?
- Can you explain why the object store exists?
```

Do not make every checkpoint excessively long.

---

# FINAL CHECKPOINT

At the end, include a strong self-assessment.

The learner should be able to answer:

### Fundamentals

- What is Ray?
- Why does Ray exist?
- What is a task?
- What is an actor?
- What is the object store?
- What is an object reference?

### Ray Data

- What is a Dataset?
- What is a block?
- How does `map_batches` work?
- What batch formats are supported?
- Why is streaming useful?
- What is back pressure?

### Resources

- How are CPU resources assigned?
- How are GPUs assigned?
- Why does actor count matter?
- Why does batch size matter?

### ML workloads

- How would you build batch inference?
- Why use actor pools?
- Why load the model once per actor?
- How would you generate embeddings?

### Production

- How would you write results to Parquet?
- How would you orchestrate the pipeline?
- How would you deploy Ray on Kubernetes?
- How does autoscaling fit in?

### Architecture

- When should you use Ray?
- When should you use Dask?
- When should you use Spark?
- When should you use Polars/DuckDB?
- Why is Ray Data not a SQL engine?

---

# INTERVIEW QUESTIONS

Include a final interview-preparation section with questions from:

### Beginner

- What is Ray?
- What is a Ray task?
- What is a Ray actor?
- What is Ray Data?
- What is `map_batches`?

### Intermediate

- Tasks vs actors?
- Why does Ray use an object store?
- What is streaming execution?
- What is back pressure?
- Why use actor pools?
- How do CPU/GPU resources work?

### Advanced

- How would you design distributed batch inference?
- How would you tune actor count?
- How would you tune batch size?
- How would you debug GPU under-utilization?
- Ray Data vs Spark?
- Ray Data vs Dask?
- When should Ray not be used?
- How would you design Ray Data for production?

For each important interview question, provide a concise but technically correct answer.

---

# ROADMAP-ALIGNED HANDS-ON CHECKLIST

The final document must explicitly include all of these roadmap requirements:

```text
[ ] Ray tasks
[ ] Ray actors
[ ] Distributed object store
[ ] Starting Ray locally
[ ] Ray dashboard
[ ] Ray Data datasets
[ ] Reading Parquet
[ ] Reading CSV
[ ] Reading images
[ ] map_batches
[ ] pandas batch format
[ ] PyArrow batch format
[ ] NumPy batch format
[ ] Streaming execution
[ ] Blocks
[ ] Back pressure
[ ] CPU resources
[ ] GPU resources
[ ] Mixed CPU/GPU pipeline
[ ] Actor pools
[ ] Stateful batch processing
[ ] Model reuse per actor
[ ] ML preprocessing
[ ] Batch inference
[ ] Embedding generation
[ ] Feeding training jobs
[ ] Writing Parquet
[ ] Lakehouse integration awareness
[ ] Orchestration integration
[ ] Ray cluster awareness
[ ] Kubernetes deployment awareness
[ ] Autoscaling awareness
[ ] Ray vs Spark
[ ] Ray vs Dask
[ ] Ray limitations
[ ] Not a SQL engine
[ ] Spark/DuckDB/warehouse alternatives
[ ] Performance measurement
[ ] Batch-size tuning
[ ] Actor-count tuning
[ ] Failure/debugging scenarios
[ ] End-to-end Ray Data project
[ ] Spark pandas UDF comparison
[ ] Three-workload engine decision note
```

---

# ROADMAP COVERAGE AUDIT

Before finishing the file, perform a final internal audit against the authoritative Module 2.21 roadmap.

Create a final section:

```markdown
## Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section |
|---|---|---|
| Ray tasks | Yes | ... |
| Ray actors | Yes | ... |
| Object store | Yes | ... |
| Local Ray | Yes | ... |
| Dashboard | Yes | ... |
| Ray Data datasets | Yes | ... |
| Parquet | Yes | ... |
| CSV | Yes | ... |
| Images | Yes | ... |
| map_batches | Yes | ... |
| Streaming execution | Yes | ... |
| Back pressure | Yes | ... |
| CPU/GPU resources | Yes | ... |
| Actor pools | Yes | ... |
| ML preprocessing | Yes | ... |
| Batch inference | Yes | ... |
| Embeddings | Yes | ... |
| Training integration | Yes | ... |
| Outputs | Yes | ... |
| Orchestration | Yes | ... |
| Cluster deployment | Yes | ... |
| Kubernetes/autoscaling | Yes | ... |
| Ray vs Spark vs Dask | Yes | ... |
| Limitations | Yes | ... |
| Hands-on project | Yes | ... |
| Performance tuning | Yes | ... |
| Spark comparison | Yes | ... |
```

Every roadmap requirement must be marked **Yes** before considering the file complete.

---

# QUALITY BAR

The finished `04-ray-data-overview.md` must feel like a serious internal training document used to train a junior/mid-level Data Engineer toward production competency.

It must NOT be:

- a shallow Ray introduction
- a list of definitions
- a collection of disconnected code snippets
- a generic distributed-computing tutorial
- an ML tutorial
- a Kubernetes tutorial
- a marketing description of Ray

It must be a **structured Data Engineering learning module**.

The learner should finish the file understanding:

```text
Why Ray exists
      ↓
How Ray works
      ↓
Tasks + Actors + Object Store
      ↓
Ray Data
      ↓
Distributed datasets
      ↓
map_batches
      ↓
Streaming
      ↓
Back pressure
      ↓
CPU/GPU resources
      ↓
Actor pools
      ↓
ML preprocessing
      ↓
Batch inference
      ↓
Embeddings
      ↓
Production integration
      ↓
Performance tuning
      ↓
Ray vs Dask vs Spark
      ↓
Production decision
```

---

# FINAL EXECUTION INSTRUCTION

Now inspect the existing:

```text
21-Performance-Scaling-and-Cost-Optimization/04-ray-data-overview.md
```

and then rewrite/update **ONLY that file** according to this prompt.

Preserve useful existing material if it is already correct, but improve it wherever it does not satisfy the roadmap and quality requirements above.

Do not modify any other file.

Do not create additional files.

Do not stop after producing an outline.

Produce the **complete, detailed Markdown learning module** in:

```text
04-ray-data-overview.md
```

The final file must be self-contained, progressive, practical, technically rigorous, roadmap-complete, and suitable for learning Ray and Ray Data from fundamentals through production-oriented advanced usage.