# MapReduce and Why Spark Replaced It

> **Roadmap location:** `Stage 2C — Data Engineering_3/02-Hadoop-Ecosystem-and-Legacy-Big-Data/03-mapreduce-model-and-why-spark-replaced-it.md`  
> **Module purpose:** Understand, maintain, debug, and migrate legacy Hadoop batch workloads—not assume Hadoop MapReduce is the default choice for new systems.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain the logical MapReduce model: map → shuffle/sort → reduce.
- Trace key-value pairs from input splits through mapper output, partitioning, shuffle, sorting, reducers, and HDFS output files.
- Run a Python word-count job through Hadoop Streaming.
- Explain when a combiner is correct, why Hadoop may omit it, and why it must not be required for correctness.
- Explain partitioners, custom sort/grouping, shuffle costs, map-side joins, reduce-side joins, and secondary sort.
- Diagnose task failures, retries, speculative execution, and shuffle-related failures.
- Read enough Java MapReduce code to recover its business logic and port it safely.
- Compare MapReduce and Spark without assuming Spark is always faster or entirely in-memory.
- Port word count and a join to PySpark DataFrames and design a fair comparison.
- Identify cases where a simple, robust MapReduce job may still be appropriate.

## 2. Prerequisites and place in the roadmap

Expected prior knowledge:

- Linux shell, file permissions, processes, and log inspection.
- HDFS concepts from Topic 01: NameNode metadata, DataNodes, blocks, replication, and `hdfs dfs` commands.
- YARN concepts from Topic 02: ResourceManager, NodeManagers, containers, resource allocation, application state, and logs.
- Basic Python, SQL joins, distributed processing, partitioning, and shuffle concepts.
- Familiarity with Spark from the earlier Data Engineering modules is useful; this lesson explains how its execution model differs.

### How this lesson fits the module

| Previous or next topic | Relationship |
|---|---|
| `01-hdfs-architecture-namenode-datanodes-and-replication.md` | HDFS stores the input and output data. MapReduce tasks read input through Hadoop's filesystem APIs and write output to HDFS. |
| `02-yarn-resource-management.md` | In a YARN deployment, YARN allocates containers and schedules the MapReduce application. YARN resource allocation is separate from the MapReduce programming model. |
| This lesson | Establishes shuffle, partitioning, combiners, joins, and fault-tolerance concepts used by Spark and other distributed engines. |
| `04-hive-metastore-and-hiveql.md` | Hive queries may execute through MapReduce, Tez, or Spark depending on the installation. Understanding the legacy execution engine helps interpret old plans and migrate workloads. |
| `07-migrating-hadoop-workloads-to-cloud-lakehouse.md` | MapReduce logic must be translated into equivalent transformations and validated against the old job's outputs before cutover. |

The module's purpose is to understand and migrate legacy systems. Do not infer that every new pipeline should be implemented in MapReduce.

## 3. The MapReduce model

MapReduce is a **programming model**: transform input records into intermediate key-value pairs, group all intermediate values for each key, and compute a result per key.

```text
Input files
    |
    v
InputFormat / RecordReader
    |
    v
Map tasks (one task per input split, approximately)
    |
    | intermediate (key, value) records
    v
Optional combiner on mapper output
    |
    v
Partition by key -> sort/spill -> local map output
    |
    v
Shuffle: each reducer fetches its partition from every mapper
    |
    v
Merge and sort by key; values for the same key are grouped
    |
    v
Reduce tasks
    |
    v
OutputFormat / RecordWriter
    |
    v
Output directory in HDFS (e.g. part-r-00000, _SUCCESS)
```

This is a logical flow. Exact implementation details depend on Hadoop version and job configuration. For classic Hadoop MapReduce, mapper output is typically sorted and spilled to local disk, then fetched by reducers over the network. The framework merges sorted segments. Intermediate data is not automatically stored as durable HDFS output between every map and reduce step.

### 3.1 Key-value pairs

An intermediate record is a pair `(key, value)`. The key determines which reducer group receives the record; the value carries the information to aggregate or process.

Word count emits `(word, 1)`. A sales aggregation might emit `(store_id, sale_amount)`. A reduce-side join might emit `(customer_id, ("CUSTOMER", customer_fields))` or `(customer_id, ("ORDER", order_fields))`.

A key is not necessarily a string. Hadoop's Java APIs use types implementing Hadoop's serialization interfaces (commonly `Writable` types). Hadoop Streaming presents records to external programs as lines of text, so the scripts below encode the key and value as tab-separated fields.

### 3.2 Map, shuffle/sort, reduce

- **Map:** receives an input key/value record and emits zero or more intermediate pairs.
- **Partition:** assigns each intermediate key to one reducer partition. The default hash partitioner usually sends equal keys to the same reducer.
- **Sort/group:** mapper outputs are sorted by key; the shuffle transfers partitions to reducers; reducer-side merge/sort groups values by key.
- **Reduce:** receives a key and its iterable/list of values and emits zero or more final pairs.
- **Output:** each reducer normally writes one output file. With one reducer, a common filename is `part-r-00000`; with multiple reducers, files are numbered, such as `part-r-00000` and `part-r-00001`. If reducers are disabled, mapper outputs use names such as `part-m-00000`.

The model does not require a particular business operation. Counting, summing, grouping, filtering, sorting, and joining can all be built from the primitives, though some algorithms are more natural or efficient in other engines.

## 4. Input splits, tasks, and HDFS files

### 4.1 Input splits are not the same as HDFS blocks

An **HDFS block** is a storage unit distributed across DataNodes. An **input split** is a logical unit of work presented to the MapReduce input layer. FileInputFormat commonly creates splits based on file length and configured split size, but split boundaries and record boundaries are handled by the InputFormat/RecordReader. A record such as a line of text is not supposed to be cut into two logical records simply because a byte boundary falls inside it.

Consequences:

- One input file can produce multiple map tasks.
- A map task can read data spanning HDFS blocks, depending on split layout.
- A tiny file often creates a tiny map task, so thousands of tiny files can create scheduling overhead.
- The number of reducers is configured independently of the number of input splits.

### 4.2 Where data lives

- **Input:** typically durable files in HDFS, read through Hadoop's filesystem APIs.
- **Mapper intermediate output:** usually written to the worker's local disk as sorted/spilled map output; reducers fetch it over the network.
- **Final output:** normally written to HDFS by the output writer. The output directory must not already exist for a standard Hadoop job submission.
- **Logs and counters:** application/task logs and counters are exposed through Hadoop/YARN interfaces; aggregated log availability depends on cluster configuration.

The NameNode manages filesystem namespace and block metadata; it does not carry the bulk file contents. YARN allocates compute resources; it does not define the map/reduce algorithm.

## 5. Word count: manually trace three lines

Use these exact input lines:

```text
red blue red
blue green
red green blue
```

### Step 1 — Map output

The mapper emits one `(word, 1)` pair for every token:

```text
(red, 1)
(blue, 1)
(red, 1)
(blue, 1)
(green, 1)
(red, 1)
(green, 1)
(blue, 1)
```

### Step 2 — Shuffle and sort

The framework partitions each key to a reducer, transfers the records, sorts/merges by key, and groups values. With one reducer, the conceptual grouped input is:

```text
blue  -> [1, 1, 1]
green -> [1, 1]
red   -> [1, 1, 1]
```

The order of keys shown here is lexicographic for illustration. Actual sort order is determined by the configured key comparator. With multiple reducers, keys are split across reducer partitions; all values for a given key must go to the same reducer, but output files do not necessarily form one globally sorted file.

### Step 3 — Reduce

For each key, sum the values:

```text
blue  3
green 2
red   3
```

The output contains three records. This trace is conceptual; Hadoop's internal serialized key/value objects are not literally displayed as Python tuples.

## 6. Executable lab A: Hadoop Streaming word count in Python

This lab uses Hadoop Streaming to run Python scripts as mapper and reducer processes. It is executable only when a compatible Hadoop installation, HDFS, and the Streaming JAR are available. A local shell pipeline can test the scripts but does **not** prove that a Hadoop cluster job works.

### 6.1 Create the mapper

Save as `experiments/03_mapreduce/mapper.py`:

```python
#!/usr/bin/env python3
import sys
import re

TOKEN = re.compile(r"[A-Za-z0-9_]+")

for line in sys.stdin:
    for word in TOKEN.findall(line.lower()):
        print(f"{word}\t1")
```

This deliberately defines tokenization as lowercase alphanumeric/underscore tokens. It is not a linguistically complete tokenizer; keep this same rule when comparing with Spark.

### 6.2 Create the reducer

Save as `experiments/03_mapreduce/reducer.py`:

```python
#!/usr/bin/env python3
import sys

current_word = None
current_count = 0

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    if not line:
        continue

    try:
        word, count_text = line.split("\t", 1)
        count = int(count_text)
    except ValueError as exc:
        raise SystemExit(f"Malformed mapper record: {line!r}") from exc

    if current_word is not None and word != current_word:
        print(f"{current_word}\t{current_count}")
        current_count = 0

    current_word = word
    current_count += count

if current_word is not None:
    print(f"{current_word}\t{current_count}")
```

The reducer assumes the framework supplies records sorted by key, which is the standard MapReduce shuffle/sort contract for this job. It keeps only one key's running count in memory; it does not load the entire input into a list.

### 6.3 Test scripts locally first

From the experiment directory:

```bash
chmod +x mapper.py reducer.py

printf 'red blue red\nblue green\nred green blue\n' \
  | ./mapper.py \
  | LC_ALL=C sort \
  | ./reducer.py
```

Expected logical result (key order may depend on sort locale unless `LC_ALL=C` is used):

```text
blue	3
green	2
red	3
```

This local pipeline validates script interoperability and the reducer's sorted-input assumption. It does not exercise Hadoop's partitioning, HDFS, YARN, retries, or distributed shuffle.

### 6.4 Locate the Streaming JAR

The exact location varies by Hadoop distribution and installation. Find the JAR rather than assuming a universal path:

```bash
find "$HADOOP_HOME" -name 'hadoop-streaming*.jar' -print
hadoop version
hdfs dfs -ls /
```

Set `STREAMING_JAR` to the path returned by your installation, for example:

```bash
export STREAMING_JAR=/path/to/hadoop-streaming-version.jar
```

The example path is a placeholder, not a claim that this file exists on your machine.

### 6.5 Upload input to HDFS and submit

Create local input:

```bash
mkdir -p input
cat > input/lines.txt <<'EOF'
red blue red
blue green
red green blue
EOF
```

Upload it. The target input path must not collide with unrelated data:

```bash
hdfs dfs -mkdir -p /user/"$USER"/mapreduce-lab/input
hdfs dfs -put -f input/lines.txt /user/"$USER"/mapreduce-lab/input/
```

Choose an output path that does not already exist:

```bash
hdfs dfs -test -e /user/"$USER"/mapreduce-lab/output && \
  echo "Output path exists; choose a new path or remove the lab output deliberately."
```

After confirming the output path is absent, submit:

```bash
hadoop jar "$STREAMING_JAR" \
  -D mapreduce.job.reduces=1 \
  -input /user/"$USER"/mapreduce-lab/input \
  -output /user/"$USER"/mapreduce-lab/output \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py
```

Depending on Hadoop distribution/version, `-files` may be preferred or supported as an alternative to `-file`; use the syntax documented by the installed Streaming JAR. The scripts must be shipped to task containers. If the cluster cannot launch `python3`, install/configure it on worker nodes or use an appropriate distributed-cache/runtime setup. Executable permissions and interpreter paths must also be compatible with the cluster.

Read the output:

```bash
hdfs dfs -cat /user/"$USER"/mapreduce-lab/output/part-r-*
hdfs dfs -ls /user/"$USER"/mapreduce-lab/output
```

Hadoop generally refuses to write to an existing output directory. Use a new output path for each run, or remove only the known disposable lab output after confirming it is safe to delete:

```bash
hdfs dfs -rm -r /user/"$USER"/mapreduce-lab/output
```

Do not run a broad recursive deletion against a production path.

### 6.6 Operational checks

- Inspect the job summary/counters in the job history or YARN UI.
- Use `yarn application -list`, `yarn application -status <application_id>`, and `yarn logs -applicationId <application_id>` where supported.
- Confirm the final output record counts and values independently.
- For a multi-reducer job, inspect every `part-r-*` file; do not assume all keys are in `part-r-00000`.

## 7. Combiners: local aggregation before shuffle

A **combiner** is an optional local aggregation optimization, usually executed on mapper output before it is transferred to reducers. It can reduce the number of intermediate records and therefore reduce network traffic, sort/merge work, and local spill volume.

For word count, a mapper that sees:

```text
red	1
blue	1
red	1
red	1
```

may run the word-count aggregation locally and emit:

```text
blue	1
red	3
```

The reducer still sums all partial counts from all mappers. If `red` occurs in five mapper partitions, the reducer may receive up to five partial values (or fewer if local aggregation combines more records).

### 7.1 Combiner correctness rule

The combiner must preserve the final answer regardless of whether it runs zero, one, or multiple times on intermediate subsets. Do not rely on Hadoop invoking it, and do not rely on a single invocation.

Safe example: integer sum for word count. Summing partial sums is equivalent to summing all original values.

Potentially unsafe example: computing an average by averaging mapper averages without carrying each partial count. If one mapper has 100 rows averaging 10 and another has 1 row averaging 100, the unweighted average of the two averages is 55, while the true average is `(100*10 + 1*100) / 101 ≈ 10.89`. A safe combiner for average carries `(sum, count)` and merges both fields; the final reducer computes `sum / count`.

Other cautions:

- `max` and `min` are associative and commutative for ordinary well-defined values, so they can be safely combined.
- Floating-point addition can vary slightly with aggregation order because finite-precision arithmetic is not perfectly associative. Define tolerances if exact bitwise reproducibility is required.
- A combiner must use compatible key/value semantics with mapper and reducer logic. It is not automatically valid merely because its code resembles the reducer.
- A combiner may be invoked on only some spills or not invoked at all. It is an optimization, never a correctness requirement.

### 7.2 Add the combiner to the Streaming job

The same reducer can serve as the combiner for integer word count:

```bash
hadoop jar "$STREAMING_JAR" \
  -D mapreduce.job.reduces=1 \
  -input /user/"$USER"/mapreduce-lab/input \
  -output /user/"$USER"/mapreduce-lab/output-combined \
  -mapper mapper.py \
  -combiner reducer.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py
```

The output must be semantically identical to the non-combiner run. Do not assume it will have fewer shuffle bytes for a tiny input; the framework may not invoke the combiner, and the input may be too small to show meaningful savings.

### 7.3 Compare shuffle metrics without inventing results

Run the job both ways against the same input and comparable configuration. Record:

- `Map output records`
- `Map output bytes`
- `Combine input records` and `Combine output records`, when exposed
- `Reduce shuffle bytes` or the equivalent counter available in your Hadoop version
- `Reduce input records`
- Total job duration, with the caveat that tiny jobs are dominated by startup and scheduling overhead

Counter names differ across Hadoop versions/distributions; inspect the job counters rather than assuming every cluster exposes the same exact names. In the JobHistory UI, open the completed job's counters. From the CLI, use the job-history UI or the distribution's supported `mapred job -counter` / counters interface. If counters cannot be collected, document that limitation and capture the available JobHistory counter page or logs. Report **measured** values only after running the job; this lesson contains no benchmark results.

## 8. Partitioners, sort order, grouping, and shuffle cost

### 8.1 Partitioners

A partitioner maps a key to a reducer partition. For `R` reducers, a common hash partitioner behaves conceptually like:

```text
partition = (hash(key) & positive_mask) modulo R
```

This is illustrative pseudocode, not the exact implementation contract for every key type. The important invariant is: all records that belong to the same reduce group must reach the same reducer. If two equal keys are assigned to different reducers, aggregation becomes incorrect.

A custom partitioner is useful when the default distribution causes severe skew or when the data model requires related keys to co-locate. It is not a substitute for a correct grouping design. Partitioning by a field different from the grouping key can split one logical group across reducers.

### 8.2 Custom sort and grouping

Hadoop supports a sort comparator and, separately, a grouping comparator. These are important for secondary sort and advanced reduce-side joins.

- **Sort comparator:** orders intermediate keys within a reducer partition.
- **Grouping comparator:** determines which adjacent keys are presented as one reducer group.
- **Partitioner:** determines which reducer receives a key.

These three choices must agree. For a composite key `(customer_id, event_time)`, the partitioner often partitions by `customer_id`, the sort comparator orders by `(customer_id, event_time)`, and the grouping comparator groups only by `customer_id`. The reducer then receives all events for one customer in event-time order.

### 8.3 Why shuffle is expensive

Shuffle cost includes intermediate serialization, local writes/spills, network transfer, fetch requests, merge/sort CPU, disk I/O, and possible repeated work after task failures. Wide operations such as grouping, joins, and global sorting often require data movement.

Ways to reduce shuffle:

- Filter rows and columns before a wide operation.
- Aggregate locally using a valid combiner or map-side aggregation.
- Use an appropriate partition count; too few reducers limit parallelism and can create oversized partitions, while too many create overhead and many small outputs.
- Use a map-side join when one side is genuinely small enough to distribute safely.
- Handle skew explicitly; one hot key can dominate one reducer even when total cluster capacity is high.
- Avoid unnecessary `groupByKey`-style materialization when a streaming aggregation is sufficient.

A combiner can reduce records sent over the network, but it does not eliminate the need for reducers to merge partial values.

## 9. Joins in MapReduce

Assume two datasets.

`customers.tsv`:
```text
c1	Ada
c2	Ben
c3	Chen
```

`orders.tsv`:
```text
o1	c1	25.00
o2	c1	10.00
o3	c2	7.50
```

The desired result is an inner join of orders to customer names:

```text
o1	c1	Ada	25.00
o2	c1	Ada	10.00
o3	c2	Ben	7.50
```

Customer `c3` has no order, so it does not appear in this inner join.

### 9.1 Reduce-side join

The mapper emits both record types keyed by customer ID:

```text
c1	ORDER|o1|25.00
c1	ORDER|o2|10.00
c1	CUSTOMER|Ada
c2	ORDER|o3|7.50
c2	CUSTOMER|Ben
c3	CUSTOMER|Chen
```

The shuffle sends every record with the same customer key to the same reducer. The reducer identifies the customer record and order records for each key, then emits joined rows.

A conceptual reducer algorithm:

```python
# Pseudocode: values are tagged records for one customer_id.
customer_name = None
orders = []

for value in values:
    tag, *fields = value.split("|")
    if tag == "CUSTOMER":
        customer_name = fields[0]
    elif tag == "ORDER":
        orders.append(fields)

if customer_name is not None:
    for order_id, amount in orders:
        emit(order_id, customer_id, customer_name, amount)
```

This is conceptual pseudocode, not a complete Streaming implementation. A production reducer must define escaping for delimiters, handle duplicate/missing customer records, decide whether to buffer orders, and define inner/left/right/full join semantics. For large key groups, buffering all orders for a key can exhaust reducer memory; process incrementally or use a secondary-sort design.

**Advantages:** both sides can be large; no need to copy the entire customer table to every mapper.  
**Costs:** both sides are shuffled by join key, network and disk I/O can be substantial, and a skewed customer key can overload a reducer.

### 9.2 Map-side join

A map-side join avoids a reduce-side shuffle only when data layout and size make it feasible. Common forms include:

- **Broadcast/distributed-cache join:** load a small lookup dataset into each mapper process or task. Each mapper joins local input rows against the in-memory lookup. The small side must fit safely in each task's memory, and distributing it to all workers has a cost.
- **Sort-merge map-side join:** both datasets are partitioned compatibly and sorted by the join key, with matching partition boundaries. The mapper can stream through aligned partitions. This has stricter data preparation and compatibility requirements.

Do not call a join “map-side” simply because a mapper reads two arbitrary files. A correct map-side join needs a safe lookup/broadcast strategy or compatible sorted/partitioned inputs.

| Consideration | Map-side broadcast join | Reduce-side join |
|---|---|---|
| Small side | Must fit in each mapper's memory (with overhead) | Can be large |
| Shuffle | Avoids join-key shuffle for the main join | Shuffles both tagged sides by join key |
| Preparation | Broadcast/cache distribution or lookup setup | Tag records and partition by join key |
| Main risk | Memory pressure and distributing lookup to every mapper | Shuffle volume, skew, reducer bottlenecks |
| Best fit | Small dimension/lookup + large fact data | Both sides large or no compatible layout |

## 10. Secondary sort

The normal reducer contract groups values by key, but values within a group are not generally guaranteed to be in the desired business order. If each customer needs events sorted by timestamp, sorting only on `customer_id` is insufficient.

A common Java MapReduce design:

1. Emit composite key `(customer_id, timestamp)` and event payload as value.
2. Partition by `customer_id`, so all events for one customer go to one reducer.
3. Sort by `(customer_id, timestamp)`.
4. Group by `customer_id` only.
5. In the reducer, iterate values in timestamp order.

For example, the intermediate composite keys could be:

```text
(c1, 2026-01-01T10:00:00Z) -> event_A
(c1, 2026-01-01T11:00:00Z) -> event_B
(c2, 2026-01-01T09:00:00Z) -> event_C
```

The reducer sees one group for `c1`, with `event_A` before `event_B`, and one group for `c2`. The exact comparator and grouping comparator must be implemented carefully. If the partitioner uses the full composite key, two timestamps for the same customer may be sent to different reducers, breaking the grouping requirement.

## 11. Failure handling, retries, speculative execution, and on-disk shuffle

### 11.1 Task retries

Hadoop can retry failed map or reduce tasks according to job and cluster configuration. A failed task attempt may result from a transient node issue, process crash, bad input record, dependency problem, permission error, or memory/resource exhaustion. Retries help with transient failures; they do not fix deterministic bugs.

For example, if every attempt fails on the same malformed record, increasing retry counts just delays failure. Find the first meaningful exception in the task logs and reproduce with a minimal input.

### 11.2 Speculative execution

Speculative execution may launch a duplicate attempt for a task that appears unusually slow. The framework accepts one successful attempt and discards the competing attempt's output. It can mitigate stragglers caused by noisy nodes or uneven performance.

It does not make arbitrary side effects safe. Mapper/reducer code should be deterministic and should not write to external systems with uncoordinated side effects. A duplicate attempt may execute concurrently even though only one output is committed by the framework.

Disable or tune speculation only after diagnosing the workload: speculation can waste resources on tasks that are slow because of legitimate skew or a consistently expensive key.

### 11.3 Map output and disk

Classic MapReduce mapper output is buffered, sorted, spilled to local disk, and served to reducers. Reducers fetch mapper partitions, merge sorted segments, and can spill their own intermediate structures to disk. This is robust for large jobs but creates I/O and materialization overhead.

If a map task fails, its intermediate output may need to be regenerated. If a worker becomes unavailable, the framework can rerun work elsewhere when the input and required resources are available. The framework's exact recovery behavior depends on which task failed, output commit state, and cluster configuration.

### 11.4 Debugging runbook

1. Find the application/job ID and state.
2. Determine whether failure occurred in map, shuffle/fetch, or reduce.
3. Inspect the first causal exception in the failing task attempt, not only the final wrapper exception.
4. Check task counters: input records, map output records/bytes, spilled records, failed attempts, and reduce shuffle/fetch metrics where available.
5. Check node/container logs, disk space, local-disk health, network errors, permissions, input corruption, and memory limits.
6. Compare failed and successful attempts; determine whether failures follow a particular input partition or host.
7. Reproduce with a small input and one reducer when appropriate.
8. After fixing the cause, rerun to a fresh output path and validate record counts, aggregates, null handling, and business invariants.

| Symptom | Possible causes | First checks |
|---|---|---|
| Map tasks fail repeatedly on same split | Bad input, parser bug, missing dependency, permission issue | First exception and input offset/record |
| Reduce fetch failures | Mapper node lost, local disk issue, network instability | Map attempt state, fetch-failure logs, node health |
| One reducer runs much longer | Key skew, too few reducers, large group, expensive reducer logic | Per-reducer input records/bytes and key distribution |
| Container killed for memory | Large per-key buffering, oversized structures, poor sizing | Container diagnostics, reducer data structures, YARN logs |
| Many spills / high local disk I/O | Large intermediate output or low sort buffer | Map output bytes, spilled records, disk health |
| Job output already exists | Hadoop output path collision | Choose a fresh output path; delete only known disposable lab output |

## 12. `mrjob`: what it helps with and what it does not

`mrjob` is a Python library for writing MapReduce jobs and running them in supported execution modes, including local testing and Hadoop-backed execution when configured. It can make Python MapReduce code easier to structure and package.

Limitations to understand:

- It does not remove the need to understand Hadoop's partitioning, shuffle, serialization, task retries, and cluster configuration.
- Local mode is useful for logic tests but does not reproduce distributed execution, HDFS, YARN resource contention, or cluster shuffle behavior.
- Packaging Python dependencies for remote workers still needs deliberate setup.
- Advanced Hadoop features—custom partitioners, sort/grouping comparators, specialized input/output formats, and cluster-specific settings—may require lower-level Hadoop integration or extra configuration.
- The library's API and compatibility depend on its installed version; verify supported Hadoop/Python versions before using it in a legacy environment.

Use `mrjob` when it reduces boilerplate for a simple Python MapReduce task. Do not treat it as a drop-in replacement for all Java MapReduce capabilities or as a modern distributed DataFrame engine.

## 13. Why Spark superseded MapReduce for many workloads

Classic Hadoop MapReduce is effective at large, fault-tolerant batch processing, but its stage-oriented execution can be expensive for multi-step pipelines. A common pattern is map → materialize map output locally → shuffle → reduce output to durable storage → start another job to read that output. Multi-stage algorithms may repeatedly write intermediate data to HDFS between separate jobs.

Spark introduced a richer execution engine and APIs:

- **DAG scheduling:** Spark plans a graph of transformations and can pipeline compatible narrow transformations within a stage.
- **Lazy evaluation:** transformations describe work; an action triggers execution, allowing the engine to optimize the plan.
- **In-memory reuse:** cached/persisted datasets can be reused without rereading and recomputing them when the chosen storage level and available memory allow it.
- **Richer abstractions:** RDDs, DataFrames, SQL, joins, windows, and structured APIs reduce low-level code for common analytics.
- **Unified pipelines:** multiple transformations can be represented in one application rather than hand-wiring many separate MapReduce jobs.

### 13.1 Do not oversimplify “in-memory”

Spark is not an “everything stays in RAM” engine. It can spill data to disk, read from disk, materialize shuffle files, and recompute lost partitions. Wide transformations still cause shuffle and often involve serialization, network traffic, disk I/O, and sorting. Cache is optional and can evict data. A job with poor partitioning, skew, excessive shuffling, or memory pressure may perform badly.

Likewise, MapReduce does not necessarily write every intermediate record to HDFS: classic map output is typically on local disk and transferred to reducers; reducer outputs are normally written to the configured filesystem. The main comparison is that MapReduce jobs often materialize outputs between separate jobs, whereas Spark can optimize a DAG and pipeline some operations within stages.

### 13.2 When Spark is usually a better fit

- Iterative or multi-stage analytics that reuse intermediate datasets.
- Complex joins, aggregations, window operations, and SQL workloads.
- Interactive exploration and workloads needing a rich API.
- Pipelines where combining many transformations into one optimized plan reduces repeated materialization.

### 13.3 When MapReduce may remain reasonable

- A stable, simple, very large batch job whose execution is primarily I/O-bound.
- Legacy workflows whose migration cost and operational risk outweigh the expected benefit.
- Workloads already tuned and reliable on an existing Hadoop estate.
- A simple, sequential processing job where Spark's additional runtime, dependency, and operational complexity would not buy a meaningful advantage.

This is not a claim that MapReduce is generally preferable for new work. For new distributed analytics, Spark or a managed SQL/processing service is often more productive. The right choice depends on workload shape, data layout, operational maturity, cost, latency requirements, and available platform.

## 14. MapReduce-to-Spark concept mapping

| MapReduce/Hadoop | Spark concept | Important distinction |
|---|---|---|
| Mapper emits intermediate pairs | `map`, `flatMap`, DataFrame `select`/`explode`/expressions | DataFrame expressions can be optimized; not every operation maps one-to-one to a user-written mapper. |
| Local combiner / map-side aggregation | `reduceByKey`, aggregate functions, partial aggregation | Spark can perform map-side combining for associative aggregations; `groupByKey` generally transfers all values and is often less efficient for aggregation. |
| Partitioner | RDD partitioner; DataFrame partitioning/shuffle distribution | DataFrame partitioning is optimizer- and plan-dependent; `repartition` can itself trigger a shuffle. |
| Shuffle and sort | Wide dependency, shuffle exchange, sort/aggregate stage | Spark shuffle files and network transfer still cost time and disk. |
| Reducer aggregation | `reduceByKey`, `aggregateByKey`, `groupBy`, `agg` | Choose aggregation semantics deliberately; a full group of values can be memory-intensive. |
| Multiple MapReduce jobs | Spark DAG of transformations/actions | Spark may pipeline narrow transformations, but shuffle boundaries often create stages. |
| HDFS input/output | Hadoop-compatible paths, object storage, tables, DataFrames | Spark can use HDFS and many other storage systems; storage semantics and commit protocols still matter. |

### 14.1 `reduceByKey` versus `groupByKey`

- `reduceByKey` combines values using an associative/commutative function and can reduce data before shuffle.
- `groupByKey` gathers all values for a key. It is appropriate when every value is actually needed, but not when a sum/count/min/max would suffice.
- For DataFrames, prefer built-in aggregate functions such as `groupBy(...).agg(...)` over collecting groups into Python lists unless that is truly required.

### 14.2 Narrow and wide dependencies

- **Narrow dependency:** a child partition depends on a limited set of parent partitions; Spark can often pipeline operations in one stage. Examples include many `map` and `filter` transformations.
- **Wide dependency:** child partitions depend on data from many parent partitions, commonly requiring a shuffle. Examples include `groupByKey`, many joins, and repartitioning.

Exact stage boundaries depend on the physical plan, exchange operators, and execution settings. Do not equate every source-level transformation with one Spark stage.

## 15. Equivalent word count in PySpark DataFrames

The following code uses the same tokenization rule as the Streaming mapper: lowercase, then split into sequences of ASCII letters, digits, and underscores. It returns the same word/count semantics.

Save as `experiments/03_mapreduce/word_count_df.py`:

```python
from pyspark.sql import SparkSession, functions as F

spark = (
    SparkSession.builder
    .appName("mapreduce-comparison-word-count")
    .getOrCreate()
)

input_path = "hdfs:///user/YOUR_USER/mapreduce-lab/input"
output_path = "hdfs:///user/YOUR_USER/mapreduce-lab/spark-output"

lines = spark.read.text(input_path)

# Extract all tokens using the same rule as mapper.py.
words = (
    lines
    .select(
        F.explode(
            F.split(
                F.lower(F.col("value")),
                r"[^a-z0-9_]+"
            )
        ).alias("word")
    )
    .where(F.col("word") != "")
)

counts = words.groupBy("word").agg(F.count(F.lit(1)).alias("count"))

# Output path must not already exist. Use a fresh path for each run.
counts.write.mode("errorifexists").option("sep", "\t").csv(output_path)

spark.stop()
```

The regex extracts tokens by splitting on non-token characters. For the three-line example, the expected logical records are `blue 3`, `green 2`, and `red 3`. Spark CSV output commonly writes a directory containing part files, not one named `part-r-00000`; exact filenames and ordering are not guaranteed. If a single ordered display is needed for inspection, run a query with `orderBy("word")`, but do not use a global sort unnecessarily in a production job.

Before running, replace `YOUR_USER`, ensure Spark is configured to use the intended Hadoop/HDFS configuration, and choose a fresh output path. Example submission, adapted to the installed environment:

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  experiments/03_mapreduce/word_count_df.py
```

This command requires Spark with YARN support and valid cluster configuration. For local testing, configure an appropriate local master and local input/output paths. Do not compare the runtime of a local Python pipe with a cluster Spark job and call it a fair benchmark.

## 16. Equivalent reduce-side join in PySpark DataFrames

Use the same `customers.tsv` and `orders.tsv` examples defined in Section 9. The equivalent inner join is:

```python
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("orders-customers-join").getOrCreate()

customers = (
    spark.read
    .option("sep", "\t")
    .option("header", "false")
    .schema("customer_id STRING, customer_name STRING")
    .csv("hdfs:///path/to/customers.tsv")
)

orders = (
    spark.read
    .option("sep", "\t")
    .option("header", "false")
    .schema("order_id STRING, customer_id STRING, amount DECIMAL(12,2)")
    .csv("hdfs:///path/to/orders.tsv")
)

joined = (
    orders.join(customers, on="customer_id", how="inner")
    .select("order_id", "customer_id", "customer_name", "amount")
)

joined.write.mode("errorifexists").parquet("hdfs:///path/to/join-output")

spark.stop()
```

**Schema note:** Spark's `schema` argument is normally a `StructType` or a DDL schema string, not a comma-separated sequence of column declarations passed as a positional string in every API version. To keep the example broadly compatible, use an explicit `StructType` in the runnable version below:

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DecimalType

spark = SparkSession.builder.appName("orders-customers-join").getOrCreate()

customer_schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("customer_name", StringType(), True),
])
order_schema = StructType([
    StructField("order_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("amount", DecimalType(12, 2), True),
])

customers = (
    spark.read.option("sep", "\t").schema(customer_schema)
    .csv("hdfs:///path/to/customers.tsv")
)
orders = (
    spark.read.option("sep", "\t").schema(order_schema)
    .csv("hdfs:///path/to/orders.tsv")
)

joined = (
    orders.join(customers, on="customer_id", how="inner")
    .select("order_id", "customer_id", "customer_name", "amount")
)

joined.write.mode("errorifexists").parquet("hdfs:///path/to/join-output")
spark.stop()
```

The second version is the recommended runnable form. Replace placeholder paths and ensure the output path is absent. Spark's optimizer may choose a broadcast join or a shuffle join depending on statistics, hints, configuration, and data sizes. The DataFrame code describes semantics; it does not prescribe one physical join strategy.

## 17. Read legacy Java MapReduce code to port it

When reviewing a legacy job, identify the business semantics before translating implementation details.

1. **Driver:** find job name, input/output paths, mapper/reducer classes, number of reducers, key/value classes, partitioner, sort comparator, grouping comparator, and input/output formats.
2. **Mapper:** identify record parsing, filtering, normalization, emitted key, emitted value, and whether records are tagged for a join.
3. **Combiner:** verify its aggregation is correct for any subset and any number of invocations. Never assume its presence is required.
4. **Partitioner:** confirm records in one logical reduce group are routed to the same reducer.
5. **Reducer:** determine whether it aggregates, joins, sorts, deduplicates, or buffers values. Find assumptions about value order and memory.
6. **Serialization:** inspect `Writable` types and custom serialization. Confirm field delimiters, nulls, decimal precision, time zones, and character encoding.
7. **Input/output:** inspect `InputFormat`, `OutputFormat`, compression, schema, and commit behavior.
8. **Correctness contract:** document null behavior, duplicate keys, late records, ordering, aggregation precision, and output partitioning.
9. **Port to Spark:** express row-level logic as DataFrame transformations and built-in SQL functions where possible; use explicit UDFs only when needed.
10. **Validate:** compare counts, distinct keys, sums, null distributions, duplicate handling, and representative records on the same immutable input snapshot.

Do not mechanically replace every mapper with `map` and every reducer with `groupBy`. A legacy job may depend on a custom partitioner, secondary sort, side inputs, a combiner, or subtle join semantics.

## 18. Hands-on exercises

All exercises belong under `experiments/03_mapreduce/`, as prescribed by the module roadmap.

### Exercise 1 — Word count on HDFS

1. Implement `mapper.py` and `reducer.py` as in Section 6.
2. Test with the three-line input locally.
3. Upload the same input to HDFS.
4. Run Hadoop Streaming and read all reducer output files.
5. Explain the input split count, mapper task count, reducer count, and output filenames based on the job configuration and actual job counters.

**Evidence to record:** commands, Hadoop/Spark versions, job ID, output path, and validation results. Do not claim the job ran unless you ran it.

### Exercise 2 — Add a combiner and compare shuffle bytes

1. Run the job without a combiner and capture available map-output and reduce-shuffle counters.
2. Add `-combiner reducer.py`.
3. Run against the same input with the same reducer count.
4. Verify identical word counts.
5. Compare counters and explain whether the sample is large enough to be informative.

If the combiner is not invoked or counters are unavailable, report that accurately. Increase the dataset with repeated words if needed, while keeping input identical between the two runs. Do not invent metric values.

### Exercise 3 — Reduce-side join of orders and customers

1. Create the sample customer and order datasets from Section 9.
2. Write a mapper that validates each row and emits `customer_id` as key, with a record type (`CUSTOMER` or `ORDER`) in the value.
3. Write a reducer that receives all tagged records for one customer and emits the required inner join.
4. Test duplicate customers, customers without orders, orders with missing customer IDs, malformed rows, and a customer with many orders.
5. Decide and document whether duplicate customer IDs are rejected, deduplicated, or intentionally create multiple joined rows.

The reducer pseudocode in Section 9 explains the algorithm; a production submission must implement robust delimiter/escaping and missing/duplicate-key policy rather than silently assuming clean data.

### Exercise 4 — Port to PySpark DataFrames

1. Port word count and the orders/customers join to DataFrames.
2. Run both implementations against equivalent data and equivalent output semantics.
3. Compare runtime only after multiple comparable runs, separating startup time from steady-state work where possible.
4. Compare source code size using the same definition (for example, nonblank, non-comment lines of application code).
5. Compare actual execution stages from Spark UI / event logs and MapReduce jobs/counters. Do not assume one MapReduce job equals one Spark stage.
6. Record input size, cluster shape, executor/container settings, partition counts, output format, compression, warm/cold cache state, and versions.

A meaningful benchmark needs identical data, equivalent output requirements, comparable resources, and repeatable measurements. No benchmark is provided in this lesson.

## 19. Production checklist and common mistakes

### Production considerations

- Define a stable input schema and malformed-record policy.
- Make mapper/reducer logic deterministic and safe to retry.
- Avoid external side effects inside tasks unless idempotency/transactionality is explicitly designed.
- Check key skew before scaling reducer count.
- Validate combiner algebra and behavior when omitted or invoked multiple times.
- Design joins for duplicate keys, nulls, missing references, and memory bounds.
- Use compression thoughtfully for input, intermediate shuffle, and output; evaluate CPU versus I/O trade-offs.
- Monitor failed attempts, spilled records, map output bytes, reducer input, shuffle fetch failures, task duration distribution, and output file count.
- Avoid excessive tiny files and too many tiny tasks.
- Write outputs to a new path, validate them, then use a controlled publication/cutover step.
- When migrating, preserve business semantics first; optimize only after output equivalence is established.

### Common mistakes

- Treating HDFS blocks and MapReduce input splits as identical.
- Assuming one mapper per file or one reducer per key.
- Assuming all intermediate data is written to HDFS.
- Assuming a combiner always runs or can perform any reducer operation.
- Using a non-associative or non-commutative combiner without preserving sufficient state.
- Partitioning by a field that splits one logical reduce group.
- Assuming reducer values arrive in business order without a secondary-sort design.
- Buffering unbounded values for a hot key in reducer memory.
- Calling any join that reads two files a map-side join.
- Assuming Spark is always faster or never uses disk.
- Comparing different input, cluster resources, caching, or output formats and presenting the result as an engine benchmark.
- Assuming Spark `groupByKey` is equivalent in performance to aggregation via `reduceByKey`.
- Deleting an existing HDFS output path without confirming it is disposable.

## 20. Interview questions and concise answers

**1. What are the three main phases of MapReduce?**  
Map emits intermediate key-value pairs; shuffle/sort partitions, transfers, orders, and groups them by key; reduce processes each key and its values to emit final results.

**2. What is the difference between an HDFS block and an input split?**  
An HDFS block is a storage unit; an input split is a logical unit of mapper work. They are related but not identical.

**3. Why is shuffle expensive?**  
It can require serialization, local spill and merge, network transfer, sorting, disk I/O, and extra work after failed attempts.

**4. Why is a combiner optional?**  
Hadoop may invoke it zero or more times. Correctness must hold even if it does not run; it is only a local optimization.

**5. When is a combiner safe?**  
When the partial operation preserves the final result under arbitrary grouping and repeated application, usually by using associative/commutative aggregation or sufficient state such as `(sum, count)` for averages.

**6. Why does a reduce-side join need a partitioner keyed by the join key?**  
All records for one join key must reach the same reducer so it can match records from both inputs.

**7. What does secondary sort solve?**  
It orders records within a reduce group by a secondary field, using a composite sort key, a partitioner that keeps the primary key together, and a grouping comparator for the primary key.

**8. What is speculative execution?**  
It launches a duplicate attempt for a slow task and accepts one successful attempt, potentially reducing straggler impact while consuming extra resources.

**9. Why did Spark replace MapReduce for many workloads?**  
Spark can represent multi-step computation as a DAG, pipeline compatible transformations, reuse cached data, and offer SQL/DataFrame APIs, often avoiding repeated job boundaries and intermediate materialization.

**10. Is Spark always in-memory?**  
No. Spark can spill to disk, shuffle through disk files, and recompute partitions. Memory reuse is an optimization, not a universal guarantee.

**11. When might MapReduce still be reasonable?**  
For stable, simple, very large batch workloads that are I/O-bound or already reliable and inexpensive on an existing Hadoop platform, where migration does not justify its cost and risk.

**12. What should be checked before porting a Java MapReduce job?**  
Mapper/reducer semantics, key/value types, combiner, partitioner, sort/grouping comparators, joins, serialization, null/duplicate behavior, output contract, and task side effects.

## 21. Checkpoint and self-assessment

Mark an item only when you can explain or demonstrate it without relying solely on memorized definitions.

- [ ] I can explain map, shuffle/sort, and reduce using the word-count trace.
- [ ] I can distinguish input splits, mapper tasks, reducer tasks, HDFS blocks, and output files.
- [ ] I can run a Streaming word-count job on HDFS and inspect its result.
- [ ] I can explain why a combiner is optional and prove whether a proposed combiner is safe.
- [ ] I can explain partitioning, sort order, grouping, and shuffle costs.
- [ ] I can choose between map-side broadcast/sort-merge joins and reduce-side joins.
- [ ] I can describe secondary sort and the roles of partitioner, sort comparator, and grouping comparator.
- [ ] I can diagnose task retries, speculative execution, and reduce shuffle failures.
- [ ] I understand `mrjob`'s value and its distributed-execution limitations.
- [ ] I can compare MapReduce and Spark without saying Spark is always faster or never writes to disk.
- [ ] I can port word count and an orders/customers join to PySpark DataFrames with equivalent semantics.
- [ ] I can read a Java MapReduce driver, mapper, combiner, partitioner, and reducer to recover business logic.
- [ ] I can validate a migration using record counts, aggregates, key distributions, nulls, duplicates, and representative records.

## 22. Further reading

Use documentation compatible with the Hadoop and Spark versions installed in your environment; APIs, configuration names, and counter availability can vary by release.

- Apache Hadoop MapReduce Tutorial: https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html
- Apache Hadoop Streaming: https://hadoop.apache.org/docs/stable/hadoop-streaming/HadoopStreaming.html
- Apache Spark RDD Programming Guide: https://spark.apache.org/docs/latest/rdd-programming-guide.html
- Apache Spark SQL, DataFrames and Datasets Guide: https://spark.apache.org/docs/latest/sql-programming-guide.html
- Apache Spark Configuration: https://spark.apache.org/docs/latest/configuration.html

---

**Lesson completion criterion:** You should be able to trace the MapReduce data path, run and validate the Streaming lab, explain the trade-offs behind combiners and joins, and port the same business semantics to Spark. Treat performance claims as hypotheses until supported by measurements from a controlled run.
