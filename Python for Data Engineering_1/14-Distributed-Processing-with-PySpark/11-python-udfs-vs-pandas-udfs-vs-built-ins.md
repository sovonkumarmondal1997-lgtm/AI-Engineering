# Python UDFs vs pandas UDFs vs Built-ins

> **Module 2.14 — Distributed Processing with PySpark**  
> **Phase D — Performance Internals**  
> **Topic 11 — Python UDFs vs pandas UDFs vs Built-ins**
>
> The goal of this topic is not merely to learn UDF syntax. The goal is to learn how to choose the right computation model for Spark: use Spark-native computation when it can express the logic, and choose the appropriate Python extension mechanism when custom logic is genuinely required.

---

## 1. Learning Objectives

By the end of this topic, you should be able to:

- explain what a Spark built-in function is and why it is generally preferred;
- explain how Spark-native expressions participate in Spark's expression tree;
- define and use a Python UDF;
- declare UDF return types correctly;
- handle SQL `NULL` values safely inside Python code;
- explain the conceptual Spark JVM → Python worker → Python result boundary;
- explain why ordinary Python UDFs can be expensive;
- explain Arrow's role in columnar data interchange;
- distinguish ordinary Python UDFs, Arrow-optimized Python UDFs, pandas UDFs, `applyInPandas`, `mapInPandas`, and `mapInArrow`;
- explain Series → Series and iterator-of-Series → iterator-of-Series pandas UDF patterns;
- explain grouped aggregation pandas UDF use cases;
- explain why iterator pandas UDFs can be useful when expensive setup can be reused;
- explain the memory implications of `applyInPandas`;
- explain why a very large group can overwhelm a Python worker;
- explain how UDFs can reduce or limit optimizer visibility;
- apply the **filter first, UDF last** pattern when semantics permit;
- package Python dependencies so executors can import them;
- explain why local success does not guarantee executor success;
- describe Python UDTFs at an advanced awareness level;
- describe the Spark 4 Python data source API at an awareness level;
- benchmark equivalent implementations fairly;
- inspect explain plans for Python evaluation;
- make a production decision based on correctness, execution model, data volume, memory, observability, and measured evidence.

---

## 2. Why This Topic Matters

Sooner or later, a Spark pipeline needs logic that Spark does not provide directly. The implementation choice can materially affect runtime, resource usage, memory behavior, and how much Spark can understand about the computation.

The key engineering question is therefore not:

> **"How do I create a UDF?"**

It is:

> **"What is the highest-level Spark computation model that correctly expresses this requirement?"**

A practical hierarchy is:

```text
Spark built-in function
        ↓
Spark SQL expression
        ↓
DataFrame / SQL composition
        ↓
Appropriate specialized Spark API
        ↓
pandas UDF / appropriate Arrow-based API
        ↓
Plain Python UDF when necessary
        ↓
Other advanced Python APIs such as UDTFs when their semantics fit
```

This is a decision framework, not an absolute prohibition on UDFs. A Python UDF can be the correct engineering choice when Spark-native expressions cannot express the required logic.

### The central mental model

Think of Spark as a distributed computation engine with a large vocabulary of native operations.

A built-in expression is work Spark already understands.

A Python UDF is custom work that requires crossing into Python.

A pandas UDF is still custom Python work, but data can be exchanged in Arrow-oriented batches and processed using vectorized pandas operations.

The correct choice depends on the semantics of the workload, not on the slogan "UDFs are bad."

---

## 3. The Spark Computation Model

Before comparing APIs, remember the execution path:

```text
Driver
  |
  | constructs logical computation
  v
Spark execution engine
  |
  +-----------------------------+
  |                             |
  v                             v
Spark-native operators       Python evaluation
                                  |
                                  v
                           Python worker
                                  |
                                  v
                           custom Python logic
```

The important question is **where the computation runs and what Spark can see about it**.

For Spark-native expressions, Spark has structured information about the expression.

For Python code, Spark generally has much less semantic visibility into the implementation itself.

That distinction becomes important later when we discuss:

- optimizer visibility;
- code generation opportunities;
- data reduction before Python;
- plan inspection;
- Python worker resource usage.

---

## 4. A Simple Business Problem

Assume a DataFrame contains:

```text
customer_id
country
phone_number
email
amount
event_timestamp
```

The business requirement is:

> Normalize phone numbers by removing formatting characters.

### 4.1 Spark-native implementation

```python
from pyspark.sql import functions as F

result = df.withColumn(
    "clean_phone",
    F.regexp_replace("phone_number", "[^0-9]", "")
)
```

This is the first implementation to consider because Spark already provides the required operation.

### 4.2 Plain Python UDF implementation

```python
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

@F.udf(returnType=StringType())
def normalize_phone(phone):
    if phone is None:
        return None
    return "".join(ch for ch in phone if ch.isdigit())

result = df.withColumn(
    "clean_phone",
    normalize_phone(F.col("phone_number"))
)
```

This works conceptually, but now the computation enters Python.

### 4.3 Why compare the implementations?

The business result can be equivalent while the execution model is different.

That is the lesson of this topic:

```text
Same business logic
        ↓
Different implementation
        ↓
Different execution path
        ↓
Different optimization opportunities
        ↓
Potentially different resource profile
```

The same comparison should be extended to Arrow-optimized Python UDFs and pandas UDFs where those mechanisms are appropriate.

---

## 5. Built-in Spark Functions

Built-ins are Spark-native functions such as:

- `col`
- `lit`
- `when` / `otherwise`
- `regexp_replace`
- `lower`
- `upper`
- `trim`
- `concat`
- `substring`
- `length`
- date functions
- timestamp functions
- arithmetic expressions
- aggregations

Examples:

```python
from pyspark.sql import functions as F

df.select(
    F.col("customer_id"),
    F.lower(F.trim(F.col("email"))).alias("normalized_email"),
    (F.col("amount") * F.lit(1.18)).alias("amount_with_tax"),
)
```

### What makes a built-in different?

A built-in is not merely "a Python function that happens to be fast."

The important distinction is that Spark receives an expression that belongs to its supported computation model.

For example:

```python
F.lower(F.col("email"))
```

constructs a Spark expression.

By contrast:

```python
normalize_email(F.col("email"))
```

where `normalize_email` is a Python UDF introduces custom Python evaluation.

This distinction matters because Spark can reason about native expressions.

---

## 6. Why Built-ins Are Usually Preferred

Built-ins generally provide more opportunities for Spark-native execution and optimization.

Potential advantages include:

- Spark-native execution;
- JVM-side execution paths where applicable;
- Catalyst visibility;
- integration with Spark SQL;
- code-generation opportunities where supported;
- expression-level optimization opportunities;
- reduced Python/JVM data-transfer overhead.

Be precise:

> **Built-ins give Spark visibility into the expression, which creates optimization opportunities.**

Do **not** turn that into the false statement:

> "Every built-in automatically gets every possible optimization."

Actual behavior depends on the expression, data source, plan, statistics, configuration, and Spark version.

### A useful engineering rule

Before writing Python, ask:

```text
Does Spark already know how to do this?
```

If yes, prefer the Spark-native implementation unless there is a documented reason not to.

---

## 7. Python UDF Fundamentals

A Python UDF lets you define custom Python logic and expose it as a Spark column expression.

A simple example:

```python
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

@F.udf(returnType=StringType())
def normalize_phone(phone):
    if phone is None:
        return None
    return "".join(ch for ch in phone if ch.isdigit())

result = df.withColumn(
    "clean_phone",
    normalize_phone(F.col("phone_number"))
)
```

### What each part means

#### `@F.udf`

Registers the Python function as a Spark UDF.

#### `returnType=StringType()`

Tells Spark the expected output schema type.

#### `phone`

The Python value supplied to the function for the UDF execution path.

#### `F.col("phone_number")`

A Spark `Column` expression supplied to the UDF.

#### The result

The UDF returns a Spark `Column` expression:

```python
normalize_phone(F.col("phone_number"))
```

### UDFs are lazy

Defining the UDF and building the DataFrame transformation does not immediately execute the Python function.

Execution occurs when an action causes Spark to run the plan.

That connects directly to the lazy-evaluation model from Topic 04.

---

## 8. Python UDF Execution Model

A useful conceptual model is:

```text
Spark JVM
    |
    v
Spark task
    |
    v
Python worker
    |
    v
Python function
    |
    v
Python result
    |
    v
Spark JVM / downstream execution
```

The exact internal mechanics vary by Spark version and execution path, so do not assume every UDF uses identical byte-level communication.

The important engineering boundary is:

```text
JVM-side Spark execution
        ↕
Python execution
```

That boundary can introduce costs involving:

- serialization and deserialization;
- Python worker processes;
- data conversion;
- Python interpreter execution;
- communication;
- custom-function invocation;
- reduced optimizer visibility.

### Why row-at-a-time Python UDFs can be expensive

Conceptually:

```text
100 million logical rows
        ↓
custom Python function
        ↓
many Python-level function applications
```

The overhead can come from several sources simultaneously:

1. moving data toward Python execution;
2. converting values;
3. invoking Python logic;
4. executing the Python interpreter;
5. moving results back into Spark's execution path;
6. losing some opportunities for Spark to reason about the internal logic.

Do not interpret this as "one IPC message per row." The conceptual model is about per-row custom function work, not a claim about one physical transport operation per row.

---

## 9. Return Types and NULL Handling

A UDF's return type is part of the contract between your Python function and Spark.

Common types include:

```python
from pyspark.sql import types as T

T.StringType()
T.IntegerType()
T.DoubleType()
T.BooleanType()
T.DateType()
T.TimestampType()
T.ArrayType(T.StringType())
T.StructType([...])
```

### Why return types matter

Spark needs to understand the output schema.

If the declared type and actual Python result do not match, execution can fail or produce behavior that is not what you intended.

Treat the declared return type as a production interface, not a decorative annotation.

### NULL and Python `None`

Spark SQL uses `NULL`.

Python uses `None`.

A defensive scalar UDF commonly handles the mapping explicitly:

```python
@F.udf(returnType=T.StringType())
def normalize_phone(phone):
    if phone is None:
        return None
    return "".join(ch for ch in phone if ch.isdigit())
```

Example:

| Input | Output |
|---|---|
| `"123-456"` | `"123456"` |
| `None` | `None` |
| `""` | `""` |

### Test NULL behavior

Do not assume that a built-in and a custom Python function have identical NULL semantics.

Test:

- `NULL`;
- empty strings;
- malformed values;
- boundary values;
- unexpected types;
- empty input.

Correctness comes before optimization.

---

## 10. Python/JVM Boundary

The Python/JVM boundary is one of the most important concepts in this topic.

Consider:

```text
Spark-native expression
        |
        v
Spark execution engine
```

versus:

```text
Python UDF
        |
        v
Spark execution
        |
        v
Python worker
        |
        v
custom Python logic
```

The second path creates a language/runtime boundary.

That does not mean the Python UDF is automatically wrong.

It means you should account for the boundary in the performance model.

### Questions to ask

- How many rows enter Python?
- How many columns are needed?
- How expensive is the Python logic?
- Is the computation vectorizable?
- Is the data grouped?
- How much memory does the Python process need?
- Are dependencies available on executors?
- Can Spark reduce the data before Python execution?

These questions are often more useful than simply asking whether an API is "fast."

---

## 11. Arrow Fundamentals

Arrow was introduced earlier in the Data Engineering roadmap.

The relevant connection here is:

```text
Arrow
  ↓
columnar interchange
  ↓
JVM ↔ Python data movement
```

Arrow can reduce some overhead associated with moving columnar data between JVM-side Spark execution and Python execution in supported paths.

However:

> **Arrow does not magically make every Python UDF fast.**

Arrow changes a data interchange mechanism. It does not remove:

- the cost of Python computation;
- poor algorithms;
- excessive data volume;
- memory pressure;
- skew;
- bad grouping choices;
- dependency problems.

This distinction is essential.

---

## 12. Arrow-Optimized Python UDFs

Modern PySpark provides Arrow-optimized execution options for Python UDFs.

The purpose is to improve the data interchange path between Spark and Python for supported execution paths.

Conceptually:

```text
Ordinary Python UDF

Spark
  ↓
Python execution boundary
  ↓
Python function


Arrow-oriented Python UDF

Spark
  ↓
Arrow-oriented interchange
  ↓
Python function
```

The exact decorator/configuration/API behavior is Spark-version-sensitive. Use the API available in the Spark/PySpark version installed by your project and verify the official API for that version rather than copying a legacy tutorial.

### Arrow-optimized UDF vs pandas UDF

These are related but distinct concepts.

An Arrow-optimized Python UDF does not automatically mean:

> "This is a pandas UDF."

A pandas UDF specifically uses pandas-oriented vectorized interfaces and Arrow for supported data interchange.

Keep the mental model separate:

```text
Arrow optimization
        ≠
pandas UDF
```

---

## 13. pandas UDF Fundamentals

A pandas UDF is a Python function exposed through a Spark API that operates on batches represented using pandas objects for supported execution patterns.

A simple Series → Series example:

```python
import pandas as pd
from pyspark.sql import functions as F

@F.pandas_udf("double")
def add_tax(amount: pd.Series) -> pd.Series:
    return amount * 1.18

result = df.withColumn(
    "amount_with_tax",
    add_tax(F.col("amount"))
)
```

Conceptually:

```text
Spark
  ↓
Arrow batches
  ↓
pandas Series
  ↓
vectorized Python computation
  ↓
Arrow
  ↓
Spark
```

### Why batching matters

Instead of designing custom Python logic around individual scalar values, the function can operate on a batch.

For vectorizable work, this can reduce some per-element overhead.

But:

> **pandas UDF does not mean "the entire Spark DataFrame becomes one pandas DataFrame."**

Spark remains distributed.

---

## 14. pandas UDF Types

The exact supported signatures and type annotations are version-sensitive. Learn the execution patterns first and verify the installed Spark version when implementing them.

### 14.1 Series → Series

Mental model:

```text
Spark column batch
        ↓
pandas Series
        ↓
pandas/vectorized computation
        ↓
pandas Series
        ↓
Spark column
```

Example:

```python
@F.pandas_udf("double")
def add_tax(amount: pd.Series) -> pd.Series:
    return amount * 1.18
```

Typical use:

- vectorizable numerical transformations;
- vectorizable string operations;
- custom pandas-supported calculations.

### 14.2 Iterator of Series → Iterator of Series

Mental model:

```text
Iterator[pd.Series]
        ↓
batch
batch
batch
        ↓
Iterator[pd.Series]
```

This pattern is useful when expensive setup can be performed outside the inner per-batch operation.

Illustrative structure:

```python
from typing import Iterator
import pandas as pd

def transform_batches(
    batches: Iterator[pd.Series],
) -> Iterator[pd.Series]:
    expensive_state = initialize_state()

    for batch in batches:
        yield apply_state(batch, expensive_state)
```

The important idea is reuse of appropriate initialization within the function's execution context.

Do not assume a universal worker lifecycle. Spark's Python worker reuse and execution behavior can vary with configuration and execution path.

### 14.3 Grouped aggregation pandas UDF

Pandas UDFs can also be used for grouped aggregation patterns where the function receives grouped values and produces an aggregate result.

The critical distinction is:

```text
grouped aggregation pandas UDF
        ≠
groupBy(...).applyInPandas(...)
```

The former is an aggregation pattern.

The latter gives a pandas DataFrame for each group and permits more general per-group transformation.

---

## 15. Iterator pandas UDFs and Expensive Initialization

Suppose custom logic requires setup such as:

- loading configuration;
- preparing a lookup object;
- initializing a model;
- constructing reusable state.

A naive scalar UDF design can put too much work inside repeated function calls.

An iterator-based pandas UDF can make the initialization structure more appropriate:

```text
initialize reusable state
        ↓
process batch 1
        ↓
process batch 2
        ↓
process batch 3
        ↓
...
```

This is not a guarantee that initialization happens exactly once per executor or for the entire application.

The production rule is:

> Design initialization according to the documented execution semantics of the selected API and validate it on the target Spark version.

---

## 16. `applyInPandas`

`applyInPandas` is designed for grouped pandas processing.

Mental model:

```text
Spark data
    ↓
grouping
    ↓
one group presented as a pandas DataFrame
    ↓
Python function
    ↓
output pandas DataFrame
    ↓
Spark
```

Illustrative example:

```python
import pandas as pd

def country_trend(pdf: pd.DataFrame) -> pd.DataFrame:
    pdf = pdf.sort_values("event_timestamp")
    pdf["running_amount"] = pdf["amount"].cumsum()
    return pdf[[
        "country",
        "event_timestamp",
        "amount",
        "running_amount",
    ]]

result = (
    df.groupBy("country")
      .applyInPandas(
          country_trend,
          schema="""
              country string,
              event_timestamp timestamp,
              amount double,
              running_amount double
          """
      )
)
```

### Why use it?

It is useful when the transformation naturally depends on a complete group and cannot be expressed conveniently with Spark-native functions.

Examples:

- per-group custom statistical procedures;
- per-group model fitting;
- per-group time-series calculations;
- complex pandas-native algorithms.

### The critical memory warning

A group is a unit of data presented to the Python function.

Therefore:

```text
data skew
   ↓
one unusually large group
   ↓
large pandas DataFrame
   ↓
Python worker memory pressure
   ↓
possible OOM
```

`applyInPandas` is **not** "free distributed pandas."

The largest group matters.

---

## 17. `mapInPandas`

`mapInPandas` is batch-oriented rather than group-oriented.

Mental model:

```text
Spark partitions/batches
        ↓
iterator of pandas DataFrames
        ↓
custom batch transformation
        ↓
iterator of pandas DataFrames
        ↓
Spark
```

It is appropriate when the logic naturally operates on batches rather than on complete logical groups.

Illustrative structure:

```python
def transform_batches(
    iterator,
):
    for pdf in iterator:
        output = pdf.copy()
        output["normalized_amount"] = output["amount"] * 1.18
        yield output
```

The schema and exact API details should be checked against the installed PySpark version.

### `applyInPandas` vs `mapInPandas`

| API | Unit of processing | Typical use |
|---|---|---|
| pandas UDF | Series/batches | vectorized column logic |
| `applyInPandas` | group | per-group complex logic |
| `mapInPandas` | batch | arbitrary batch transformation |

The distinction matters because the unit of processing determines the memory model.

---

## 18. `mapInArrow`

`mapInArrow` provides an Arrow RecordBatch-oriented extension point.

The mental model is:

```text
Spark
  ↓
Arrow RecordBatch
  ↓
Python transformation
  ↓
Arrow RecordBatch
  ↓
Spark
```

It is useful when:

- Arrow-level columnar processing is appropriate;
- pandas is not necessary;
- custom batch processing needs Arrow-oriented inputs/outputs.

The exact signature and supported behavior are version-sensitive. Verify the installed Spark/PySpark documentation before implementing production code.

Do not fabricate a signature from memory.

### Why use Arrow directly?

Conceptually:

```text
pandas-oriented custom processing
        vs
Arrow-oriented custom processing
```

The right choice depends on what representation your algorithm naturally consumes and produces.

---

## 19. Python UDTFs

UDTF means **User Defined Table Function**.

The key difference from a scalar UDF is output cardinality.

### Scalar UDF

```text
input value/row
      ↓
one output value
```

### UDTF

```text
input
      ↓
custom table-producing logic
      ↓
multiple output rows
```

This makes UDTFs useful for custom logic that naturally expands an input into a relation rather than producing one scalar result.

Python UDTFs are an advanced Spark 4-era extensibility capability.

At this stage, understand:

- what a table function is;
- how its output semantics differ from a scalar UDF;
- when multiple output rows are a natural fit;
- that the exact API is version-sensitive.

Do not treat UDTFs as interchangeable with ordinary UDFs.

---

## 20. Python Data Source API Awareness

Spark 4 includes a Python data source API for Python-based data-source extensibility.

This is fundamentally different from a UDF.

A UDF changes computation over data already represented in Spark.

A data source API extends how Spark can interact with external data.

Conceptually:

```text
UDF
data already in Spark
        ↓
custom computation


Python data source API
external/source representation
        ↓
custom source integration
        ↓
Spark
```

At this module level, know:

- what the API is;
- why it exists;
- what problem it addresses;
- broad use cases;
- that it is a source-extensibility mechanism rather than a row transformation.

Do not turn this section into a full data-source implementation course.

---

## 21. UDFs and Optimizer Visibility

This is the bridge to Topic 12.

A Spark-native expression can be represented as a Spark expression:

```text
built-in expression
        ↓
Spark understands expression
        ↓
optimizer can reason about it
```

A custom Python function is less transparent:

```text
Python UDF
        ↓
custom Python computation
        ↓
reduced semantic visibility
```

This can limit or complicate optimization opportunities around the custom computation.

Potential areas include:

- predicate pushdown opportunities;
- expression simplification;
- column pruning around the custom operation;
- code generation;
- other expression-level optimizations.

Be precise:

> UDFs can **block or limit** optimizer visibility.

Do not claim:

> "A Python UDF always completely prevents optimization."

Spark can still optimize portions of the surrounding plan.

### The key question

When you inspect a plan, ask:

> **Where did the Python computation appear?**

That question leads directly into Topic 12.

---

## 22. Filter First, UDF Last

One of the most useful production patterns is:

```text
FILTER
  ↓
SELECT REQUIRED COLUMNS
  ↓
REDUCE DATA
  ↓
APPLY EXPENSIVE CUSTOM LOGIC
```

Suppose:

```python
bad = (
    df.withColumn(
        "clean_phone",
        normalize_phone(F.col("phone_number"))
    )
    .filter(F.col("country") == "IN")
)
```

When the filter is semantically independent of the UDF:

```python
better = (
    df.filter(F.col("country") == "IN")
      .withColumn(
          "clean_phone",
          normalize_phone(F.col("phone_number"))
      )
)
```

The second shape can reduce the number of rows entering Python.

### Important qualification

Do not reorder transformations blindly.

Correctness comes first.

If moving the filter changes semantics, it is not an optimization.

### General pattern

```text
Can I reduce rows?
        ↓
Can I reduce columns?
        ↓
Can I reduce data volume?
        ↓
Only then run expensive custom Python
```

---

## 23. UDF Placement and Data Reduction

UDF cost depends on more than the function body.

Consider:

```text
UDF on 1 billion rows
```

versus:

```text
filter
  ↓
10 million rows
  ↓
same UDF
```

The same function can have radically different total cost because the amount of data entering Python changed.

Consider:

- number of rows;
- number of columns;
- data size;
- function complexity;
- batch size;
- grouping;
- serialization;
- executor resources;
- caching/reuse;
- downstream operations.

### Practical rule

Before optimizing the Python function itself, ask whether you can reduce the amount of data sent through it.

---

## 24. Memory Risks

Python execution introduces another resource dimension: Python worker memory.

Important sources of memory pressure include:

- pandas DataFrame materialization;
- Arrow batches;
- Python object overhead;
- large groups;
- large model state;
- heavy libraries;
- skew;
- unnecessary columns;
- unnecessarily large intermediate results.

### The most important grouped-processing risk

```text
skewed key
   ↓
huge group
   ↓
applyInPandas
   ↓
large pandas DataFrame
   ↓
Python worker memory pressure
```

A larger Spark cluster does not automatically make a single huge group fit into one Python worker's memory.

The unit of processing matters.

---

## 25. pandas UDF Memory Model

Do not confuse these patterns:

### Batch-oriented pandas UDF

```text
batch
  ↓
pandas Series
  ↓
result
```

### Grouped `applyInPandas`

```text
logical group
  ↓
pandas DataFrame
  ↓
result
```

### Iterator APIs

```text
batch 1
batch 2
batch 3
...
```

The word "pandas" does not mean the entire Spark DataFrame is converted into one pandas object.

Memory behavior depends on the selected API and the unit of processing.

Avoid making assumptions about exact batch sizes unless verified for the target Spark version and configuration.

---

## 26. Dependency Packaging

A classic production failure is:

> "The UDF works on my laptop."

but:

> "The UDF fails on executors."

The driver and executor environments must be considered separately.

Potential failures include:

- `ModuleNotFoundError`;
- package-version mismatch;
- incompatible binary dependency;
- package installed on the driver but absent on executors;
- different Python versions;
- incompatible native libraries.

### Why this matters

A Python UDF executes in distributed worker environments.

Therefore:

```text
local environment
        ≠
executor environment
```

unless you deliberately make them consistent.

### Production questions

- Which Python version runs on executors?
- Which packages are installed?
- Are versions pinned?
- How are dependencies distributed?
- Is the environment reproducible?
- Are native dependencies compatible?

Topic 02 covers the broader dependency-packaging and submission model. Here, focus on its consequences for custom Python execution.

---

## 27. Heavy Libraries and Model Initialization

This pattern is dangerous:

```python
@F.udf(...)
def predict(value):
    import huge_ml_library
    ...
```

Potential concerns include:

- library import cost;
- model initialization;
- Python worker memory;
- repeated setup;
- serialization;
- executor resource consumption;
- version compatibility.

Do not assume that every worker, task, or batch has exactly the same lifecycle.

Instead, choose an API whose execution model matches the initialization strategy and verify the behavior on the target cluster.

### Iterator-based approach

Where appropriate, an iterator pandas UDF can structure initialization so reusable state is established outside the inner batch loop:

```text
initialize reusable state
        ↓
batch 1
batch 2
batch 3
...
```

This can be a better fit than unnecessarily repeating expensive setup for each individual logical row.

---

## 28. Benchmarking

Benchmarking is part of engineering, not an optional final step.

Implement the same business logic in multiple ways:

1. built-in functions;
2. plain Python UDF;
3. Arrow-optimized Python UDF;
4. pandas UDF.

Then measure.

Use a table like:

| Implementation | Runtime | Shuffle | CPU | Memory | Notes |
|---|---:|---:|---:|---:|---|
| Built-in | measured | measured | measured | measured | |
| Python UDF | measured | measured | measured | measured | |
| Arrow UDF | measured | measured | measured | measured | |
| pandas UDF | measured | measured | measured | measured | |

Do **not** invent values.

Record actual measurements from your environment.

### Useful evidence

- wall-clock runtime;
- task duration;
- CPU utilization;
- memory behavior;
- shuffle read/write;
- spill;
- Python execution indicators where available;
- executor behavior;
- correctness.

---

## 29. Fair Benchmarking

A fair comparison controls:

- same input dataset;
- same cluster;
- same Spark configuration;
- same number of partitions;
- same business logic;
- same output;
- same action;
- same warm-up strategy;
- multiple runs where appropriate.

Avoid:

- comparing tiny data against huge data;
- including I/O in only one implementation;
- comparing different algorithms instead of equivalent implementations;
- using only the fastest single run;
- ignoring correctness.

### Benchmark sequence

```text
CORRECTNESS FIRST
        ↓
SAME LOGIC
        ↓
SAME DATA
        ↓
SAME ENVIRONMENT
        ↓
MEASURE
        ↓
INSPECT PLAN / UI
        ↓
CONCLUDE
```

A benchmark result is evidence for a specific workload and environment, not a universal law.

---

## 30. Explain Plans — Bridge to Topic 12

Do not turn this topic into the full Catalyst course.

Instead, learn to ask:

> **"Where did the Python execution appear?"**

Start with:

```python
df.explain("formatted")
```

or another explain mode supported by the installed Spark version.

Compare the plans for:

- built-in implementation;
- Python UDF implementation;
- pandas UDF implementation.

Look for Python evaluation nodes or other indicators of Python execution where applicable.

The goal is:

```text
SEE THE DIFFERENCE
        ↓
UNDERSTAND THE COST
        ↓
PREPARE FOR CATALYST
```

Topic 12 will teach how to inspect Catalyst plans and reason about Spark's optimizer in much greater depth.

---

## 31. Production Decision Framework

Use the following as a starting decision matrix:

| Requirement | Preferred starting point |
|---|---|
| Standard string/date/math logic | Built-in |
| Standard aggregation | Built-in |
| Logic Spark already supports | Built-in |
| Custom scalar Python logic unavailable in Spark | Python UDF if necessary |
| Vectorizable custom Python logic | pandas UDF may be appropriate |
| Expensive setup reused across batches | Iterator pandas UDF may be appropriate |
| Per-group complex pandas processing | `applyInPandas` |
| Arbitrary batch transformation | `mapInPandas` / `mapInArrow` where appropriate |
| Multiple output rows from custom Python logic | Python UDTF where appropriate |
| Custom data-source behavior | Python data source API awareness |

This is not a rigid compiler rule.

The final decision should consider:

- correctness;
- data volume;
- semantics;
- execution model;
- optimizer visibility;
- memory;
- dependency packaging;
- observability;
- benchmark evidence;
- maintainability.

---

## 32. Production Scenarios

### Scenario 1 — Built-in already exists

A team creates a Python UDF for phone normalization even though Spark provides `regexp_replace`.

**Reasoning:**

1. confirm that `regexp_replace` expresses the requirement;
2. compare semantics and edge cases;
3. prefer the native expression if equivalent;
4. remove unnecessary Python execution;
5. benchmark representative data if performance is material.

---

### Scenario 2 — Custom NLP normalization

A company needs custom text normalization unavailable through Spark expressions.

**Reasoning:**

1. confirm that SQL/DataFrame composition cannot express the requirement;
2. determine whether the custom logic is scalar or naturally vectorized;
3. consider pandas UDF if vectorization is appropriate;
4. otherwise consider a Python UDF;
5. package dependencies explicitly;
6. benchmark representative workloads.

---

### Scenario 3 — pandas UDF is fast on small data but slow at scale

Possible causes:

- the workload changes at scale;
- data distribution changes;
- Python becomes CPU-bound;
- memory pressure increases;
- batch behavior changes;
- downstream work dominates;
- partitioning is unsuitable.

**Investigation:**

```text
Correctness
   ↓
same dataset shape
   ↓
partition count
   ↓
task duration
   ↓
CPU
   ↓
memory
   ↓
plan
   ↓
Spark UI
```

Do not conclude "pandas UDFs are bad" from one result.

---

### Scenario 4 — `applyInPandas` causes Python worker OOM

Inspect:

- group-size distribution;
- largest groups;
- number of columns;
- pandas memory amplification;
- Arrow-related data movement;
- Python worker memory;
- skew.

If the operation does not actually require whole-group pandas processing, consider a different API.

---

### Scenario 5 — Filter occurs after an expensive UDF

Ask:

> Is the filter independent of the UDF?

If yes, test:

```text
filter → reduce columns → UDF
```

against:

```text
UDF → filter
```

while preserving semantics.

Measure the amount of data entering Python.

---

### Scenario 6 — UDF imports a 2 GB ML library

Do not immediately place model loading inside a row-at-a-time UDF.

Reason about:

- initialization frequency;
- worker memory;
- dependency distribution;
- model serialization;
- batch processing;
- iterator APIs;
- alternative Spark-native or specialized inference mechanisms.

The correct design depends on the actual model and workload.

---

### Scenario 7 — Works locally, fails on executors

Investigate:

1. executor Python version;
2. installed packages;
3. package versions;
4. native dependencies;
5. environment distribution;
6. submission configuration;
7. cluster/container image.

The driver environment is not proof of executor readiness.

---

### Scenario 8 — Team wants a UDF policy

A useful policy is not:

> "Never use UDFs."

Instead:

1. search for a built-in;
2. use Spark SQL/DataFrame expressions where possible;
3. reduce rows before Python;
4. reduce columns before Python;
5. select an appropriate vectorized API;
6. avoid unnecessarily large grouped pandas operations;
7. package dependencies explicitly;
8. benchmark representative workloads;
9. inspect plans;
10. test NULL and edge cases;
11. document why custom Python is necessary;
12. revisit older UDFs when Spark adds new native functionality.

---

## 33. Hands-On Labs

> **Important:** The roadmap specifies `src/spark_lab/udfs.py`, but this document must not create or modify that file. Implement the exercises in your existing project environment.

### Lab 1 — Phone Number Normalization

Implement the same transformation using:

1. built-in functions;
2. plain Python UDF;
3. Arrow-optimized Python UDF using the installed Spark version's supported API;
4. pandas UDF.

Record:

- correctness;
- runtime;
- CPU;
- memory;
- plan observations.

---

### Lab 2 — Iterator pandas UDF

Build an iterator-of-Series pandas UDF.

Simulate expensive setup such as configuration or lookup initialization.

Observe the difference between:

```text
setup inside repeated processing
```

and:

```text
setup once per appropriate iterator execution context
        ↓
reuse across batches
```

Do not infer a universal Python-worker lifecycle from one local run.

---

### Lab 3 — `applyInPandas`

Build a per-country trend calculation.

Document:

- group boundary;
- pandas DataFrame input;
- output schema;
- memory behavior;
- largest-group risk.

---

### Lab 4 — `mapInPandas`

Build a custom batch transformation.

Then explain why it differs from grouped `applyInPandas`.

---

### Lab 5 — Filter Before UDF

When semantically equivalent, compare:

```text
UDF → filter
```

with:

```text
filter → UDF
```

Measure the effect of reducing rows before Python.

---

### Lab 6 — Explain Plans

Run:

```python
df.explain("formatted")
```

for the built-in and UDF versions.

Identify where Python execution appears, where supported.

---

### Lab 7 — Dependency Packaging

Create a UDF that requires a non-standard package.

Demonstrate:

1. local success;
2. executor dependency failure;
3. correct dependency packaging;
4. successful distributed execution.

Do this in a controlled environment.

---

### Lab 8 — Large-Group Memory Risk

Create a deliberately skewed grouping example.

Use `applyInPandas`.

Do **not** intentionally crash the machine.

Instead:

- create a bounded synthetic example;
- inspect group sizes;
- identify the largest group;
- reason about pandas memory;
- stop before unsafe resource consumption.

---

### Lab 9 — NULL Contract

Create equivalent built-in and Python implementations.

Test:

- `NULL`;
- empty string;
- malformed string;
- valid string.

Document semantic differences.

---

### Lab 10 — Dependency Version Mismatch

Use a deliberately controlled environment to demonstrate a package-version mismatch between driver and executor.

Document:

- symptom;
- root cause;
- packaging fix;
- verification.

---

### Lab 11 — Same Logic, Different APIs

Choose one custom numerical or string transformation and implement it using:

- built-in if possible;
- Python UDF;
- pandas UDF.

Compare:

- correctness;
- plan;
- runtime;
- memory;
- complexity.

---

### Lab 12 — Production Decision Memo

For one custom transformation, write a short engineering memo answering:

1. Can Spark already express it?
2. If not, why?
3. Which extension API is appropriate?
4. How much data enters Python?
5. What are the memory risks?
6. How are dependencies packaged?
7. What benchmark evidence supports the decision?
8. How will it be monitored in production?

---

## 34. Debugging Exercises

For every problem, work through:

**Symptom → likely causes → investigation → fix → verification → production lesson**

### 1. Built-in replaced by Python UDF

**Symptom:** A simple string operation became slower.

**Investigate:** Search the Spark function catalog and compare the plan.

**Fix:** Replace the custom function with an equivalent built-in when semantics match.

**Lesson:** Search for native capability before introducing Python.

---

### 2. UDF makes a pipeline much slower

**Symptom:** Runtime increases substantially after introducing a UDF.

**Investigate:** Measure rows entering Python, inspect the plan, task duration, CPU, memory, and Python execution indicators.

**Fix:** Reduce data before Python or select a more appropriate API.

**Lesson:** UDF cost is workload-dependent.

---

### 3. Wrong return type

**Symptom:** UDF execution fails because the output does not match the declared Spark type.

**Investigate:** Check the Python return values and declared `returnType`.

**Fix:** Correct the contract and add tests.

**Lesson:** Schema is part of the UDF interface.

---

### 4. NULL mishandling

**Symptom:** The UDF throws an exception for missing values.

**Investigate:** Reproduce with explicit `NULL` inputs.

**Fix:** Handle `None` and define expected SQL semantics.

**Lesson:** NULL behavior must be tested.

---

### 5. pandas UDF receives unexpected input shape

**Symptom:** The function assumes one scalar but receives a pandas Series.

**Investigate:** Inspect the selected pandas UDF type and function signature.

**Fix:** Write vectorized logic against the documented input representation.

**Lesson:** API semantics determine the function contract.

---

### 6. `applyInPandas` causes Python worker OOM

**Symptom:** Large groups exhaust Python worker memory.

**Investigate:** Measure group-size distribution and inspect the largest groups.

**Fix:** Reconsider grouped pandas processing, reduce columns, redesign the computation, or use a different execution model.

**Lesson:** One logical group can become one large pandas object.

---

### 7. `mapInPandas` schema mismatch

**Symptom:** Spark rejects the output schema.

**Investigate:** Compare declared schema with output DataFrame columns and types.

**Fix:** Make the schema contract explicit and test small data first.

**Lesson:** Batch APIs still require strict schema discipline.

---

### 8. Iterator pandas UDF has expensive initialization

**Symptom:** Batch processing spends excessive time initializing state.

**Investigate:** Determine where initialization occurs and whether state can be reused safely.

**Fix:** Structure initialization at the appropriate iterator execution scope.

**Lesson:** Initialization strategy matters for distributed Python workloads.

---

### 9. UDF works locally but not on executors

**Symptom:** `ModuleNotFoundError` or version errors occur only in the cluster.

**Investigate:** Compare driver and executor environments.

**Fix:** Package and distribute dependencies explicitly.

**Lesson:** Local Python is not the production executor environment.

---

### 10. Filter occurs after expensive UDF

**Symptom:** Python receives far more rows than necessary.

**Investigate:** Check whether the filter is independent of the UDF.

**Fix:** Move the filter before Python if semantics remain equivalent.

**Lesson:** Reduce data before expensive custom logic.

---

### 11. UDF plan shows limited optimization opportunities

**Symptom:** A native expression and Python UDF produce visibly different physical-plan regions.

**Investigate:** Use `explain("formatted")`.

**Fix:** Replace the UDF with native expressions when possible or document why custom logic is necessary.

**Lesson:** Optimizer visibility is an architectural concern.

---

### 12. "pandas UDF is always faster"

**Symptom:** A pandas UDF is slower than a built-in or ordinary implementation.

**Investigate:** Check whether the logic is actually vectorizable, whether Python dominates, whether data volume is appropriate, and whether the native expression already solves the problem.

**Fix:** Choose the API based on semantics and measured evidence.

**Lesson:** There is no universal fastest UDF type.

---

## 35. Common Misconceptions

### 1. "UDFs are always bad."

**Correct mental model:** UDFs are appropriate when custom logic is genuinely required. The engineering goal is to use the highest-level suitable API.

### 2. "pandas UDFs are always faster."

**Correct mental model:** They can reduce certain Python/JVM overheads and exploit vectorization, but workload, data shape, algorithm, memory, and native alternatives matter.

### 3. "Arrow makes every Python operation fast."

**Correct mental model:** Arrow improves supported data interchange paths. It does not make arbitrary Python algorithms cheap.

### 4. "Built-ins are just Python functions."

**Correct mental model:** A built-in generally represents a Spark-native expression that Spark understands.

### 5. "A Python UDF runs on the driver."

**Correct mental model:** The UDF's custom logic executes in Python worker processes associated with distributed task execution.

### 6. "A Python UDF automatically runs in parallel inside one Python process."

**Correct mental model:** Spark distributes tasks; Python workers and task/process behavior depend on execution configuration.

### 7. "`cache()` fixes UDF performance."

**Correct mental model:** Caching can avoid recomputing reused results. It does not remove Python execution from the computation.

### 8. "`applyInPandas` distributes each group across unlimited Python memory."

**Correct mental model:** A logical group is a unit presented to the Python function. A huge group can create a large pandas object and memory pressure.

### 9. "pandas means the entire Spark DataFrame becomes one pandas DataFrame."

**Correct mental model:** Supported pandas APIs operate on distributed batches or groups according to their semantics.

### 10. "Arrow and pandas UDF are exactly the same thing."

**Correct mental model:** Arrow is a data-interchange technology; pandas UDFs are a Spark Python API pattern that can use Arrow.

### 11. "Python UDFs are visible to Catalyst in the same way as built-ins."

**Correct mental model:** Spark has much less semantic visibility into arbitrary Python code than into native expressions.

### 12. "If it works locally, it will work on executors."

**Correct mental model:** Executor environments must contain compatible Python dependencies.

### 13. "Imports inside a UDF are always harmless."

**Correct mental model:** Imports and initialization can contribute to worker overhead and dependency/resource problems.

### 14. "More executors automatically solve Python UDF overhead."

**Correct mental model:** More distributed capacity does not remove per-record Python overhead, skew, memory constraints, or poor execution design.

### 15. "A UDF after a filter costs the same as a UDF before a filter."

**Correct mental model:** If the filter reduces rows before Python, total custom Python work can be lower.

### 16. "UDTF and UDF are interchangeable."

**Correct mental model:** A scalar UDF produces a value; a UDTF naturally produces rows.

### 17. "`mapInPandas` and `applyInPandas` are the same."

**Correct mental model:** One is batch-oriented; the other is grouped-processing-oriented.

### 18. "A pandas UDF eliminates serialization."

**Correct mental model:** Arrow can make supported interchange more efficient; data still crosses execution boundaries.

### 19. "Benchmarking one million rows proves production performance."

**Correct mental model:** Production data volume, distribution, partitions, memory, and downstream operations can change the result.

### 20. "If the output is correct, the implementation is production-ready."

**Correct mental model:** Production readiness also requires performance evidence, memory analysis, dependency packaging, observability, testing, and maintainability.

---

## 36. Practice Questions

Exactly **40** questions follow: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced.

### 36.1 Basic — 10 Questions

1. What is a Spark built-in function, and why is it usually considered before a Python UDF?
2. Given `F.lower(F.col("email"))`, what kind of object is Spark building?
3. What problem does a Python UDF solve that a built-in may not?
4. Why does a Python UDF require a return type?
5. How should a scalar Python UDF normally handle a missing string value?
6. What is the conceptual role of a Python worker?
7. What is Arrow in the context of Python/Spark data interchange?
8. What is the main difference between a pandas UDF and a plain Python UDF at a high level?
9. Why does `applyInPandas` have a different memory model from a simple Series → Series pandas UDF?
10. Why should a developer inspect Spark's built-in functions before writing custom Python?

### 36.2 Moderate — 10 Questions

11. Spark provides `regexp_replace`. Why might a Python UDF be the wrong choice for phone normalization?
12. Given a Python UDF with `returnType=T.IntegerType()` that sometimes returns strings, what should you investigate?
13. Why can filtering rows before a Python UDF reduce total execution cost?
14. Explain the conceptual JVM → Python worker → JVM path for a Python UDF.
15. Why does Arrow not automatically make an arbitrary Python UDF fast?
16. Explain the difference between Series → Series and iterator-of-Series → iterator-of-Series pandas UDFs.
17. When is `applyInPandas` more appropriate than a simple pandas UDF?
18. When is `mapInPandas` more natural than `applyInPandas`?
19. Why can a large group cause `applyInPandas` to consume excessive memory?
20. What is the difference between an executor dependency problem and a UDF logic bug?

### 36.3 Hard — 10 Questions

21. Two equivalent pipelines exist: `UDF → filter` and `filter → UDF`. What conditions must be true before moving the filter earlier?
22. A pandas UDF is slower than a Spark built-in for the same transformation. Give several technically plausible reasons.
23. A team claims "Arrow removes serialization." Correct the statement precisely.
24. A plan contains a Python evaluation region where the equivalent built-in plan does not. What does that suggest about optimizer visibility?
25. Given a per-country modeling requirement, what makes `applyInPandas` attractive and what is its principal memory risk?
26. A UDF loads a large model. Why might an iterator pandas UDF be worth considering?
27. How would you design a benchmark comparing built-in, Python UDF, Arrow-optimized UDF, and pandas UDF implementations?
28. A UDF works on the driver but fails on executors with `ModuleNotFoundError`. How would you diagnose it?
29. Why can adding executors fail to solve a skewed `applyInPandas` workload?
30. Explain why `mapInArrow` can be conceptually different from pandas-based batch processing.

### 36.4 Advanced — 10 Questions

31. Design an implementation decision for a 5-billion-row normalization pipeline where Spark has a native expression for 95% of the logic and custom Python is required for the remaining 5%.
32. Design a custom inference transformation where model initialization is expensive and the input is large. Compare at least three execution models.
33. A grouped pandas operation OOMs only in production. Design an investigation that separates skew, group size, pandas memory amplification, and dependency/resource issues.
34. Define a production policy that permits Python UDFs without turning the team into "UDFs are forbidden" or "anything goes."
35. How would you prove that a filter-before-UDF rewrite is both semantically safe and operationally beneficial?
36. Design a benchmark experiment that remains meaningful when one implementation has a different execution plan from another.
37. Explain how optimizer visibility should influence API selection even when two implementations produce identical results.
38. A team wants a custom function that emits multiple output rows per input. Explain why a UDTF may be a better abstraction than a scalar UDF.
39. Explain how dependency packaging, Python worker memory, optimizer visibility, and data volume interact in a production UDF decision.
40. Build a decision tree that chooses among built-ins, Python UDFs, pandas UDFs, `applyInPandas`, `mapInPandas`, `mapInArrow`, and UDTFs.

---

## 37. Interview Practice

Exactly **40** interview questions follow: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced.

### 37.1 Basic — 10 Questions

1. What is the difference between a Spark built-in function and a Python UDF?
   - **Answer guidance:** Built-ins form Spark-native expressions; Python UDFs execute custom Python logic and introduce a Python execution boundary.

2. Why are built-ins generally preferred?
   - **Answer guidance:** They provide Spark with semantic visibility and more opportunities for native execution and optimization.

3. What does `@F.udf` do?
   - **Answer guidance:** It exposes a Python function as a Spark UDF expression.

4. Why is a UDF return type important?
   - **Answer guidance:** It defines the Spark schema contract for the function's output.

5. How should Python UDF code handle SQL NULL?
   - **Answer guidance:** Explicitly handle Python `None` and return the intended null result.

6. What is a Python worker?
   - **Answer guidance:** A Python process used by Spark task execution for supported Python operations.

7. What is Arrow?
   - **Answer guidance:** A columnar data representation/interchange technology used in supported Spark/Python execution paths.

8. What is a pandas UDF?
   - **Answer guidance:** A Spark Python UDF pattern that operates on pandas-oriented batches/objects for supported execution styles.

9. What is `applyInPandas`?
   - **Answer guidance:** A grouped API that presents each group to a Python function as a pandas DataFrame and returns a pandas DataFrame matching the declared schema.

10. What is the purpose of a Python UDTF?
    - **Answer guidance:** To implement custom table-producing logic that naturally emits multiple output rows.

### 37.2 Moderate — 10 Questions

11. Explain the Python/JVM boundary for a scalar Python UDF.
    - **Answer guidance:** Spark task execution crosses into a Python worker, performs custom Python computation, and returns results to Spark; data conversion/communication can add cost.

12. Why can row-at-a-time Python UDFs be expensive?
    - **Answer guidance:** Function invocation, Python interpreter work, data conversion, boundary overhead, and reduced optimizer visibility can accumulate.

13. How does a pandas UDF change the execution model?
    - **Answer guidance:** It processes supported data in batches and uses pandas-oriented vectorized operations, with Arrow involved in supported interchange.

14. Explain iterator pandas UDFs.
    - **Answer guidance:** They consume and produce iterators of pandas Series and can structure reusable initialization around batch processing.

15. Why can `applyInPandas` be dangerous with skew?
    - **Answer guidance:** A very large group can become a large pandas DataFrame in one Python execution context, causing memory pressure.

16. Why might `mapInPandas` be preferred for batch logic?
    - **Answer guidance:** Its unit of processing is batch-oriented rather than a logical group.

17. Why does dependency packaging matter?
    - **Answer guidance:** Python code runs on executors, so required packages and compatible versions must be present there.

18. What does "filter first, UDF last" mean?
    - **Answer guidance:** Reduce rows and columns before expensive Python execution when the transformation reorder is semantically safe.

19. Why should explain plans be compared?
    - **Answer guidance:** They show how Spark represents and executes the alternatives and can expose Python evaluation regions.

20. Why is pandas UDF not automatically faster than a Python UDF?
    - **Answer guidance:** Performance depends on vectorizability, data volume, memory, native alternatives, algorithm, and execution conditions.

### 37.3 Hard — 10 Questions

21. A Spark built-in and a Python UDF produce the same result. Why can their plans differ?
    - **Answer guidance:** The built-in is represented as a Spark-native expression; the Python function is an external/custom computation boundary.

22. How would you diagnose a Python UDF that makes a job 10× slower?
    - **Answer guidance:** Establish correctness, measure rows entering Python, inspect the plan and UI, compare CPU/memory/task time, and test native/vectorized alternatives.

23. What is the role of Arrow in pandas UDF execution?
    - **Answer guidance:** It supports efficient columnar interchange between Spark-side execution and Python/pandas for supported APIs.

24. Why does `applyInPandas` have a different memory risk from a Series → Series pandas UDF?
    - **Answer guidance:** `applyInPandas` is group-oriented and can materialize a whole logical group as a pandas DataFrame.

25. How would you safely handle expensive model initialization?
    - **Answer guidance:** Choose an API with an appropriate batch/iterator execution model, avoid unnecessary per-row initialization, package dependencies, and measure memory/latency.

26. Why does adding executors not necessarily solve UDF performance?
    - **Answer guidance:** Python overhead, skew, per-worker memory, and optimizer limitations remain; more capacity does not change the execution semantics.

27. How would you benchmark four equivalent UDF implementations?
    - **Answer guidance:** Same data, cluster, configuration, partitions, action, output, warm-up approach, correctness checks, repeated measurements, plan/UI inspection.

28. What would you look for in `explain("formatted")`?
    - **Answer guidance:** Identify where Python evaluation occurs and compare it with the native expression plan without trying to interpret the entire Catalyst system yet.

29. How should a team decide whether to allow Python UDFs?
    - **Answer guidance:** Allow them when justified, require a native-function search, data reduction, API selection, dependency packaging, correctness tests, plan inspection, and representative benchmarks.

30. What is the difference between `mapInArrow` and `mapInPandas`?
    - **Answer guidance:** One is Arrow RecordBatch-oriented; the other uses pandas DataFrame batches. The appropriate representation depends on the algorithm and API support.

### 37.4 Advanced — 10 Questions

31. Design an API-selection framework for a large Spark platform.
    - **Answer guidance:** Start with native expressions, then specialized Spark APIs, then the least expensive suitable Python extension, and require evidence for production exceptions.

32. How would you prevent a custom Python transformation from becoming a hidden platform-wide bottleneck?
    - **Answer guidance:** Establish policy, benchmark standards, plan inspection, observability, dependency controls, ownership, and periodic review.

33. How would you reason about a UDF that is fast at small scale but fails at large scale?
    - **Answer guidance:** Analyze data volume, distribution, partitioning, Python CPU, memory, group size, dependency footprint, and downstream operations.

34. Explain why a UDF can affect optimizer visibility without making the entire surrounding plan unoptimizable.
    - **Answer guidance:** The custom expression itself has limited semantic visibility, while Spark can still optimize other independent parts of the plan.

35. Design a safe experiment for a large-group `applyInPandas` workload.
    - **Answer guidance:** Measure group-size distribution, use bounded synthetic data, limit resource consumption, inspect Python worker memory, and avoid intentionally exhausting the environment.

36. How would you design dependency distribution for custom Spark Python code?
    - **Answer guidance:** Pin compatible versions, distribute the environment consistently, validate on executors, and make deployment reproducible.

37. When would a UDTF be a better abstraction than a UDF?
    - **Answer guidance:** When the custom logic naturally emits multiple rows rather than one scalar output per input.

38. What is the difference between a UDF and a Python data source API?
    - **Answer guidance:** A UDF extends computation over data; a Python data source API extends data-source integration.

39. How would you make a UDF decision auditable?
    - **Answer guidance:** Document the native alternatives considered, semantics, expected data volume, API choice, dependency requirements, benchmark evidence, plan observations, and memory risks.

40. What would convince you that a custom Python implementation is production-ready?
    - **Answer guidance:** Correctness, representative benchmark evidence, acceptable memory/resource behavior, executor-ready dependencies, explain-plan understanding, observability, tests, and a documented rationale.

---

## 38. Architecture Scenarios

For each scenario, reason about:

- correctness;
- data volume;
- execution model;
- Python/JVM boundary;
- optimizer visibility;
- memory;
- dependency packaging;
- scalability;
- observability;
- benchmark evidence.

### Scenario 1 — Five Billion Record Normalization

Design a phone/email normalization pipeline for 5 billion records.

Questions:

- Which logic can remain Spark-native?
- Which logic truly requires Python?
- How will rows and columns be reduced first?
- How will the custom path be benchmarked?

---

### Scenario 2 — Custom ML Inference

Design a custom ML inference transformation.

Consider:

- model size;
- initialization;
- Python worker memory;
- batching;
- dependency packaging;
- failure handling;
- latency versus throughput.

Compare at least three possible implementation models.

---

### Scenario 3 — Per-Country Modeling

Design a per-country model-fitting pipeline.

Consider:

- group size;
- skew;
- `applyInPandas`;
- output schema;
- Python memory;
- model initialization;
- monitoring.

---

### Scenario 4 — Arbitrary Batch Transformation

Design a custom transformation that operates on batches but does not need complete logical groups.

Compare:

- pandas UDF;
- `mapInPandas`;
- `mapInArrow`.

Explain the unit of processing for each.

---

### Scenario 5 — Team UDF Governance

Design a platform policy deciding when developers may introduce Python UDFs.

Include:

- native-function search;
- semantic review;
- benchmark evidence;
- dependency packaging;
- plan inspection;
- ownership;
- review of old UDFs.

---

### Scenario 6 — Dependency Distribution

Design a reproducible dependency strategy for a Spark cluster where Python workers need several non-standard packages.

Consider:

- version pinning;
- executor environment;
- deployment;
- validation;
- native libraries;
- rollback.

---

### Scenario 7 — Production pandas OOM

A production `applyInPandas` pipeline fails intermittently with Python worker OOM.

Design the investigation.

Include:

- group-size distribution;
- skew;
- columns;
- pandas memory;
- Python worker memory;
- executor configuration;
- alternative APIs.

---

### Scenario 8 — UDF Benchmarking Platform

Design a framework that lets engineers compare custom Spark functions fairly.

It should record:

- correctness;
- runtime;
- task duration;
- CPU;
- memory;
- shuffle;
- spills;
- plan;
- Spark configuration;
- data characteristics.

The framework should prevent teams from turning one small benchmark into a universal performance claim.

---

## 39. Production UDF Policy

A practical team policy can be:

1. **Search for a built-in first.**
2. **Use Spark SQL/DataFrame expressions where possible.**
3. **Reduce rows before entering Python.**
4. **Reduce columns before entering Python.**
5. **Use vectorized approaches when appropriate.**
6. **Avoid unnecessarily large grouped pandas operations.**
7. **Package dependencies explicitly.**
8. **Benchmark representative workloads.**
9. **Inspect plans.**
10. **Test NULL and edge cases.**
11. **Document why a UDF is necessary.**
12. **Revisit old UDFs when Spark adds new built-ins.**

The policy should encourage engineering discipline rather than banning UDFs.

---

## 40. Performance Checklist

### Before Writing a UDF

- [ ] Does Spark already have a built-in?
- [ ] Can SQL express the logic?
- [ ] Can DataFrame expressions express the logic?
- [ ] Can I filter rows first?
- [ ] Can I select fewer columns first?
- [ ] Is the custom logic actually necessary?

### If Python Is Necessary

- [ ] Should this be a Python UDF?
- [ ] Should it use an Arrow-optimized Python UDF mechanism?
- [ ] Should it be a pandas UDF?
- [ ] Should it be iterator-based?
- [ ] Is grouped processing necessary?
- [ ] Could `applyInPandas` create a huge group?
- [ ] Is `mapInPandas` more appropriate?
- [ ] Is `mapInArrow` appropriate?
- [ ] Is a UDTF the right abstraction?
- [ ] Are dependencies packaged for executors?

### After Implementation

- [ ] Validate correctness.
- [ ] Test NULLs.
- [ ] Test empty input.
- [ ] Test large input.
- [ ] Explain the plan.
- [ ] Benchmark.
- [ ] Inspect Spark UI.
- [ ] Measure memory.
- [ ] Record the decision.

---

## 41. Learning Loop

Apply the Module 2.14 learning loop:

```text
READ
  ↓
PREDICT
  ↓
WRITE IT
  ↓
EXPLAIN THE PLAN
  ↓
RUN SMALL
  ↓
RUN BIG
  ↓
READ SPARK UI
  ↓
CHANGE ONE THING
  ↓
MEASURE AGAIN
  ↓
WRITE IT DOWN
  ↓
EXPLAIN ALOUD
```

### Apply it to UDFs

1. Predict why the built-in should be preferable.
2. Implement the built-in.
3. Implement a Python UDF.
4. Implement a pandas UDF.
5. Compare plans.
6. Run on small data.
7. Run on larger data.
8. Inspect the UI.
9. Change only the UDF implementation.
10. Measure.
11. Explain the result.

The objective is not to memorize a ranking.

The objective is to build evidence-based execution-model judgment.

---

## 42. Final Decision Tree

```text
START
  |
  v
Can Spark built-ins / SQL express the logic?
  |
  +-- YES --> USE BUILT-IN / SQL
  |
  +-- NO
        |
        v
Is custom Python genuinely required?
        |
        +-- NO --> RE-DESIGN WITH SPARK-NATIVE OPERATIONS
        |
        +-- YES
              |
              v
Is the logic naturally vectorizable?
              |
              +-- YES --> pandas UDF / appropriate Arrow-based API
              |
              +-- NO
                    |
                    v
Is row-wise custom logic unavoidable?
                    |
                    +-- YES --> Python UDF
                    |
                    v
Does the logic operate per group?
                    |
                    +-- YES --> applyInPandas where appropriate
                    |
                    v
Does the logic operate per batch?
                    |
                    +-- YES --> mapInPandas / mapInArrow where appropriate
                    |
                    v
Does the function naturally produce multiple rows?
                    |
                    +-- YES --> consider Python UDTF
                    |
                    v
BENCHMARK
  ↓
INSPECT PLAN
  ↓
VALIDATE MEMORY
  ↓
DOCUMENT DECISION
```

This is a conceptual decision aid, not a rigid compiler rule. Actual API selection must follow semantics and the supported Spark version.

---

## 43. Learning Checkpoints

### Beginner

- [ ] Explain what a built-in Spark function is.
- [ ] Explain what a Python UDF is.
- [ ] Create a simple Python UDF.
- [ ] Declare a return type.
- [ ] Handle NULL values.
- [ ] Explain why built-ins are generally preferred.

### Intermediate

- [ ] Explain the Python/JVM boundary.
- [ ] Explain Arrow.
- [ ] Create a pandas UDF.
- [ ] Explain Series → Series.
- [ ] Explain iterator pandas UDFs.
- [ ] Explain `applyInPandas`.
- [ ] Explain `mapInPandas`.
- [ ] Explain `mapInArrow`.

### Advanced

- [ ] Explain optimizer visibility.
- [ ] Explain filter-before-UDF.
- [ ] Diagnose `applyInPandas` memory risks.
- [ ] Package dependencies for executors.
- [ ] Compare implementations with benchmarks.
- [ ] Explain Python UDTFs at an awareness level.
- [ ] Explain the Python data source API at an awareness level.
- [ ] Make a production UDF decision.

---

## 44. Final Assessment

### Part A — Conceptual: 10 Questions

1. Explain why Spark-native expressions are generally preferred.
2. Explain the Python/JVM boundary.
3. Explain ordinary Python UDF execution.
4. Explain Arrow's role.
5. Explain pandas UDF batching.
6. Explain iterator pandas UDFs.
7. Explain `applyInPandas` memory risk.
8. Explain `mapInPandas`.
9. Explain UDTFs versus scalar UDFs.
10. Explain why optimizer visibility matters.

### Part B — Code: 10 Questions

1. Write a built-in phone normalization expression.
2. Write a NULL-safe Python UDF.
3. Declare an appropriate string return type.
4. Write a Series → Series pandas UDF.
5. Sketch an iterator-of-Series pandas UDF.
6. Write an `applyInPandas` per-group transformation specification.
7. Sketch a `mapInPandas` batch transformation.
8. Show a filter-before-UDF rewrite.
9. Show an `explain("formatted")` call.
10. Show how you would structure a benchmark harness.

### Part C — Performance: 5 Scenarios

1. Python UDF is slower than a built-in.
2. pandas UDF is slower than expected.
3. `applyInPandas` OOMs on large groups.
4. Filtering before Python reduces runtime.
5. More executors do not solve the bottleneck.

For each, require evidence rather than intuition.

### Part D — Debugging: 5 Scenarios

1. Executor `ModuleNotFoundError`.
2. UDF return-type mismatch.
3. NULL failure.
4. pandas output schema mismatch.
5. Unexpected Python-worker memory pressure.

For each, provide symptom → cause → investigation → fix → verification.

### Part E — Architecture: 5 Scenarios

1. Five-billion-row normalization.
2. Custom ML inference.
3. Per-country modeling.
4. Team UDF governance.
5. Production benchmarking platform.

The learner passes this topic only when they can justify an execution-model choice rather than merely reproduce syntax.

---

## 45. Glossary

**Built-in function** — A Spark-supported function that forms part of Spark's native expression system.

**Spark expression** — A structured expression representing computation in Spark's DataFrame/SQL model.

**UDF** — User-defined function exposed to Spark as a callable data-processing operation.

**Python UDF** — A UDF whose custom function logic executes in Python.

**Python worker** — A Python process used by Spark for supported Python execution.

**JVM** — Java Virtual Machine; Spark's core execution environment is JVM-based.

**Serialization** — Converting data into a representation suitable for transfer or storage.

**Deserialization** — Reconstructing data from a serialized representation.

**Arrow** — A columnar data representation and interchange technology used by supported systems and Spark/Python execution paths.

**pandas UDF** — A Spark Python UDF pattern using pandas-oriented inputs/outputs for supported vectorized execution.

**Vectorization** — Applying operations to batches/arrays rather than invoking custom scalar Python logic independently for each value.

**Batch** — A bounded set of records processed together.

**Series** — A one-dimensional pandas data structure.

**Iterator pandas UDF** — A pandas UDF pattern consuming and producing iterators of pandas objects.

**`applyInPandas`** — A grouped Spark API that applies a pandas function to each logical group.

**`mapInPandas`** — A batch-oriented Spark API that applies a pandas function to batches.

**`mapInArrow`** — An Arrow RecordBatch-oriented custom processing API.

**Grouped processing** — Processing records according to a logical grouping key.

**Python UDTF** — Python User Defined Table Function; custom logic that can produce table rows.

**Python data source API** — Spark Python extensibility for custom data-source behavior.

**Catalyst** — Spark SQL's optimizer framework.

**Predicate pushdown** — Moving filtering closer to a data source when the source and plan permit it.

**Code generation** — Generating executable code for supported Spark expressions/operators.

**Optimizer visibility** — The degree to which Spark can understand the semantics of a computation and reason about it.

**Executor dependency** — A Python package, library, or environment requirement needed by code running on executors.

**Schema** — The structured description of columns, types, and nullability.

**Return type** — The Spark data type declared for a UDF result.

**NULL handling** — The explicit treatment of missing SQL values and their Python representation.

**Skew** — Uneven distribution of data that causes some tasks or groups to be much larger than others.

**Python worker memory** — Memory available to the Python execution process, including Python/pandas/Arrow-related objects and application state.

---

## 46. Common Production Questions

### Why is my UDF slow?

Check:

1. whether a built-in already exists;
2. how many rows enter Python;
3. how many columns enter Python;
4. Python CPU cost;
5. serialization/data-transfer overhead;
6. batch/grouping semantics;
7. dependency initialization;
8. memory pressure;
9. plan differences;
10. representative benchmark results.

### Why is my pandas UDF not faster?

Possible explanations include:

- the built-in is already highly optimized;
- the custom logic is not sufficiently vectorizable;
- Python computation dominates;
- the data is too small for the batching advantage to matter;
- memory pressure dominates;
- grouping or partitioning is poor;
- another downstream operation dominates.

Measure rather than assume.

### Why does `applyInPandas` run out of memory?

Investigate:

- largest group size;
- skew;
- selected columns;
- pandas object memory;
- Arrow-related batches;
- Python worker memory;
- model/library memory.

### Why does my UDF work locally but fail on the cluster?

Compare:

- Python version;
- installed packages;
- package versions;
- native libraries;
- executor environment;
- dependency-distribution mechanism.

### Why did filtering before the UDF improve performance?

Because fewer rows entered the expensive custom Python computation.

Verify that the rewrite is semantically equivalent.

### Why does Spark optimize my built-in expression but not my Python function?

Spark has structured semantic information about supported native expressions. Arbitrary Python code exposes less of its internal computation to Spark's optimizer.

### How do I decide between a Python UDF and pandas UDF?

Ask:

1. Is custom Python truly required?
2. Is the logic naturally vectorizable?
3. Is the data representation suitable for pandas?
4. What are the memory requirements?
5. What does a representative benchmark show?

### When should I avoid pandas entirely?

Avoid it when:

- Spark-native expressions solve the problem;
- the algorithm is not naturally vectorizable;
- grouped pandas processing creates unacceptable memory risk;
- a different Spark API fits the semantics better.

### How do I benchmark UDF implementations?

Use identical:

- data;
- logic;
- cluster;
- Spark configuration;
- partitioning;
- action;
- output.

Then measure runtime, task behavior, CPU, memory, shuffle/spill, plan, and correctness.

### How do I know whether custom logic belongs in Spark at all?

Ask whether:

- the operation is naturally distributed;
- the Python dependency is necessary;
- the data volume justifies distributed execution;
- the computation can be expressed with native Spark operations;
- a different processing architecture is more appropriate.

---

## 47. Connection to the Next Topic

This topic intentionally stops short of fully teaching Catalyst.

You should now understand:

```text
Built-in expression
        ↓
Spark can see the expression
        ↓
optimization opportunities


Python UDF
        ↓
custom Python boundary
        ↓
less semantic visibility
        ↓
different execution characteristics
```

The next topic is:

> **Topic 12 — Catalyst Optimizer and Explain Plans**

Topic 12 will teach how to inspect and reason about Spark's logical and physical planning system in much greater depth.

The key bridge is:

> **Now that you understand why Python UDFs can reduce Spark's visibility into your computation, Topic 12 will teach you how to inspect Catalyst's plans directly.**

---

## 48. Topic Completion Standard

Do not consider this topic complete merely because you can write:

```python
@F.udf(...)
```

You should be able to:

- explain built-in Spark functions;
- explain why native expressions are generally preferred;
- implement a NULL-safe Python UDF;
- explain return types;
- explain Python worker execution;
- explain the JVM/Python boundary;
- explain serialization conceptually;
- explain Arrow's role;
- distinguish Arrow-optimized Python UDFs from pandas UDFs;
- explain Series → Series pandas UDFs;
- explain iterator pandas UDFs;
- explain grouped aggregation pandas UDF use cases;
- explain `applyInPandas`;
- explain `mapInPandas`;
- explain `mapInArrow`;
- explain Python UDTFs at an awareness level;
- explain the Python data source API at an awareness level;
- diagnose `applyInPandas` memory risks;
- explain optimizer visibility;
- apply filter-first/UDF-last safely;
- package executor dependencies;
- benchmark equivalent implementations;
- inspect explain plans for Python execution;
- make a production API-selection decision;
- defend that decision with evidence.

---

## 49. Final Self-Review

Before moving to Topic 12, verify:

- [ ] Built-in functions are thoroughly explained.
- [ ] Why built-ins are preferred is explained.
- [ ] Python UDF fundamentals are explained.
- [ ] Python worker execution model is explained.
- [ ] JVM/Python boundary is explained.
- [ ] Serialization is explained.
- [ ] Return types are explained.
- [ ] NULL handling is explained.
- [ ] Arrow is connected to earlier learning.
- [ ] Arrow-optimized Python UDFs are covered.
- [ ] pandas UDFs are covered.
- [ ] Series → Series is covered.
- [ ] Iterator of Series → Iterator of Series is covered.
- [ ] Series → scalar / aggregation use case is covered.
- [ ] `applyInPandas` is covered.
- [ ] `mapInPandas` is covered.
- [ ] `mapInArrow` is covered.
- [ ] Python UDTFs are covered at the required awareness level.
- [ ] Python data source API is covered at the required awareness level.
- [ ] `applyInPandas` memory risk is explained.
- [ ] UDF optimizer impact is explained.
- [ ] Predicate pushdown limitations are explained carefully.
- [ ] Code generation limitations are explained carefully.
- [ ] Filter-first/UDF-last is demonstrated.
- [ ] Dependency packaging is covered.
- [ ] Heavy library/model initialization is discussed.
- [ ] Benchmark discipline is covered.
- [ ] Same logic is implemented conceptually in multiple ways.
- [ ] Explain-plan comparison is included.
- [ ] At least 8 hands-on labs/exercises are specified.
- [ ] At least 12 debugging exercises exist.
- [ ] At least 20 misconceptions exist.
- [ ] Exactly 40 practice questions exist.
- [ ] Exactly 40 interview questions exist.
- [ ] At least 8 architecture scenarios exist.
- [ ] Production UDF policy exists.
- [ ] Performance checklist exists.
- [ ] Learning checkpoints exist.
- [ ] Final assessment exists.
- [ ] Glossary exists.
- [ ] Beginner → intermediate → advanced progression is clear.
- [ ] Spark 4.x awareness is maintained.
- [ ] No benchmark numbers are fabricated.
- [ ] No deep duplication of Topic 12 exists.
- [ ] No deep duplication of Topic 15 exists.
- [ ] Only the target artifact is being delivered.

---

## 50. Summary

The central lesson is:

> **Choose the computation model, not merely the API that is easiest to type.**

Use Spark-native built-ins when they correctly express the requirement.

Use Python only when custom logic is genuinely necessary.

When Python is necessary, choose the execution model deliberately:

```text
Built-in / SQL
      ↓
Specialized Spark API
      ↓
pandas UDF / Arrow-oriented API when vectorization fits
      ↓
Python UDF when scalar custom logic is unavoidable
      ↓
applyInPandas for group-oriented pandas processing
      ↓
mapInPandas / mapInArrow for batch-oriented custom processing
      ↓
UDTF when the natural output is multiple rows
```

Then validate the decision:

```text
Correctness
    ↓
Data reduction
    ↓
Execution-model analysis
    ↓
Dependency packaging
    ↓
Explain plan
    ↓
Benchmark
    ↓
Memory analysis
    ↓
Spark UI evidence
    ↓
Production decision
```

The expert skill is not knowing every UDF API by memory.

The expert skill is being able to answer:

> **Can Spark already do this?**

> **If not, what is the correct extension mechanism?**

> **How much data will enter Python?**

> **What happens at the JVM/Python boundary?**

> **Will this create a memory problem?**

> **Will this reduce optimizer visibility?**

> **Can I reduce the data before invoking Python?**

> **Are dependencies available on executors?**

> **What does a fair benchmark prove?**

> **Can I defend this implementation as a production engineering decision?**
