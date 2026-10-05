# Claude Code Prompt — Build `05-numba-and-cython-for-hot-loops.md`

## ROLE

Act as a **Senior Data Engineer with 10+ years of production industry experience**, specializing in:

- Python performance engineering
- Data Engineering
- NumPy and vectorization
- pandas and Polars
- Numba
- Cython
- Native Python extensions
- CPU optimization
- Parallel computing
- Distributed data processing
- Apache Spark
- Dask
- Ray
- Production packaging and deployment
- Benchmarking and profiling

You are also an expert technical educator.

Your responsibility is to create a **production-oriented learning module** that teaches the learner how to identify, optimize, compile, test, benchmark, package, deploy, and operationalize Python hot loops using **Numba and Cython**.

Teach the subject progressively:

```text
Basic
  ↓
Why Python loops become bottlenecks
  ↓
When compilation is justified
  ↓
Numba fundamentals
  ↓
Numba optimization
  ↓
Numba parallelism
  ↓
DataFrame integration
  ↓
Cython fundamentals
  ↓
Cython static typing
  ↓
Typed memoryviews
  ↓
GIL / nogil
  ↓
Correctness testing
  ↓
Packaging and deployment
  ↓
Distributed-engine integration
  ↓
Production decision
```

The final document must teach **why and when** to use Numba/Cython, not merely how to write decorators or `.pyx` files.

---

# TASK

You are working inside:

```text
21-Performance-Scaling-and-Cost-Optimization/
```

The target file is:

```text
05-numba-and-cython-for-hot-loops.md
```

Your task is to **write/update ONLY**:

```text
05-numba-and-cython-for-hot-loops.md
```

---

# ABSOLUTE FILE-SCOPE RULE

Do NOT modify, create, rename, delete, or reorganize any other file or folder.

Do not modify:

```text
README.md
01-estimating-data-size-and-memory-footprint.md
02-predicate-pushdown-and-projection-pruning.md
03-parallel-dataframes-with-dask.md
04-ray-data-overview.md
06-benchmarking-pipelines.md
07-compute-cost-optimization.md
practice-questions.md
```

Only:

```text
05-numba-and-cython-for-hot-loops.md
```

may be changed.

Do not create the `workloads/hot_loops/` directory. Describe the hands-on project inside this Markdown file only.

---

# SOURCE OF TRUTH — MODULE 2.21 ROADMAP

The authoritative roadmap is:

```text
Stage 2
└── 21-Performance-Scaling-and-Cost-Optimization/
    └── 05-numba-and-cython-for-hot-loops.md
```

This topic belongs to:

```text
Phase C — Speed Up the Hot Path
```

and is explicitly an **Advanced** topic.

The module's optimization ladder is:

```text
1. Do less work
        ↓
2. Use a better engine
        ↓
3. Use more cores
        ↓
4. Use more machines
        ↓
5. Compile hot loops
```

Therefore, this file must teach an extremely important engineering principle:

> **Compilation is not the first optimization technique.**

The learner must understand that the correct sequence is:

```text
Profile
  ↓
Identify the hot loop
  ↓
Try vectorized NumPy
  ↓
Try Polars expressions / SQL where appropriate
  ↓
Measure again
  ↓
If the loop is still the bottleneck
  ↓
Consider Numba or Cython
```

Do not teach Numba/Cython as automatic replacements for vectorization or better query plans.

---

# WHY THIS TOPIC EXISTS

The roadmap explains that some logic cannot be conveniently vectorized, including examples such as:

- sequential state machines
- custom sessionization
- unusual parsing
- complex scoring

When profiling proves that such a Python loop is the bottleneck, compilation can provide very large speedups.

Teach this concept carefully.

Do NOT promise a fixed performance multiplier.

The learner must understand:

```text
10× faster
100× faster
1.2× faster
No improvement
Slower
```

are all possible outcomes depending on:

- workload
- data types
- algorithm
- memory access
- vectorization
- compilation overhead
- CPU architecture
- parallelism
- Python interactions
- benchmark methodology

Never manufacture benchmark results.

---

# PRIMARY LEARNING OBJECTIVE

By the end of this file, the learner must be able to:

1. Explain what a hot loop is.
2. Explain why Python loops can become performance bottlenecks.
3. Explain why profiling must happen before compilation.
4. Explain why vectorization should usually be attempted first.
5. Explain when SQL/Polars/NumPy can replace a Python loop.
6. Decide when Numba is justified.
7. Decide when Cython is justified.
8. Explain the difference between JIT compilation and ahead-of-time compilation.
9. Use Numba's `@njit`.
10. Understand Numba's nopython mode.
11. Understand Numba supported types/features.
12. Understand compilation overhead.
13. Understand specialization and compiled signatures.
14. Use `cache=True` appropriately.
15. Write numeric Numba functions over NumPy arrays.
16. Understand limitations caused by Python objects.
17. Identify when Numba falls back or fails to compile.
18. Use `parallel=True`.
19. Use `prange`.
20. Understand when parallel loops are actually beneficial.
21. Understand race conditions and correctness concerns in parallel code.
22. Use `@vectorize`.
23. Use `@guvectorize`.
24. Understand when custom ufuncs are useful.
25. Integrate Numba functions with pandas/Polars pipelines.
26. Pass column arrays into compiled functions instead of DataFrames.
27. Understand Numba/Polars integration patterns.
28. Understand Numba/pandas integration patterns.
29. Explain what Cython is.
30. Understand `.pyx` files.
31. Understand `cdef`.
32. Understand static typing in Cython.
33. Understand typed memoryviews.
34. Build a Cython extension.
35. Understand build backends.
36. Understand compilation toolchains.
37. Read Cython annotation reports.
38. Identify remaining Python interactions using the annotation report.
39. Understand the GIL in the context of compiled code.
40. Understand `nogil`.
41. Understand how releasing the GIL enables thread-level parallelism.
42. Connect this to Module 2.10 concurrency concepts.
43. Test optimized code against a pure-Python reference.
44. Use property-based testing concepts from Module 2.19.
45. Understand numerical correctness and edge cases.
46. Understand packaging compiled extensions.
47. Understand wheel creation.
48. Understand platform-specific build challenges.
49. Understand Docker/image implications.
50. Understand deployment costs.
51. Understand Rust/PyO3/maturin as alternatives at awareness level.
52. Understand mypyc as an alternative at awareness level.
53. Use compiled functions inside Spark pandas UDFs.
54. Use compiled functions inside Dask workloads.
55. Use compiled functions inside Ray workloads.
56. Compare pure Python, vectorized, Numba, and Cython approaches.
57. Measure compilation time separately from steady-state runtime.
58. Make a production decision based on performance gain versus maintenance/deployment cost.

Do not skip any of these concepts.

---

# PREREQUISITE BOUNDARY

This module assumes the learner has already studied:

- Python
- NumPy
- pandas
- Polars
- SQL
- basic algorithmic complexity
- profiling
- concurrency
- Spark
- Dask
- Ray
- testing
- packaging/container fundamentals

The roadmap specifically states that **basic profiling with `cProfile` and `timeit` is not re-taught**.

Do not turn this file into a beginner Python tutorial.

However, provide enough context to make the performance concepts understandable.

For example:

> "A hot loop is a small section of code that consumes a disproportionate amount of total runtime."

Then move into the advanced material.

---

# REQUIRED LEARNING PHILOSOPHY

Every major concept must follow:

```text
WHAT
↓
WHY
↓
WHEN
↓
HOW
↓
CODE
↓
INTERNAL BEHAVIOR
↓
PERFORMANCE IMPLICATION
↓
CORRECTNESS RISK
↓
PRODUCTION TRADE-OFF
```

For every optimization technique answer:

- What problem does it solve?
- What problem does it NOT solve?
- When should I use it?
- When should I avoid it?
- What does the generated execution look like conceptually?
- What does it cost to introduce?
- How do I prove it is faster?
- How do I prove it remains correct?
- How do I deploy it?

---

# REQUIRED DOCUMENT STRUCTURE

Build the document progressively. A recommended structure is:

```text
1. Module Overview
2. The Hot-Loop Problem
3. Profile Before You Compile
4. The Optimization Decision Ladder
5. Pure Python Baseline
6. Vectorized NumPy / Polars / SQL Baseline
7. When Compilation Is Justified
8. Numba Fundamentals
9. @njit and Nopython Mode
10. Supported Types and Features
11. Compilation Time vs Runtime
12. cache=True
13. Numba and NumPy Arrays
14. Numba Limitations and Failure Modes
15. Numba Parallelism
16. parallel=True
17. prange
18. Parallel Correctness and Race Conditions
19. @vectorize
20. @guvectorize
21. Numba with pandas
22. Numba with Polars
23. Cython Fundamentals
24. .pyx Files
25. cdef and Static Types
26. Typed Memoryviews
27. Building Cython Extensions
28. Cython Build Backends
29. Annotation Reports
30. GIL and nogil
31. Cython Parallelism
32. Correctness Testing
33. Property-Based Testing
34. Packaging and Deployment
35. Wheels and Platform Compatibility
36. Docker / Image Considerations
37. Rust/PyO3/maturin and mypyc Awareness
38. Compiled Functions in Spark
39. Compiled Functions in Dask
40. Compiled Functions in Ray
41. Full Sessionization Case Study
42. Benchmarking All Implementations
43. Failure Injection and Debugging
44. Production Decision Framework
45. Hands-on Exercise
46. Checkpoint
47. Interview Questions
48. Roadmap Coverage Audit
```

You may adjust the exact section names, but every roadmap requirement must be represented.

---

# SECTION 1 — MODULE OVERVIEW

Start by explaining:

## What is a hot loop?

Use a practical Data Engineering example.

For example:

```python
for event in events:
    if event.user_id != previous_user:
        ...
```

Explain why such sequential logic can be difficult to express as a simple vectorized operation.

Then explain the central idea:

```text
Python loop
   ↓
Profile
   ↓
Confirm bottleneck
   ↓
Try vectorization / query engine
   ↓
Still hot?
   ↓
Compile
   ├── Numba
   └── Cython
```

Make this the mental model for the entire document.

---

# SECTION 2 — PROFILE BEFORE YOU COMPILE

Explain why the roadmap explicitly says:

> Compile only after profiling shows a hot loop.

Explain:

```text
Bad engineering:

"This loop looks slow."
        ↓
Use Numba
```

versus:

```text
Good engineering:

Measure
  ↓
Profile
  ↓
Find bottleneck
  ↓
Confirm loop dominates runtime
  ↓
Optimize
```

Explain that a loop may not be the bottleneck because runtime may instead be dominated by:

- disk I/O
- network I/O
- database queries
- Parquet scanning
- serialization
- Python object creation
- inefficient joins
- distributed scheduling overhead

Give examples.

---

# SECTION 3 — OPTIMIZATION DECISION LADDER

Teach the module's optimization ladder:

```text
1. Do less work
2. Use a better engine
3. Use more cores
4. Use more machines
5. Compile hot loops
```

Then focus on the decision:

```text
Can NumPy vectorization solve it?
      ↓
Can Polars expression / SQL solve it?
      ↓
Can a better algorithm solve it?
      ↓
Is the Python loop still the bottleneck?
      ↓
YES
      ↓
Consider Numba / Cython
```

Explain why compiling an inefficient algorithm does not make it a good algorithm.

---

# SECTION 4 — PURE PYTHON BASELINE

Create a realistic baseline.

Use a **sessionization/state-machine** example because the roadmap explicitly requires this.

Example conceptual workload:

```text
Sorted events:

user_id | timestamp
--------|----------
A       | 10:00
A       | 10:05
A       | 10:45
A       | 11:30
B       | 09:00
B       | 09:10
```

Define a session boundary using an inactivity threshold.

Implement:

```python
def sessionize(user_ids, timestamps, gap_seconds):
    ...
```

Start with a clear pure-Python implementation.

Explain:

- algorithm
- complexity
- state
- why it is sequential
- why this makes it a candidate for compilation

Do not assume compilation is already justified.

---

# SECTION 5 — VECTORIZED BASELINE

Before Numba, attempt alternatives.

Show the learner how to ask:

> Can this be expressed using NumPy, Polars, or SQL?

Provide a vectorized approach where reasonably possible.

Also show a Polars implementation where practical.

Explain that the point is not necessarily that vectorization will always win.

The point is to establish a **strong baseline** before introducing compiled code.

Compare:

```text
Pure Python
vs
NumPy
vs
Polars
```

Measure all of them.

---

# SECTION 6 — WHEN COMPILATION IS JUSTIFIED

Explain suitable cases:

- sequential state machines
- custom sessionization
- custom scoring
- unusual parsing
- tight numerical loops
- algorithms that operate naturally over arrays

Explain unsuitable cases:

- I/O-bound code
- database queries
- large SQL joins
- Parquet scan bottlenecks
- network calls
- code dominated by Python objects
- code already fast enough
- code that Polars/SQL handles efficiently

Make this a production decision.

---

# SECTION 7 — NUMBA FUNDAMENTALS

Introduce Numba simply:

> Numba is a JIT compiler that can compile suitable Python numerical code, especially code operating on NumPy arrays.

Explain:

```text
Python source
     ↓
Numba
     ↓
specialized compiled machine code
     ↓
CPU execution
```

Contrast this with ordinary Python interpretation.

Explain:

- JIT
- compilation
- specialization
- machine code
- first-call overhead
- repeated execution

---

# SECTION 8 — `@njit`

Teach:

```python
from numba import njit

@njit
def sum_array(values):
    total = 0.0

    for value in values:
        total += value

    return total
```

Explain every line.

Then compare:

```python
pure_python(...)
```

with:

```python
numba_function(...)
```

Explain the first-call compilation behavior.

Then explain subsequent calls.

---

# SECTION 9 — NUMPY ARRAYS WITH NUMBA

This is fundamental.

Teach why this pattern works well:

```text
NumPy array
     ↓
Numba
     ↓
compiled numeric loop
```

Explain:

- contiguous memory
- numeric dtypes
- predictable types
- efficient loops
- memory access

Show examples using:

- `int32`
- `int64`
- `float32`
- `float64`

Explain dtype implications where relevant.

---

# SECTION 10 — NUMBA NOPYTHON MODE

Teach the difference between:

```text
Python-heavy execution
```

and:

```text
nopython compiled execution
```

Explain why nopython mode matters.

Show examples of code that compiles cleanly.

Then show examples involving unsupported Python constructs or objects.

Explain why:

```text
Python object
     ↓
dynamic behavior
     ↓
harder to compile efficiently
```

The learner must understand that Numba is not a universal Python compiler.

---

# SECTION 11 — SUPPORTED TYPES AND FEATURES

Teach the concept of supported types/features.

Cover relevant numeric structures such as:

- scalars
- NumPy arrays
- primitive types
- common loops
- conditionals
- arithmetic
- array indexing

Also explain that support depends on Numba/version/context.

Do not claim universal support.

When showing unsupported examples, explain how the learner can identify the problem.

---

# SECTION 12 — COMPILATION TIME VS RUN TIME

This is mandatory.

Teach:

```text
First invocation
    ↓
Compilation overhead
    ↓
Compiled function
    ↓
Repeated invocations
    ↓
Fast execution
```

Explain why benchmarking:

```python
start()
first_numba_call()
stop()
```

can produce misleading results.

Show separate measurements for:

1. first call
2. warm calls
3. total application runtime

Explain when compilation overhead matters in production.

---

# SECTION 13 — `cache=True`

Teach:

```python
@njit(cache=True)
def ...
```

Explain:

- why caching exists
- what can be reused
- why it can reduce repeated compilation overhead
- limitations
- environment/version/platform considerations

Do not imply cache eliminates all startup costs.

---

# SECTION 14 — NUMBA FAILURE MODES

Include examples where Numba does not work well.

At minimum:

### Python objects

```python
list_of_dicts
```

### Dynamic object-heavy logic

### Unsupported library calls

### Accidental object-mode behavior or compilation failure

Explain the diagnostic process.

The learner should know how to ask:

> Is this actually executing as compiled numeric code?

---

# SECTION 15 — NUMBA PARALLELISM

Introduce:

```python
@njit(parallel=True)
```

Explain what it means.

Then:

```python
from numba import prange
```

and:

```python
for i in prange(n):
    ...
```

Explain:

- parallel loop execution
- CPU cores
- independent iterations
- scheduling
- overhead
- workload size

---

# SECTION 16 — `prange`

Teach `prange` carefully.

Start with an embarrassingly parallel workload.

Example:

```python
@njit(parallel=True)
def transform(values):
    output = np.empty_like(values)

    for i in prange(values.size):
        output[i] = values[i] * values[i]

    return output
```

Explain why this is parallelizable.

Then show a stateful/ordering-dependent loop where naïve parallelization is unsafe.

Explain:

```text
Independent iterations
      ↓
Good candidate

Shared mutable state
      ↓
Potential race condition
```

---

# SECTION 17 — PARALLEL CORRECTNESS

Do not teach parallelism as "free speed."

Explain:

- race conditions
- ordering assumptions
- reductions
- shared state
- deterministic results
- floating-point differences

Give an example where naïve parallelization can produce incorrect output.

Explain how to redesign the algorithm.

---

# SECTION 18 — `@vectorize`

Teach Numba's:

```python
@vectorize
```

Explain that it can create custom ufunc-like operations.

Provide a simple example.

Explain:

```text
Scalar operation
      ↓
custom vectorized function
      ↓
array-oriented usage
```

Explain when `@vectorize` is preferable to writing a full loop.

---

# SECTION 19 — `@guvectorize`

Teach:

```python
@guvectorize
```

Explain conceptually how generalized ufunc signatures work.

Use a simple, understandable example.

Explain:

- scalar dimensions
- core dimensions
- array shapes
- broadcasting concepts where relevant

Do not turn this into an advanced NumPy broadcasting course.

The learner needs enough understanding to use `@guvectorize` appropriately.

---

# SECTION 20 — NUMBA WITH DATAFRAMES

The roadmap explicitly requires:

> Pass column arrays, not DataFrames, into compiled functions.

Make this a major principle.

Show the bad conceptual pattern:

```text
DataFrame
   ↓
Numba function
```

Then the preferred pattern:

```text
DataFrame
   ↓
Extract columns
   ↓
NumPy arrays
   ↓
Numba
   ↓
Result
   ↓
DataFrame
```

Explain why.

---

# SECTION 21 — NUMBA WITH PANDAS

Show a practical pandas integration pattern.

For example:

```python
values = df["value"].to_numpy()
result = compiled_function(values)

df["result"] = result
```

Explain:

- copying vs views where relevant
- dtype conversion
- alignment
- result assignment
- avoiding row-wise `apply`

Explicitly compare this with:

```python
df.apply(...)
```

and explain why a compiled array function is architecturally different.

---

# SECTION 22 — NUMBA WITH POLARS

Show an appropriate integration pattern.

Do not pretend Numba is automatically the right tool inside every Polars pipeline.

Explain:

```text
Polars
  ↓
columnar transformation
  ↓
unavoidable custom numerical loop
  ↓
extract array representation
  ↓
Numba
  ↓
return result
  ↓
Polars
```

Discuss the trade-offs and boundary crossings.

Explain why adding Numba can sometimes make a pipeline worse if conversion/copy overhead dominates.

---

# SECTION 23 — CYTHON FUNDAMENTALS

Introduce Cython.

Explain:

> Cython is a language/compiler approach that lets Python-like code be compiled to C/C-extension code, with optional static typing and explicit control over Python/C boundaries.

Explain:

```text
Python
  ↓
Cython source (.pyx)
  ↓
C/C++ compilation
  ↓
Python extension module
```

Contrast:

```text
Numba
JIT at runtime

Cython
compiled extension built ahead of runtime
```

Do not oversimplify the distinction.

---

# SECTION 24 — `.pyx` FILES

Show a minimal Cython file.

For example:

```cython
def add_numbers(int a, int b):
    return a + b
```

Explain:

- `.pyx`
- Python-level functions
- Cython syntax
- compilation

Then progressively introduce typed loops.

---

# SECTION 25 — `cdef`

Teach:

```cython
cdef
```

Explain static C-level declarations.

Example:

```cython
cdef double total = 0.0
cdef Py_ssize_t i
```

Explain why static typing can reduce Python interaction.

Compare:

```text
Python variable
vs
C-level typed variable
```

---

# SECTION 26 — TYPED MEMORYVIEWS

This is mandatory.

Teach:

```cython
double[:] values
```

and explain typed memoryviews.

Explain:

- contiguous/strided memory concepts
- NumPy interoperability
- avoiding unnecessary copies
- typed access
- performance implications

Show a complete Cython loop using a typed memoryview.

---

# SECTION 27 — CYTHON EXTENSION BUILD

Teach the basic build lifecycle:

```text
.pyx
 ↓
Cython compilation
 ↓
generated C/C++
 ↓
native compiler
 ↓
extension
 ↓
Python import
```

Show a minimal modern project structure.

Use an appropriate modern build backend rather than outdated `setup.py`-only teaching.

If using `pyproject.toml`, explain the important pieces.

Do not invent build configuration.

---

# SECTION 28 — CYTHON BUILD BACKENDS

Teach the concept of a build backend.

Explain:

- build requirements
- compiler
- extension build
- wheel generation
- editable development
- source distribution

The learner should understand that Cython introduces a native build toolchain.

---

# SECTION 29 — CYTHON ANNOTATION REPORT

This is mandatory.

Teach how to generate/read the annotation report.

Explain that the report helps identify where code still interacts with Python.

Conceptually:

```text
Mostly C-level code
    ↓
Good candidate

Heavy Python interaction
    ↓
Optimization opportunity / limitation
```

Explain how to use the report during optimization.

Do not simply say "green is fast."

Explain what the annotations actually tell the engineer and why Python interaction matters.

---

# SECTION 30 — GIL AND `nogil`

Teach the Python GIL in the limited context necessary for this module.

Explain:

```text
Python bytecode
    ↓
GIL constraints
```

Then:

```text
Cython compiled code
    ↓
nogil
    ↓
threads can execute compiled sections concurrently
```

Explain that:

- releasing the GIL is not automatically safe
- the code must avoid unsafe Python interactions
- shared state still requires synchronization
- CPU-bound native code can benefit from multiple threads

Connect this explicitly to Stage 2 Module 2.10.

---

# SECTION 31 — CYTHON PARALLELISM

Show a controlled example of:

```cython
with nogil:
    ...
```

If using parallel constructs, explain them carefully and only where technically justified.

Discuss:

- independent iterations
- thread safety
- memory access
- race conditions
- GIL release
- CPU scaling

Do not overstate expected speedups.

---

# SECTION 32 — NUMBA VS CYTHON

Create a detailed comparison.

At minimum:

| Dimension | Numba | Cython |
|---|---|---|
| Compilation model | | |
| Ease of adoption | | |
| Python syntax | | |
| Static typing | | |
| NumPy integration | | |
| Custom C-level control | | |
| Build complexity | | |
| Deployment complexity | | |
| Runtime compilation | | |
| Parallelism | | |
| Best use case | | |
| Main limitation | | |
| Maintenance cost | | |

Explain that neither is universally better.

Provide practical scenarios.

---

# SECTION 33 — CORRECTNESS TESTING

The roadmap explicitly requires testing compiled functions against the pure-Python reference implementation.

Make this a major section.

Use:

```text
Reference implementation
        ↓
Optimized implementation
        ↓
Same input
        ↓
Compare outputs
```

Test:

- normal inputs
- empty inputs
- single element
- multiple users
- repeated timestamps
- large gaps
- no gaps
- boundary conditions
- integer/float behavior
- NaNs where applicable
- unusual input values

Explain why optimized code must never be trusted simply because it is faster.

---

# SECTION 34 — PROPERTY-BASED TESTING

Connect this to Module 2.19.

Use Hypothesis conceptually and with code.

Example structure:

```python
@given(...)
def test_numba_matches_reference(...):
    expected = python_reference(...)
    actual = numba_version(...)

    assert ...
```

Explain:

- generated inputs
- invariants
- reference comparisons
- edge cases

Do not turn this into a complete Hypothesis course.

---

# SECTION 35 — BENCHMARKING COMPILED CODE

Although full benchmarking is covered in Topic 06, this file must teach enough benchmarking to avoid incorrect conclusions.

Compare:

```text
Pure Python
Vectorized NumPy
Polars
Numba cold
Numba warm
Cython
```

Measure separately:

- compilation time
- warm execution time
- total end-to-end runtime
- memory where relevant

Explain why first-call Numba timing can be misleading.

Explain why end-to-end pipeline benchmarks can differ from isolated function benchmarks.

---

# SECTION 36 — PACKAGING AND DEPLOYMENT COST

Teach the production reality.

Numba:

- runtime/compiler considerations
- environment compatibility
- cache considerations
- version compatibility

Cython:

- C compiler
- build toolchain
- native dependencies
- wheels
- platform differences

Explain:

```text
Performance gain
      vs
Operational complexity
```

A 20% speedup may not justify a significant deployment burden.

A 10× improvement to a critical hot path may justify it.

Make this a business/engineering decision.

---

# SECTION 37 — WHEELS AND PLATFORM COMPATIBILITY

Teach why native extensions create distribution complexity.

Explain:

```text
Linux
Windows
macOS
x86_64
ARM64
Python versions
```

Discuss wheels conceptually.

Explain:

- prebuilt wheels
- source builds
- compiler availability
- CI build matrices
- platform compatibility

Do not turn this into a complete Python packaging module.

---

# SECTION 38 — DOCKER / CONTAINER CONSIDERATIONS

Explain how compiled extensions affect container images.

Discuss:

- build stage
- compiler dependencies
- runtime image
- multi-stage builds
- wheel installation
- reproducibility

Show a conceptual Docker architecture:

```text
Build image
 ├── Python
 ├── Cython
 ├── compiler
 └── build dependencies
        ↓
      wheel
        ↓
Runtime image
 ├── Python
 └── wheel
```

Explain why this can reduce runtime image size.

---

# SECTION 39 — ALTERNATIVES

The roadmap requires awareness of:

- Rust extensions using PyO3
- maturin
- Polars plugins
- mypyc

Do not teach these deeply.

For each explain:

```text
What it is
Why it exists
When it may be considered
How it compares conceptually with Numba/Cython
```

Make clear these are awareness-level alternatives.

---

# SECTION 40 — COMPILED FUNCTIONS IN DISTRIBUTED ENGINES

The roadmap explicitly requires using compiled functions inside:

- pandas UDFs
- Dask
- Ray

Teach each at an architectural level.

## Spark

Explain:

```text
Spark
 ↓
pandas UDF
 ↓
Numba/Cython optimized function
 ↓
batch processing
```

Discuss:

- serialization
- worker startup
- compilation overhead
- worker reuse
- package distribution
- whether the compiled function actually dominates runtime

## Dask

Explain:

```text
Dask partition
 ↓
NumPy arrays
 ↓
Numba/Cython
 ↓
result
```

Discuss task overhead and partition size.

## Ray

Explain:

```text
Ray Data batch
 ↓
compiled function
 ↓
result
```

Discuss worker initialization and deployment.

Do not claim that adding Numba/Cython automatically improves distributed workloads.

---

# SECTION 41 — FULL SESSIONIZATION CASE STUDY

This must be the central hands-on case study.

Use:

```text
workloads/hot_loops/
```

as the conceptual project path.

Do not create the directory.

The project should process a large set of sorted events and assign session IDs.

Build four implementations:

```text
1. Pure Python
2. NumPy / Polars where reasonably possible
3. Numba
4. Cython
```

Then compare them.

The learner must understand:

```text
Algorithm
 ↓
Reference
 ↓
Alternative vectorized implementation
 ↓
Numba
 ↓
Cython
 ↓
Benchmark
 ↓
Correctness test
 ↓
Production decision
```

---

# REQUIRED HANDS-ON EXERCISE

The roadmap explicitly requires:

1. Implement per-user sessionization over **50 million sorted events** in pure Python.
2. Profile it.
3. Rewrite it with Numba using `@njit`.
4. Add `parallel=True` across users where the algorithm permits.
5. Rewrite it with Cython using typed memoryviews.
6. Compare runtime including compilation time.
7. Prove equality with the Python reference using Hypothesis.
8. Use the Numba function inside a Polars pipeline.
9. Use it inside a Spark pandas UDF or Dask map.
10. Measure end-to-end gains.
11. Write a decision record:
    - which implementation to ship
    - why
    - performance evidence
    - maintenance cost
    - deployment cost
    - correctness evidence

Important:

Do not generate fake benchmark numbers for 50 million events.

Instead provide:

- benchmark methodology
- data-generation strategy
- commands/code
- expected observations
- result-recording table

The learner must run the benchmark and fill in actual measurements.

---

# REQUIRED BENCHMARK TABLE

Include a template:

| Implementation | Compile Time | Warm Runtime | End-to-End Runtime | Peak Memory | Correct? | Complexity |
|---|---:|---:|---:|---:|---|---|
| Pure Python | | | | | | |
| NumPy/Polars | | | | | | |
| Numba `@njit` | | | | | | |
| Numba parallel | | | | | | |
| Cython | | | | | | |

Explain that results must be measured on the learner's actual environment.

---

# REQUIRED FAILURE INJECTION

Include realistic failures.

At minimum:

## Failure 1 — Compile before profiling

Explain why this is bad engineering.

## Failure 2 — Python objects inside Numba

Show why object-heavy code limits compilation.

## Failure 3 — First-call benchmark

Show why including compilation time can mislead.

## Failure 4 — Unsafe `prange`

Demonstrate or explain a race condition.

## Failure 5 — Numba boundary-copy overhead

Show how conversion/copying can erase gains.

## Failure 6 — Cython Python interactions

Use the annotation report to identify remaining Python work.

## Failure 7 — Native build failure

Explain missing compiler/build dependency issues.

## Failure 8 — Wrong platform wheel

Explain deployment incompatibility.

## Failure 9 — Compiled function faster but pipeline unchanged

Explain why function-level speedup does not necessarily produce end-to-end improvement.

For every failure use:

```text
Symptom
↓
Root cause
↓
Diagnosis
↓
Fix
↓
Prevention
```

---

# REQUIRED PRODUCTION DECISION FRAMEWORK

Create a decision tree:

```text
Is the workload I/O-bound?
    ↓
YES → Do not compile the loop first.

NO
 ↓
Is the bottleneck a database / SQL / scan / join?
    ↓
YES → Fix the data engine/query plan first.

NO
 ↓
Can NumPy / Polars / SQL express the operation efficiently?
    ↓
YES → Prefer vectorized/engine implementation.

NO
 ↓
Is a tight numeric loop still the bottleneck?
    ↓
YES
 ↓
Need rapid Python-native optimization?
    ↓
Consider Numba.

Need deep control, static typing, native extension,
or reusable compiled module?
    ↓
Consider Cython.

Need another native-language ecosystem?
    ↓
Consider Rust/PyO3/maturin.
```

Explain that this is a heuristic.

---

# REQUIRED ENGINEERING TRADE-OFF TABLE

Include:

| Option | Performance Potential | Development Effort | Deployment Complexity | Maintenance | Best Fit |
|---|---|---|---|---|---|
| Pure Python | | | | | |
| NumPy | | | | | |
| Polars | | | | | |
| Numba | | | | | |
| Cython | | | | | |
| Rust/PyO3 | | | | | |

Do not assign arbitrary numerical scores.

Explain qualitatively.

---

# CODE QUALITY REQUIREMENTS

All examples must:

- Use modern Python.
- Be clear.
- Be incremental.
- Be runnable where practical.
- Separate benchmark code from production logic.
- Include comments explaining non-obvious performance decisions.
- Avoid artificial micro-optimizations without explanation.
- Prefer NumPy arrays over Python objects for Numba examples.
- Demonstrate correctness before performance claims.

Do not produce code merely to make the file longer.

Every code example must teach an engineering concept.

---

# VERSION AND API ACCURACY

Numba and Cython evolve.

Before using APIs:

- Prefer current stable APIs.
- Avoid deprecated approaches.
- Do not invent signatures.
- Clearly identify version-sensitive behavior.
- If exact behavior depends on installed versions/platform/compiler, say so.
- Do not present uncertain native build configuration as guaranteed.

Especially verify concepts around:

- `@njit`
- `parallel=True`
- `prange`
- `@vectorize`
- `@guvectorize`
- Cython build configuration
- annotation reports
- `nogil`

---

# REQUIRED DIAGRAMS

Use Markdown/ASCII diagrams where useful.

At minimum include:

1. Python loop → profiler → compiler decision.
2. Optimization ladder.
3. Numba JIT flow.
4. First call vs warm calls.
5. Numba array execution.
6. `prange` parallel execution.
7. Cython compilation pipeline.
8. Typed memoryview architecture.
9. GIL vs `nogil`.
10. Distributed-engine integration.
11. Production decision tree.

Do not use diagrams as decoration.

---

# PRACTICAL CHECKPOINTS

After major sections include concise checkpoints.

Examples:

```text
Checkpoint:
- Can you explain why profiling comes before compilation?
- Can you explain why NumPy arrays are a good input for Numba?
- Can you explain the difference between @njit and @vectorize?
```

Later:

```text
Checkpoint:
- Can you explain typed memoryviews?
- Can you explain why Cython introduces build complexity?
- Can you explain when nogil is useful?
```

---

# FINAL CHECKPOINT

The learner must be able to explain, without notes:

## Performance reasoning

- What is a hot loop?
- Why profile before optimizing?
- Why try vectorization first?
- When is compilation justified?

## Numba

- What does `@njit` do?
- What is nopython mode?
- Why are NumPy arrays important?
- What happens during the first call?
- What does `cache=True` do?
- What does `parallel=True` do?
- What does `prange` do?
- What are Numba's limitations?
- What are `@vectorize` and `@guvectorize`?

## Cython

- What is Cython?
- What is a `.pyx` file?
- What does `cdef` do?
- What is a typed memoryview?
- How is a Cython extension built?
- What does the annotation report show?
- What does `nogil` mean?

## Correctness

- How do you compare optimized code against a reference?
- Why is property-based testing useful?
- What can go wrong with parallel code?

## Production

- How do compiled extensions affect packaging?
- Why do wheels matter?
- What changes in Docker?
- When is Numba better than Cython?
- When is Cython better?
- When should you use Rust instead?
- How can compiled functions be used inside Spark, Dask, and Ray?

---

# INTERVIEW PREPARATION

Include interview questions at three levels.

## Beginner

- What is a hot loop?
- Why can Python loops be slow?
- What is Numba?
- What is Cython?
- What does `@njit` mean?
- What is JIT compilation?

## Intermediate

- Why should you profile before using Numba?
- Why do NumPy arrays work well with Numba?
- What is nopython mode?
- What is the difference between `parallel=True` and `prange`?
- What is a typed memoryview?
- Why does Cython use `cdef`?
- Why does Cython introduce deployment complexity?

## Advanced

- When would you choose Numba over Cython?
- How would you optimize a sessionization loop?
- How would you benchmark cold versus warm Numba execution?
- How would you safely parallelize a stateful algorithm?
- How would you validate compiled code?
- How would you deploy Cython wheels across Linux and ARM64?
- How would you use Numba inside a Spark pandas UDF?
- When would Numba make a Dask/Ray pipeline slower?
- How would you decide between Numba, Cython, and Rust?

Provide technically correct answers after the questions.

---

# COMMON MISTAKES

Include and explain the roadmap's mistakes:

### Mistake 1
Compiling before vectorizing.

### Mistake 2
Passing Python objects into Numba.

### Mistake 3
Measuring the first Numba call as steady-state performance.

### Mistake 4
Shipping native code without tests.

Also include additional production mistakes:

- optimizing the wrong bottleneck
- ignoring compilation overhead
- ignoring memory bandwidth
- using parallelism on tiny workloads
- introducing race conditions
- measuring isolated function performance but ignoring pipeline performance
- ignoring deployment complexity
- assuming benchmark results transfer unchanged between machines

For every mistake explain the engineering lesson.

---

# PRODUCTION PRINCIPLES

End the technical teaching with principles:

1. **Profile first.**
2. **Fix the algorithm before compiling it.**
3. **Try vectorization and better engines first.**
4. **Compile only proven hot paths.**
5. **Prefer simple implementations when performance is already sufficient.**
6. **Separate compile time from steady-state runtime.**
7. **Measure end-to-end performance.**
8. **Test optimized code against a reference implementation.**
9. **Treat native code as an operational dependency.**
10. **Account for packaging and deployment costs.**
11. **Do not parallelize unsafe algorithms.**
12. **Do not assume more cores means linear speedup.**
13. **Do not ship an optimization without reproducible evidence.**

---

# ROADMAP COVERAGE CHECKLIST

Before completing the file, verify every requirement:

```text
[ ] When to compile after profiling
[ ] Vectorized NumPy first
[ ] Polars expressions first
[ ] SQL alternative
[ ] Numba @njit
[ ] Numba nopython mode
[ ] Supported types/features
[ ] Compile time vs runtime
[ ] cache=True
[ ] parallel=True
[ ] prange
[ ] Parallel correctness
[ ] @vectorize
[ ] @guvectorize
[ ] Numba with DataFrames
[ ] Column arrays instead of DataFrames
[ ] pandas integration
[ ] Polars integration
[ ] Cython
[ ] .pyx files
[ ] cdef
[ ] Static types
[ ] Typed memoryviews
[ ] Build backend
[ ] Compiling extensions
[ ] Annotation report
[ ] GIL
[ ] nogil
[ ] Thread parallelism
[ ] Reference implementation
[ ] Property-based testing
[ ] Packaging costs
[ ] Wheels
[ ] Platform compatibility
[ ] Container/image implications
[ ] Rust/PyO3/maturin awareness
[ ] Polars plugins awareness
[ ] mypyc awareness
[ ] Spark pandas UDF integration
[ ] Dask integration
[ ] Ray integration
[ ] Sessionization/state-machine case study
[ ] 50-million-event exercise
[ ] Numba comparison
[ ] Cython comparison
[ ] Hypothesis correctness validation
[ ] Polars integration exercise
[ ] Spark/Dask integration exercise
[ ] Decision record
[ ] Performance comparison
[ ] Failure injection
[ ] Production decision framework
```

---

# FINAL ROADMAP COVERAGE AUDIT

At the end of the file, create:

```markdown
## Roadmap Coverage Audit

| Roadmap Concept | Covered? | Section |
|---|---|---|
| Compile after profiling | Yes | ... |
| Numba `@njit` | Yes | ... |
| Nopython mode | Yes | ... |
| Supported types/features | Yes | ... |
| Compile vs runtime | Yes | ... |
| `cache=True` | Yes | ... |
| `parallel=True` | Yes | ... |
| `prange` | Yes | ... |
| `@vectorize` | Yes | ... |
| `@guvectorize` | Yes | ... |
| DataFrame integration | Yes | ... |
| Cython `.pyx` | Yes | ... |
| `cdef` | Yes | ... |
| Typed memoryviews | Yes | ... |
| Build backend | Yes | ... |
| Annotation report | Yes | ... |
| `nogil` | Yes | ... |
| Correctness testing | Yes | ... |
| Property-based testing | Yes | ... |
| Packaging/deployment | Yes | ... |
| Wheels/platforms | Yes | ... |
| Rust/PyO3/maturin | Yes | ... |
| mypyc | Yes | ... |
| Spark integration | Yes | ... |
| Dask integration | Yes | ... |
| Ray integration | Yes | ... |
| Sessionization exercise | Yes | ... |
| Benchmark comparison | Yes | ... |
| Production decision | Yes | ... |
```

Every item must be marked **Yes** before the file is considered complete.

---

# QUALITY STANDARD

The completed file must feel like a **serious advanced Data Engineering performance module**, not a generic Numba/Cython tutorial.

It must teach the learner to think like a performance engineer:

```text
Business / SLA requirement
        ↓
Measure
        ↓
Profile
        ↓
Identify bottleneck
        ↓
Improve algorithm
        ↓
Try vectorization / better engine
        ↓
Still hot?
        ↓
Compile
        ├── Numba
        └── Cython
        ↓
Test correctness
        ↓
Benchmark
        ↓
Measure end-to-end impact
        ↓
Evaluate deployment cost
        ↓
Make production decision
```

The learner should finish the module understanding not only **how to make a Python loop faster**, but **when making it faster is actually the correct engineering decision**.

---

# FINAL EXECUTION INSTRUCTION

Now inspect the existing:

```text
21-Performance-Scaling-and-Cost-Optimization/05-numba-and-cython-for-hot-loops.md
```

and then rewrite/update **ONLY that file** according to this prompt.

Preserve useful existing content if it is correct, but improve anything that does not satisfy the roadmap and quality requirements above.

Do not modify any other file.

Do not create additional files.

Do not stop at an outline.

Produce the **complete, detailed Markdown learning module** in:

```text
05-numba-and-cython-for-hot-loops.md
```

The final document must be:

- beginner-friendly in explanation
- advanced in technical depth
- production-oriented
- performance-measurement driven
- code-heavy where appropriate
- correctness-focused
- roadmap-complete
- explicit about trade-offs
- explicit about deployment costs
- suitable for a Data Engineer progressing toward senior/production-level expertise.