# Practice Questions — Profiling, Memory and Runtime Performance

**Stage:** 1 — Programming & Computational Thinking  
**Module:** 17 — Profiling, Memory and Runtime Performance  
**Target runtime:** Python 3.12+; version-specific behavior must be checked against the interpreter and tool actually used.  
**Project context:** the shared `slowlog` log/CSV analysis ETL workload.

This assessment follows `roadmap-Profiling-Memory-and-Runtime-Performance.md` and the project location shown in `Roadmap_ptree.md`:

`Stage 1 — Programming & Computational Thinking/17-Profiling-Memory-and-Runtime-Performance/`

The nine lesson files are:

1. `01-cprofile-pstats-and-flame-graphs.md`
2. `02-sampling-profilers-with-py-spy.md`
3. `03-timeit-and-microbenchmark-pitfalls.md`
4. `04-tracemalloc-and-memory-leak-hunting.md`
5. `05-memray-and-allocation-analysis.md`
6. `06-garbage-collector-tuning-and-reference-cycles.md`
7. `07-cpython-performance-idioms.md`
8. `08-ctypes-and-cffi-for-native-code.md`
9. `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`

## How to use this assessment

- Attempt the questions before consulting the answer key.
- Each question has a unique ID, a lesson mapping, a difficulty level, and a concrete task.
- Unless a question explicitly asks for a prediction, do not invent timing or memory numbers. Report measurements from your own environment with the Python version, OS, hardware, input size, commands, and repetition strategy. Separate correctness equivalence from performance equivalence: a non-significant difference or overlapping uncertainty intervals do not prove implementations are equivalent. For performance equivalence, define a practically meaningful margin in advance and use an appropriate equivalence/non-inferiority analysis; otherwise report the estimate and uncertainty without claiming equivalence.
- For command-output questions, treat the supplied output as illustrative evidence for the stated scenario, not as a universal result.
- A defensible alternative answer earns credit when it identifies assumptions, competing explanations, and evidence that would distinguish them.
- Practical commands assume the relevant tools are installed and permitted to inspect the target process. `py-spy` attachment may require OS-specific permissions. Native profilers and memory tools have platform and build limitations.

## Assessment map

| Phase | IDs | Count | Main focus |
|---|---|---:|---|
| A — Where Does the Time Go? | A01–A12 | 12 | Profiling, sampling, CPU/wait diagnosis, benchmark design |
| B — Where Does the Memory Go? | B01–B11 | 11 | Allocation tracing, RSS, Memray, retention, GC |
| C — Making It Faster | C01–C12 | 12 | CPython idioms, FFI, native extensions, packaging decisions |
| **Total** | **A01–C12** | **35** | |

Required special formats are included: **six benchmark-defect questions** (A07–A12) and **six “What would you measure first?” incident scenarios** (A05, A06, B08, B09, C10, C11).

---

# Phase A — Where Does the Time Go?

## A01 — Read `pstats` without confusing cumulative and self time

- **Lesson:** `01-cprofile-pstats-and-flame-graphs.md`
- **Difficulty:** Beginner
- **Format:** Tool-output interpretation

A `cProfile` report contains the following illustrative rows:

```text
ncalls  tottime  percall  cumtime  percall  filename:lineno(function)
1       0.120    0.120    2.400    2.400    slowlog.py:80(run)
10000   0.700    0.00007  1.900    0.00019  slowlog.py:42(parse_line)
1       0.450    0.450    0.600    0.600    slowlog.py:61(load_csv)
50000   0.350    0.000007 0.350    0.000007 slowlog.py:27(normalize)
```

1. Define `ncalls`, `tottime`, `cumtime`, and the two meanings of `percall`.
2. Which function would you investigate first, and what additional evidence would you collect?
3. Explain why adding every row's `cumtime` does not yield total program runtime.

**Expected response:** short definitions plus a ranked investigation hypothesis. Do not claim that the row with the largest `cumtime` necessarily contains the most self-contained work.

## A02 — Capture and compare a profile

- **Lesson:** `01-cprofile-pstats-and-flame-graphs.md`
- **Difficulty:** Beginner
- **Format:** Runnable command-line exercise

Assume `slowlog.py` has a `main()` entry point and accepts `--input sample.csv`.

1. Write a command that runs it under `cProfile` and saves a profile to `slowlog.prof`.
2. Write a Python one-liner or short script using `pstats.Stats` to sort by cumulative time and print the top 15 entries.
3. Explain what you would compare before and after a change to `parse_line`.
4. Name one reason a profiled run may take longer than an unprofiled run.

**Expected response:** executable commands and a concise interpretation plan. The task is not to supply made-up profile results.

## A03 — Interpret a flame graph

- **Lesson:** `01-cprofile-pstats-and-flame-graphs.md`
- **Difficulty:** Intermediate
- **Format:** Visual-analysis reasoning

A flame graph generated from a representative workload has a wide stack rooted at `run_etl`, with most of its width under `parse_line → normalize → regex_match`. A second wide stack is rooted at `read_csv → file_read`. The graph is an ordinary on-CPU sampling flame graph; horizontal width represents sampled stack frequency, and vertical position represents stack depth.

1. What does a wide frame suggest, and what does it not prove?
2. How would you distinguish CPU spent in regex processing from time waiting for file I/O?
3. If `normalize` appears wide in many caller stacks, what does that tell you about where it is used?
4. Name a follow-up measurement that could falsify your leading hypothesis.

**Expected response:** four numbered answers. State the profiler's sampling mode and limitations.

## A04 — Sampling profiler and stack-dump interpretation

- **Lesson:** `02-sampling-profilers-with-py-spy.md`
- **Difficulty:** Intermediate
- **Format:** Command/tool interpretation

A long-running process is slow in production, but attaching a deterministic profiler would be intrusive. The operator can install `py-spy` and has permission to inspect the process.

1. Give a `py-spy` command to obtain a stack dump for PID `4242`.
2. Give a command to record a sampling profile for that PID and save it as an SVG flame graph.
3. Explain why a sampled stack dump is not a complete trace of every function call.
4. Identify two reasons the tool might fail to attach even if the PID exists.

**Expected response:** commands, sampling explanation, and platform/permission caveats.

## A05 — What would you measure first? Production incident: CPU high, throughput low

- **Lesson:** `02-sampling-profilers-with-py-spy.md`
- **Difficulty:** Advanced
- **Format:** **Measurement-first incident scenario 1 of 6**

A `slowlog` worker's CPU utilization is near 100% on one core. Throughput has fallen by 40% after a deployment. Memory is stable, and the input volume is comparable to yesterday. No stack profile has yet been captured.

1. What would you measure first, and why?
2. Which tool would you choose for a low-overhead first look and which for a controlled reproduction?
3. Give at least three competing explanations.
4. State what evidence would cause you to investigate an algorithmic issue, regex/parsing, lock contention, or a deployment/environment change next.

**Expected response:** a short incident plan ordered by information value. Do not begin by changing code or assuming the newest deployment contains a particular bug.

## A06 — What would you measure first? Production incident: job “stalled”

- **Lesson:** `02-sampling-profilers-with-py-spy.md`
- **Difficulty:** Advanced
- **Format:** **Measurement-first incident scenario 2 of 6**

A nightly ETL job has made no visible progress for 12 minutes. CPU utilization is below 3%; memory is stable; the process is still alive. The last log message says “loading input partition 7.” There is no confirmed deadlock.

1. What is the first useful measurement or observation?
2. How would you use `py-spy` or OS-level observations to distinguish blocked I/O, a lock wait, a sleep/retry loop, and a Python loop that is not actually making progress?
3. What evidence would justify escalating to a thread dump, system-call tracing, or application-level instrumentation?
4. Explain why a low-CPU stack sample must not automatically be interpreted as proof of a deadlock.

**Expected response:** ordered diagnostic steps and competing hypotheses.

## A07 — What is wrong with this benchmark? One run, one conclusion

- **Lesson:** `03-timeit-and-microbenchmark-pitfalls.md`
- **Difficulty:** Intermediate
- **Format:** **Benchmark-defect question 1 of 6**

```python
import time

start = time.perf_counter()
parse_one_huge_file("events.csv")
print(time.perf_counter() - start)
```

The author runs this once after boot and concludes that a new parser is “2× faster” because its single measured run was half as long as yesterday's run.

1. Identify at least four methodological defects or uncontrolled variables.
2. Redesign the experiment, including repetitions, input, correctness, and environmental controls.
3. Explain whether cold-cache and warm-cache runs should be mixed or reported separately.

**Expected response:** defect list and a reproducible protocol. Do not assume disk cache state without measuring or controlling it.

## A08 — What is wrong with this benchmark? Timing setup and work together

- **Lesson:** `03-timeit-and-microbenchmark-pitfalls.md`
- **Difficulty:** Intermediate
- **Format:** **Benchmark-defect question 2 of 6**

```python
import timeit

print(timeit.timeit(
    "sum(x * x for x in make_values(100_000))",
    setup="from slowlog import make_values",
    number=1,
))
```

The proposed replacement precomputes the input outside the timed region. The author compares the two numbers and declares the replacement faster.

1. Identify the comparison mismatch.
2. Design one kernel-focused benchmark and one end-to-end benchmark.
3. State what must be held constant and what should be included in the timed region for each benchmark.

**Expected response:** two explicit benchmark definitions and an explanation of what each answers.

## A09 — What is wrong with this benchmark? Different data and semantics

- **Lesson:** `03-timeit-and-microbenchmark-pitfalls.md`
- **Difficulty:** Intermediate
- **Format:** **Benchmark-defect question 3 of 6**

The old implementation parses all rows, validates malformed timestamps, and returns a count plus error details. The new implementation parses only valid rows and returns a count. The author times both on different CSV files and compares seconds per run.

1. Identify the correctness and workload confounders.
2. Define a fair comparison contract and test strategy.
3. Explain how to report performance if the implementations intentionally have different error-handling semantics.

**Expected response:** contract, validation strategy, and reporting rules.

## A10 — What is wrong with this benchmark? JIT warm-up and compilation

- **Lesson:** `03-timeit-and-microbenchmark-pitfalls.md`
- **Difficulty:** Intermediate
- **Format:** **Benchmark-defect question 4 of 6**

A Numba implementation is timed once, including its first compilation, while the Python version is run seven times and the median is reported. The Numba version is declared slower.

1. Identify the asymmetry.
2. Design separate cold-start and steady-state comparisons.
3. Explain which comparison matters for a short-lived command-line job versus a long-running worker.
4. List at least two other controls needed before drawing a conclusion.

**Expected response:** benchmark plan and context-dependent interpretation.

## A11 — What is wrong with this benchmark? Timer inside the loop

- **Lesson:** `03-timeit-and-microbenchmark-pitfalls.md`
- **Difficulty:** Intermediate
- **Format:** **Benchmark-defect question 5 of 6**

```python
samples = []
for row in rows:
    start = time.perf_counter()
    normalize(row)
    samples.append(time.perf_counter() - start)
```

The author sums the samples and uses that total as the sole performance metric for a proposed whole-file optimization.

1. Identify the measurement overhead and representativeness problems.
2. Propose a batch-level timing method and a way to inspect latency distribution if per-record latency matters.
3. Explain why the benchmark should include realistic data size and repeated trials.

**Expected response:** corrected measurement approach and trade-offs.

## A12 — What is wrong with this benchmark? Profiler used as the stopwatch

- **Lesson:** `03-timeit-and-microbenchmark-pitfalls.md`
- **Difficulty:** Advanced
- **Format:** **Benchmark-defect question 6 of 6**

A developer compares `cProfile`-reported cumulative time for the old implementation with wall-clock time from an unprofiled new implementation. The new implementation appears 35% faster.

1. Explain why these quantities are not directly comparable.
2. Design a two-stage evaluation using profiling to locate work and an unprofiled benchmark to quantify the change.
3. Specify the evidence that should be preserved for a credible performance report.

**Expected response:** a measurement protocol with profile and benchmark roles clearly separated.

---

# Phase B — Where Does the Memory Go?

## B01 — Read a `tracemalloc` snapshot difference

- **Lesson:** `04-tracemalloc-and-memory-leak-hunting.md`
- **Difficulty:** Beginner
- **Format:** Tool-output interpretation

A program takes snapshot A before processing 100,000 records and snapshot B after processing them. The top positive differences are:

```text
+18.0 MiB  slowlog.py:110  cached_records[key] = record
+7.5 MiB   slowlog.py:74   decoded = line.decode("utf-8")
+0.2 MiB   pathlib.py:...  path handling
```

1. What does a positive snapshot difference mean, and what does it not prove?
2. Which line would you inspect first for long-lived retention, and what code/data would you examine?
3. How would you distinguish expected temporary allocations from a leak-like retention problem?
4. Explain why snapshots need comparable workload phases.

**Expected response:** interpretation plus a retention investigation plan.

## B02 — Python allocation tracing versus RSS

- **Lesson:** `04-tracemalloc-and-memory-leak-hunting.md`
- **Difficulty:** Intermediate
- **Format:** Conceptual comparison

After a batch completes, `tracemalloc` reports that traced current memory is nearly back to baseline, but process RSS remains 600 MiB above its initial value.

1. Give at least four plausible explanations.
2. Describe what `tracemalloc` tracks and what RSS measures.
3. Choose the next measurement or experiment to separate retained Python objects, native allocations, allocator arenas, and memory mapped by the process.
4. Explain why “RSS did not fall” alone does not prove a memory leak.

**Expected response:** comparison and evidence-driven next steps.

## B03 — Diagnose retention, not merely allocation

- **Lesson:** `04-tracemalloc-and-memory-leak-hunting.md`
- **Difficulty:** Advanced
- **Format:** Code-reading/debugging

```python
recent_results = []

def process_batch(rows):
    result = [parse(row) for row in rows]
    recent_results.append(result)
    return len(result)
```

The worker processes one batch every minute. RSS grows steadily for hours.

1. Explain the likely retention path.
2. Rewrite the code to retain only the information required by a hypothetical “last 10 batch counts” dashboard.
3. Give a test or experiment that demonstrates whether the old batches remain reachable.
4. State what evidence would make you suspect another cause instead.

**Expected response:** corrected code and a retention verification plan. Assume the dashboard needs only integer counts.

## B04 — Memray: peak, total allocation, and retained memory

- **Lesson:** `05-memray-and-allocation-analysis.md`
- **Difficulty:** Intermediate
- **Format:** Tool selection and interpretation

A `slowlog` run allocates 4 GiB cumulatively, peaks at 900 MiB of process memory, and ends with 220 MiB more RSS than it started with.

1. Explain why these three numbers are not contradictory.
2. Which question is best answered by an allocation flame graph? Which requires a peak-memory view? Which needs retention/lifetime investigation?
3. Give a Memray command to record a script and a command to generate a report from its capture, assuming Memray is installed and the command syntax for the installed version supports these options.
4. What additional evidence is needed before labeling the growth a leak?

**Expected response:** distinguish the metrics and state the limitations of each tool.

## B05 — Reference counting, cycles, and weak references

- **Lesson:** `06-garbage-collector-tuning-and-reference-cycles.md`
- **Difficulty:** Beginner
- **Format:** Code reasoning

```python
import gc
import weakref

class Node:
    pass

left = Node()
right = Node()
left.other = right
right.other = left
ref = weakref.ref(left)

del left, right
print(ref() is None)
gc.collect()
print(ref() is None)
```

1. Predict the two printed values on a typical CPython run with cyclic GC enabled.
2. Explain why reference counting alone cannot reclaim this pair.
3. Explain what the weak reference does and does not do.
4. Name one way finalizers can complicate lifecycle reasoning.

**Expected response:** output plus object-lifetime explanation. Distinguish implementation details from Python-language guarantees where relevant.

## B06 — Should we tune the garbage collector?

- **Lesson:** `06-garbage-collector-tuning-and-reference-cycles.md`
- **Difficulty:** Intermediate
- **Format:** Engineering decision

A batch job creates many short-lived dictionaries but shows no evidence of uncollectable cycles. CPU profiling shows most time in JSON parsing and normalization. Someone proposes globally disabling GC “to improve performance.”

1. What measurements should be collected before considering GC tuning?
2. Why is disabling cyclic GC unlikely to help if the hot path is JSON parsing?
3. Under what constrained conditions might temporarily disabling cyclic GC be reasonable?
4. State the safety checks and rollback conditions for an experiment.

**Expected response:** a justified decision, not a blanket rule to always enable or disable GC.

## B07 — `gc` investigation exercise

- **Lesson:** `06-garbage-collector-tuning-and-reference-cycles.md`
- **Difficulty:** Advanced
- **Format:** Practical code

Write a small Python program that:
1. Creates two objects referencing each other.
2. Holds a weak reference to one object.
3. Deletes the strong local references.
4. Shows that the object can remain alive before collection and becomes unreachable after `gc.collect()` on CPython.
5. Prints the number returned by `gc.collect()` without assuming an exact cross-version count.

Explain why the exact number collected is not a stable acceptance criterion and why the weak reference must support weak references.

**Expected response:** runnable code and a short explanation. Do not use `id()` reuse as proof of object lifetime.

## B08 — What would you measure first? Production incident: RSS grows per batch

- **Lesson:** `04-tracemalloc-and-memory-leak-hunting.md`
- **Difficulty:** Advanced
- **Format:** **Measurement-first incident scenario 3 of 6**

A long-lived ETL process starts at 350 MiB RSS and rises by roughly 25 MiB per batch for 20 batches. The input batch sizes are stable. The process has not restarted; no out-of-memory event has occurred.

1. What would you measure first, and at what points in the batch lifecycle?
2. Choose between `tracemalloc`, Memray, object-graph tools, and OS-level RSS monitoring for the first pass. Justify the choice.
3. Give at least four competing explanations, including one that is not a Python-object leak.
4. State what evidence would determine the next tool or experiment.

**Expected response:** staged memory investigation with lifecycle checkpoints.

## B09 — What would you measure first? Production incident: memory spike during join

- **Lesson:** `05-memray-and-allocation-analysis.md`
- **Difficulty:** Advanced
- **Format:** **Measurement-first incident scenario 4 of 6**

A CSV-to-analytics job has acceptable steady-state RSS but is killed by a container memory limit during a join. The job's output is correct on smaller datasets.

1. What would you measure first to identify the peak phase and allocation sources?
2. Explain how peak memory differs from total allocation volume and end-of-run RSS.
3. Give at least three possible structural remedies and the evidence that would justify each.
4. Explain why merely calling `gc.collect()` at the end cannot prevent a peak that occurs before the join finishes.

**Expected response:** peak-focused investigation and candidate remedies.

## B10 — Avoidable copies and streaming

- **Lesson:** `04-tracemalloc-and-memory-leak-hunting.md`
- **Difficulty:** Intermediate
- **Format:** Code redesign

```python
def load_and_filter(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    parsed = [parse(line) for line in lines]
    return [record for record in parsed if record["valid"]]
```

1. Identify the major materializations and their likely peak-memory consequences.
2. Sketch a streaming alternative that reads and processes one line at a time.
3. State when streaming could change semantics or fail to reduce peak memory.
4. Propose a correctness test and a memory comparison that do not depend on a fixed RSS number.

**Expected response:** code or pseudocode plus test and measurement design.

## B11 — Choose a memory tool for a specific question

- **Lesson:** `05-memray-and-allocation-analysis.md`
- **Difficulty:** Intermediate
- **Format:** Tool selection

For each goal, choose a suitable first tool and explain the limitation:
1. Find Python source lines associated with net allocation growth.
2. Attribute native and Python allocation activity, including a suspected native extension.
3. Identify the high-water mark of a process during a transformation.
4. Determine which object graph is keeping a large cache reachable.
5. Confirm whether process RSS is increasing in production over several hours.

**Expected response:** a five-row table. More than one tool may be appropriate if the answer explains what question each tool answers.

---

# Phase C — Making It Faster

## C01 — CPython optimization: choose the right first move

- **Lesson:** `07-cpython-performance-idioms.md`
- **Difficulty:** Intermediate
- **Format:** Code review

```python
def find_duplicates(rows):
    duplicates = []
    for row in rows:
        if rows.count(row) > 1:
            duplicates.append(row)
    return duplicates
```

1. Identify the dominant algorithmic problem.
2. Explain why replacing `rows.count` with a local-variable alias alone is insufficient.
3. Propose a solution that preserves the original order and duplicate occurrences, and state its time/space trade-off.
4. Define the correctness cases you would test.

**Expected response:** runnable implementation or precise pseudocode plus complexity and tests.

## C02 — Performance folklore and measurement

- **Lesson:** `07-cpython-performance-idioms.md`
- **Difficulty:** Intermediate
- **Format:** Claim evaluation

Evaluate these claims for a modern CPython release:

A. “A list comprehension is always faster than every alternative.”  
B. “Using `__slots__` makes every program faster.”  
C. “Calling a built-in implemented in C can reduce Python-level loop overhead.”  
D. “Local-variable aliasing is always worth doing in production code.”  
E. “A cache improves performance whenever a function is called repeatedly.”

For each, classify it as generally useful, conditional, or false as stated. Explain the relevant workload, readability, memory, and cache-invalidation considerations.

**Expected response:** five classifications with brief reasoning; do not substitute folklore for a benchmark.

## C03 — Fix a `ctypes` signature bug

- **Lesson:** `08-ctypes-and-cffi-for-native-code.md`
- **Difficulty:** Intermediate
- **Format:** FFI code review

A C library exports:

```c
size_t byte_count(const char *data);
```

The Python wrapper is:

```python
import ctypes

lib = ctypes.CDLL("./libsample.so")
lib.byte_count.argtypes = [ctypes.c_char_p]
# restype is not set
result = lib.byte_count(b"hello")
```

1. Explain the risk of leaving `restype` at its default.
2. Correct the wrapper's signature.
3. Explain what `c_char_p` does not tell the wrapper about: pointer validity, ownership, or buffer length.
4. Name a safer API design if the C function must process arbitrary binary data containing embedded NUL bytes.

**Expected response:** corrected code and pointer-contract explanation. Assume the library really exports the stated C ABI.

## C04 — FFI buffer lifetime and pointer safety

- **Lesson:** `08-ctypes-and-cffi-for-native-code.md`
- **Difficulty:** Advanced
- **Format:** Debugging scenario

A Python wrapper obtains a pointer to a mutable buffer, passes it to native code, and stores the pointer in a global C structure for later use. The Python function then returns; later, the native library dereferences the pointer and intermittently crashes. The team can implement the wrapper with either `ctypes` or `cffi`.

1. Explain the likely lifetime/ownership error and why a non-NULL pointer is not proof of valid memory.
2. Propose two safe design alternatives: one that copies data into native-owned memory and one that explicitly retains a valid owner/exporter for the full native-use interval.
3. Explain how you would express and enforce the contract with `ctypes` and with `cffi`. For `cffi`, distinguish ABI mode (`ffi.dlopen`) from API mode (compiled against declarations) and explain what API mode does and does not solve.
4. State which correctness/stress tests and native debugging tools could help verify the fix.

**Expected response:** lifetime/ownership analysis, a `ctypes`/`cffi` design comparison, and a test plan. Do not propose fabricating arbitrary pointer addresses as a test.

## C05 — Select between vectorization, Numba, and a native extension

- **Lesson:** `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`
- **Difficulty:** Intermediate
- **Format:** Architecture choice

A pure-Python loop performs arithmetic over a contiguous array of millions of `float64` values. Profiling shows the loop dominates CPU time. The operation is expressible as standard array arithmetic; no custom native library is required.

Compare:
1. NumPy/vectorization,
2. Numba,
3. PyO3 or pybind11,
4. retaining Python after an algorithmic review.

For each, discuss likely performance opportunity, conversion/build costs, implementation effort, and evidence needed before selecting it. State a reasonable first experiment and why.

**Expected response:** comparison table and recommendation under the stated assumptions.

## C06 — Read a native build configuration

- **Lesson:** `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`
- **Difficulty:** Advanced
- **Format:** Packaging review

Consider:

```toml
[build-system]
requires = ["maturin>=1.9,<2"]
build-backend = "maturin"

[project]
name = "fastmath-demo"
version = "0.1.0"
requires-python = ">=3.12"
```

The project also has a Rust `Cargo.toml` with a `cdylib` target and a PyO3 dependency.

1. Explain the distinct responsibilities of `[build-system]`, `[project]`, Cargo metadata, and the module initialization name.
2. Compare the build path shown here (`maturin` + PyO3) with a C++ `pybind11` extension built using CMake and `scikit-build-core`. What does the backend orchestrate, and what must the project still declare and test?
3. List the evidence needed before claiming that the package supports Linux, macOS, Windows, multiple Python versions, and free-threaded Python.
4. Explain what stable-ABI (`abi3`) support can and cannot guarantee.
5. Name two release-engineering or supply-chain controls relevant to native wheels.

**Expected response:** a configuration comparison and a release checklist grounded in built-wheel artifacts and CI evidence.

## C07 — Compare a native boundary with an existing library

- **Lesson:** `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`
- **Difficulty:** Advanced
- **Format:** Decision matrix

A proposed Rust extension receives a Python list, converts it to `Vec<f64>`, computes a small kernel, and returns a float. An alternative uses a prebuilt NumPy array and `numpy.dot`.

1. Write a simple end-to-end cost model that includes input conversion, boundary overhead, kernel work, and output conversion/allocation.
2. Explain why the Rust implementation might lose despite a fast kernel.
3. Define a fair kernel-focused comparison and a fair end-to-end comparison.
4. List at least four factors besides elapsed time that should influence a production decision.

**Expected response:** cost equation, benchmark design, and decision criteria.

## C08 — Native crash: choose the next diagnostic

- **Lesson:** `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`
- **Difficulty:** Advanced
- **Format:** Incident analysis

A Python ETL worker sometimes terminates with a segmentation fault when calling a C extension. The Python traceback is absent. The problem is not reproduced by every input.

1. Give a prioritized diagnosis plan using a minimal reproducer, `faulthandler`, a native debugger, and sanitizers where supported.
2. Explain what each tool can and cannot establish.
3. Name likely defect classes to investigate.
4. Explain why wrapping the call in `try/except Exception` does not reliably handle this failure.

**Expected response:** ordered plan with limitations.

## C09 — When is a native extension justified?

- **Lesson:** `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`
- **Difficulty:** Intermediate
- **Format:** Short design memo

A team wants to rewrite the slowest-looking function in Rust because “Rust is always faster.” No benchmark or profile has been captured. The function scans a list and checks membership in another list.

Write a concise response to the proposal. Include:
- the first measurements and correctness checks,
- the likely algorithmic improvement to consider,
- when vectorization or an existing library might fit,
- what evidence would justify a native extension,
- the ownership and packaging costs the team must accept.

**Expected response:** 250–400 words, with a decision gate rather than a premature yes/no.

## C10 — What would you measure first? Production incident: native optimization regresses latency

- **Lesson:** `03-timeit-and-microbenchmark-pitfalls.md`
- **Difficulty:** Advanced
- **Format:** **Measurement-first incident scenario 5 of 6**

After deploying a PyO3 implementation, median latency for a small batch gets worse, while a very large synthetic benchmark looks faster. The extension converts a Python list to a Rust vector on each call. Correctness tests pass.

1. What would you measure first?
2. Define a size curve and two benchmark modes that reveal the likely crossover and conversion cost.
3. Give at least three explanations other than “Rust is slow.”
4. State what evidence would justify batching, changing the data interface, keeping Python, or rolling back.

**Expected response:** an experiment plan with expected observations, not invented measurements.

## C11 — What would you measure first? Production incident: high CPU after enabling native threads

- **Lesson:** `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`
- **Difficulty:** Advanced
- **Format:** **Measurement-first incident scenario 6 of 6**

A service's CPU usage rises sharply after a native library starts using its own thread pool. Throughput improves for one request in isolation but p99 latency worsens under concurrent load. The Python event loop also handles network requests.

1. What would you measure first at both process and request level?
2. Explain how nested thread pools, GIL behavior, queueing, and event-loop blocking could contribute.
3. Propose a controlled concurrency experiment.
4. State the evidence that would support limiting native threads, moving work to an executor, batching, or reverting the change.

**Expected response:** incident plan with concurrency and latency metrics.

## C12 — Integrated mini-project: `slowlog` performance investigation

- **Lessons:** all nine files, especially `01`–`09`
- **Difficulty:** Advanced / Capstone
- **Format:** Practical project and report

Investigate the shared deliberately inefficient `slowlog` log/CSV ETL workload. Use a dataset realistic for your machine; the roadmap suggests 1–5 GB or a scaled dataset. Do not let resource limits make the experiment unsafe.

Your work must include:

1. Establish a correctness-checked baseline with a reproducible command, dataset description, environment, wall-clock time, and peak-memory measurement.
2. Profile with `cProfile`/`pstats` and inspect the profile with `snakeviz`; also sample a representative run or live process with `py-spy` where permissions/tool availability allow. Save the profile and sampling artifacts or document a justified, reproducible substitute when a tool cannot run.
3. Design a fair benchmark for at least one proposed change. Include repeated measurements, correctness checks, and an explanation of what is inside/outside the timed region. Add a `pytest-benchmark` regression test; if the plugin cannot be used, provide an equivalent reproducible test and explain the limitation.
4. Capture allocation activity with Memray and investigate growth or peak allocation using `tracemalloc`, Memray, or a justified combination. Distinguish cumulative allocation, retained memory, peak memory, and RSS. Add a `pytest-memray` memory ceiling where supported; otherwise record the platform/tool limitation and an alternative memory regression check.
5. Explain one object-lifetime or GC consideration supported by evidence.
6. Evaluate at least two optimization options from algorithm/data-structure changes, CPython idioms, streaming/copy reduction, vectorization, FFI, or a PyO3/pybind11/Cython extension. Try either vectorization or multiprocessing for a CPU-bound stage where applicable, including conversion/serialization costs; if not applicable, justify that decision. A native implementation remains optional and must be justified by evidence.
7. Run correctness/regression tests and document the risks and limitations.
8. Produce `PERF_REPORT.md` containing baseline, methods, findings, changes, before/after evidence, memory results, trade-offs, and what you deliberately chose not to optimize.

**Acceptance criteria:**
- Correctness tests remain unchanged or are strengthened; output equivalence is checked for representative normal, boundary, and malformed inputs.
- Commands, versions, data size, environment, and measurement procedures are reproducible.
- Saved `cProfile`/`pstats` plus `snakeviz` evidence, `py-spy` sampling evidence (or a documented justified substitute), and Memray allocation evidence support the bottleneck/memory claims.
- A `pytest-benchmark` regression test and a `pytest-memray` memory ceiling are included where supported; justified alternatives document the exact tool/platform limitation.
- Performance claims use repeated measurements and distinguish kernel-only from end-to-end costs.
- Memory claims identify the metric measured and the workload phase.
- At least one algorithmic hot spot, one retention/unbounded-cache issue, one avoidable copy, and one I/O inefficiency are investigated as required by the roadmap. A finding that a suspected issue is absent is acceptable if supported by evidence and replaced with a justified investigation.
- Consider multiprocessing or vectorization for a CPU-bound stage and include serialization/conversion costs if tried.
- Optional native implementation is accepted only if evidence supports it; “no native extension” is a valid result.
- The roadmap suggests a target of at least 3× speed-up **or** 50% peak-memory reduction on the final scenario, but do not force a universal number across machines or datasets. Report the result honestly and explain any shortfall.
- Every conclusion is labeled as measured, inferred, or still unknown.

**Expected deliverables:** benchmark script(s), correctness tests, profile/report artifacts, and `PERF_REPORT.md`.

---

# Answer Key and Explanations

**Use this section only after attempting the questions.** Example commands and code are starting points; adapt paths, permissions, and tool versions to the environment. Do not treat illustrative timings as expected outputs.

## Phase A answers

### A01 — `pstats` interpretation

- `ncalls` is the number of calls; recursive functions may display primitive and total call counts separated by `/`.
- `tottime` is time attributed to the function body excluding time in subcalls.
- `cumtime` includes the function and its subcalls.
- `percall` beside `tottime` is `tottime / primitive calls` in the common non-recursive case; beside `cumtime` it is `cumtime / calls`. For recursive output, inspect the exact call-count convention shown by `pstats`.
- `parse_line` is a plausible first target because it has 10,000 calls and 1.9 seconds cumulative time, but the next step is to inspect self time and its callers, validate representative input, and use a sampling/flame view if needed. `normalize` has 0.35 seconds self time; `load_csv` has 0.45 seconds self time.
- Cumulative times overlap: a caller's cumulative time includes its callees. Summing cumulative times double-counts nested work. Profilers also add overhead, so compare runs with a consistent method.

### A02 — Profile and inspect

One valid command:

```bash
python -m cProfile -o slowlog.prof slowlog.py --input sample.csv
```

One inspection command:

```bash
python -c "import pstats; pstats.Stats('slowlog.prof').strip_dirs().sort_stats('cumtime').print_stats(15)"
```

Alternatively:

```python
import pstats

stats = pstats.Stats("slowlog.prof")
stats.strip_dirs().sort_stats("cumtime").print_stats(15)
```

Compare the same input and environment before/after, including correctness, call counts, self/cumulative time, and unprofiled wall time. Profiling instruments calls and records statistics; it can distort very short functions and change total runtime.

### A03 — Flame graph

1. Width approximates how often a stack/frame was sampled, depending on the graph's format. It indicates frequent sampled presence, not automatically total wall time or a causal bottleneck.
2. An on-CPU profile primarily samples running stacks. Compare it with wall-clock duration, I/O metrics, and possibly a tool/mode that captures waiting states. A wide `file_read` frame in an on-CPU graph does not prove the process spent most time blocked on storage.
3. `normalize` appearing in many stacks suggests it is a shared path reached by multiple callers. Determine whether its own work is expensive or whether it is merely a common parent.
4. Examples: compare a second profile, inspect self-time/caller data, disable or replace regex in a controlled reproduction, measure bytes/records processed, or compare CPU utilization to elapsed time. A good answer says what result would falsify the hypothesis.

### A04 — `py-spy`

Commands (assuming `py-spy` is installed and OS permissions allow attachment):

```bash
py-spy dump --pid 4242
py-spy record --pid 4242 --output profile.svg --format flamegraph
```

A sampling dump is a snapshot of sampled thread stacks, not an exact event trace. Short calls may never be sampled, and observed proportions depend on sample count, duration, workload stability, and sampling mode. Attachment can fail because of ptrace/security restrictions, container boundaries, permissions, platform limitations, or an incompatible process/runtime configuration.

### A05 — Incident: CPU high

A good first action is a short representative sampling profile (`py-spy record` or `py-spy top`) while observing throughput and CPU, followed by `cProfile` on a reproducible input if needed. Preserve a deployment/version comparison. Competing explanations include an algorithmic regression, changed regex/input distribution, increased retries, lock contention/spin, different dependency/runtime versions, CPU throttling, and more work per record. If one Python function dominates self time, inspect its algorithm and input. If samples show lock waits or native frames, investigate synchronization/native work. If CPU is low but elapsed time high, shift toward waiting/I/O diagnosis. Do not infer cause from deployment timing alone.

### A06 — Incident: stalled job

First establish whether the process is alive and making progress: inspect recent logs/counters and sample thread stacks; use `py-spy dump --pid ...` if permitted. Compare repeated dumps: an unchanged stack may support a blocked wait or tight loop but does not prove deadlock. Check file descriptors, external service health, I/O wait, lock state, retry/backoff logs, and system calls as appropriate. Escalate to thread-level/application instrumentation or OS tracing when repeated observations and progress counters cannot distinguish causes. Low CPU can mean waiting, sleeping, throttling, or a process with little work; it is not proof of deadlock.

### A07 — Benchmark defect 1

Defects include one trial, different days/environments, unknown cache state, no input identity/size validation, no correctness check, possible background load, and no warm-up/repetition policy. Use the same immutable dataset, verify equivalent output, run multiple independent trials, report median and spread (or use `pyperf`), record runtime/hardware/tool versions, and avoid concurrent load. If cold-cache behavior matters, design a separate cold-cache experiment; report cold and warm cases separately rather than mixing them. Do not attempt to flush caches without documenting the method and its limits.

### A08 — Benchmark defect 2

The first benchmark includes `make_values` allocation/generation; the second uses precomputed input. These answer different questions. For kernel-focused measurement, precompute the same input for both and time only processing. For end-to-end measurement, include input creation/conversion and processing for both. Use identical data and output checks, repeated runs, and stable environment. Document setup code excluded by `timeit`'s `setup` and any conversion excluded from the timed statement.

### A09 — Benchmark defect 3

The implementations have different semantics and data distributions. One skips invalid rows and does not produce error details; therefore elapsed times cannot establish that it is a faster replacement. Define one output/error contract, run both on the same representative inputs including malformed records, and compare output equivalence or explicitly define the semantic change as a product requirement. If semantics intentionally differ, report them as separate behavior variants and do not label the comparison a like-for-like speed-up.

### A10 — Benchmark defect 4

The Numba first call may include compilation, whereas the Python median does not include an equivalent one-time setup. Run two studies: (a) cold-start latency including compilation/import where relevant, and (b) warm steady-state execution after compilation. Short-lived CLI jobs may care about cold start; long-lived workers may amortize compilation. Also hold data/type/algorithm constant, verify results, use repeated measurements, record versions, and avoid mixing profiler timings with wall-clock timings.

### A11 — Benchmark defect 5

Calling `perf_counter()` for every row adds timer and loop overhead, changes the workload, and the sum hides tail latency and whole-file behavior. Time a complete batch or function repeatedly with one timer around the operation. If per-record latency is important, collect a sample using a designed instrumentation strategy and account for its overhead; report a distribution rather than only a sum. Use realistic sizes, repeated trials, correctness checks, and a stable input. Avoid interpreting a microbenchmark of `normalize(row)` as the performance of the entire ETL pipeline.

### A12 — Benchmark defect 6

`cProfile` cumulative time is instrumented function time and includes nested calls; it is not interchangeable with unprofiled wall-clock elapsed time. Use profiles to find where work occurs, then benchmark old and new versions unprofiled under the same conditions and on equivalent inputs with correctness checks. Preserve source revision, commands, data, environment, repeated samples, summary statistics, and profile artifacts. Report an effect estimate and uncertainty (for example, a confidence interval) and decide whether the effect is practically meaningful using a margin defined before inspecting the result. A non-significant difference, a confidence interval crossing zero, or overlapping intervals do not prove that the implementations are equivalent. If equivalence is the claim, use a suitably designed equivalence/non-inferiority analysis with a predeclared margin; keep that separate from functional correctness testing. Explain whether the measured improvement survives end-to-end measurement.

## Phase B answers

### B01 — Snapshot differences

A positive difference indicates more traced allocation attributed to that traceback at snapshot B than at A; it does not prove the objects are permanently leaked or that all process memory is traced. Inspect `cached_records`: determine whether entries are bounded, whether keys/values are needed, and who owns the cache. Repeat snapshots after comparable batches and after expected cleanup; compare object counts/retention and process memory. Decoded strings may be transient or retained depending on references. A leak-like pattern is persistent growth across repeated equivalent cycles without a legitimate retention policy.

### B02 — `tracemalloc` versus RSS

Plausible explanations: native-library allocations not tracked by `tracemalloc`, allocator arenas retained for reuse, memory-mapped files, fragmentation, caches in native code, still-reachable Python objects not included in the compared snapshot interval, or measurement at different lifecycle points. `tracemalloc` tracks traced Python memory allocations (depending on when tracing began and tracing domains); RSS is resident physical memory mapped into the process, including Python/native heaps and mapped pages. Compare traced current/peak memory with RSS over identical phases; inspect native allocations with Memray where supported; use object-graph tools for retention; inspect mmap/native-library behavior. RSS staying high can reflect allocator reuse or fragmentation rather than an active leak.

### B03 — Retention code

`recent_results` retains each entire parsed batch indefinitely, so the old records remain reachable through the global list. If only the last ten counts are required:

```python
from collections import deque

recent_counts = deque(maxlen=10)

def process_batch(rows):
    result = [parse(row) for row in rows]
    count = len(result)
    recent_counts.append(count)
    return count
```

If the function only needs the count, avoid materializing `result` at all:

```python
def process_batch(rows):
    count = 0
    for row in rows:
        parse(row)
        count += 1
    recent_counts.append(count)
    return count
```

Choose the second only if parsed records are not needed for later work. Compare repeated batches with `tracemalloc` snapshots and inspect the retaining references; verify that output/count semantics are unchanged. If RSS grows while traced retained objects stabilize, investigate native allocations/allocator behavior too.

### B04 — Memray metrics

Cumulative allocation is the sum of allocations over time; freed blocks can contribute to that total. Peak memory is the high-water point during execution. End-of-run RSS is one point in time and includes resident native/Python/mapped memory. An allocation flame graph helps attribute allocation activity; a peak-oriented report identifies the phase/stack associated with the peak; retention needs snapshots, object reachability, and repeated lifecycle observations. A common command pattern is:

```bash
memray run -o slowlog.bin slowlog.py --input sample.csv
memray flamegraph slowlog.bin
```

Check `memray --help` for the installed version and report type. A leak claim needs evidence of persistent growth across comparable runs/batches, references or allocation sites retaining objects, and consideration of native allocations and allocator reuse.

### B05 — Reference counting and cycles

On a typical CPython run with cyclic GC enabled, the first print is usually `False` (the weak reference still resolves) because the two nodes form a strong reference cycle; after `gc.collect()`, the second is `True` once the cycle is collected. This is an implementation-oriented exercise; collection timing should not be treated as an immediate language-level guarantee on every Python implementation. A weak reference does not keep its referent alive and does not break the cycle by itself. Finalizers such as `__del__` can complicate ordering and resurrection/lifecycle reasoning, even though modern CPython can collect many cycles with finalizers.

### B06 — GC tuning decision

Measure end-to-end runtime, CPU profile, GC collection counts/durations (`gc.get_stats()`, callbacks), object/cycle behavior, memory, and latency distribution on representative data. If the hot path is parsing/normalization, GC tuning may not address the dominant cost. A carefully scoped temporary disable may be reasonable for a bounded batch known not to create cycles, with explicit re-enabling in `finally`, memory checks, and tests. Do not disable globally in a long-running service without evidence. Roll back if memory rises, cycles accumulate, tail latency worsens, or the improvement is not repeatable.

### B07 — Runnable cycle exercise

```python
import gc
import weakref


class Node:
    pass


left = Node()
right = Node()
left.other = right
right.other = left
ref = weakref.ref(left)

del left, right
print(ref() is not None)  # Expected True on a typical CPython run before collection.
collected = gc.collect()
print(collected)          # Exact count is implementation- and version-dependent.
print(ref() is None)      # Expected True after the cycle is collected.
```

A regular user-defined class supports weak references unless its layout is customized to remove that support. Do not assert an exact `gc.collect()` count; other unreachable objects may also be collected. The robust property is that the target becomes unreachable after collection, not a particular count.

### B08 — Incident: RSS grows each batch

First instrument RSS and traced current/peak memory at consistent lifecycle checkpoints: before batch, after parse, after transform/join, after output, and after dropping batch references/cleanup. Begin with `tracemalloc` if the hypothesis is Python object retention, while recording RSS concurrently; use Memray if native allocation sources or peak allocation are plausible. Competing causes: unbounded Python cache/list, lingering references in a result registry, native extension allocations, allocator arenas/fragmentation, mmap, buffer retention, or workload size drift. Persistent traced growth and object references suggest Python retention; stable traced memory with rising RSS suggests native/mapped/allocator causes. Repeat comparable batches before deciding.

### B09 — Incident: join peak

Capture a peak-memory profile and phase markers around input read, materialization, join, and output; record RSS and traced current/peak memory, and use Memray if available for allocation stacks. Total allocation is cumulative churn; peak is maximum simultaneous memory; final RSS is the resident footprint at exit. Remedies include streaming/chunked joins, projecting fewer columns, using an indexed or columnar engine, avoiding duplicate materializations, spilling to disk, or reducing concurrent workers. Each remedy should follow evidence about the dominant live structures and correctness requirements. `gc.collect()` after the peak cannot reduce memory that was simultaneously live during the join.

### B10 — Streaming redesign

The original reads the entire file as one string, creates a list of lines, creates a list of parsed records, then creates a filtered list. Peak memory can include multiple representations at once. One possible streaming version:

```python
def load_and_filter(path):
    accepted = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            record = parse(line)
            if record["valid"]:
                accepted.append(record)
    return accepted
```

This removes the whole-file text and intermediate line/parsed lists but still retains all accepted records in `accepted`. A generator/streaming consumer can lower peak further if downstream processing permits. Streaming may change behavior if parsing depends on cross-line context or output ordering, and may not lower peak if the returned result itself dominates memory. Test output equivalence on empty, normal, malformed, and large inputs; compare peak memory on the same dataset and report measured values without a fixed expected RSS.

### B11 — Tool choices

1. **`tracemalloc` snapshots:** Python traced allocations attributed to source tracebacks; does not cover all native allocations.
2. **Memray:** allocation activity including supported native allocations; coverage/platform support depends on configuration and environment.
3. **Memray peak report or phase-based RSS sampling:** peak during a transformation; combine with allocation stacks to identify causes.
4. **`objgraph` or direct object-reference inspection:** object relationships/reachability; must be used carefully because inspection can itself hold references.
5. **OS/process metrics:** repeated RSS/USS where available over time; shows process-level trend, not allocation origin. Pair with tracing to attribute the trend.

A strong answer distinguishes the question from the tool and states limitations.

## Phase C answers

### C01 — Algorithm before micro-optimization

`rows.count(row)` scans the list for each row, making the function \(O(n^2)\) in the common case. A local alias would not fix the repeated scans. One order-preserving approach:

```python
from collections import Counter

def find_duplicates(rows):
    counts = Counter(rows)
    return [row for row in rows if counts[row] > 1]
```

This preserves each occurrence of a duplicated value in original order, matching the original function's behavior, with expected \(O(n)\) counting time and \(O(k)\) extra space for \(k\) distinct hashable values. It assumes values are hashable; if they are not, use a different strategy. Test empty input, no duplicates, repeated values, ordering, and the hashability contract.

### C02 — Folklore

A. **Conditional:** list comprehensions are often efficient and clear for materialized lists, but “always” is false; generators, built-ins, libraries, and workload semantics differ.  
B. **False as stated:** `__slots__` can reduce per-instance memory for suitable classes but does not automatically make all code faster and changes instance behavior.  
C. **Generally useful:** a built-in implemented in C can reduce Python-level iteration overhead, but measure the actual workload.  
D. **Conditional:** local aliasing can help some hot loops but may reduce readability and often has negligible effect relative to algorithm/data-layout costs.  
E. **False as stated:** caching helps only when reuse outweighs lookup/storage costs and invalidation/retention are correct; unbounded caches can cause memory growth and stale results.

The appropriate test is a representative benchmark plus correctness and maintainability review.

### C03 — Correct `ctypes` signature

```python
import ctypes

lib = ctypes.CDLL("./libsample.so")
lib.byte_count.argtypes = [ctypes.c_char_p]
lib.byte_count.restype = ctypes.c_size_t
result = lib.byte_count(b"hello")
```

Without `restype`, `ctypes` assumes C `int`, which can truncate or misinterpret a wider return such as `size_t`. `c_char_p` models a NUL-terminated byte string argument; it does not validate arbitrary pointer addresses, transfer ownership, or convey a separate binary length. For arbitrary bytes, prefer an API such as `size_t byte_count(const unsigned char *data, size_t length)` and pass a buffer plus explicit length, keeping the buffer alive for the call.

### C04 — FFI lifetime

The native code stores a pointer into Python-managed memory after the Python object/buffer may be released or moved out of its valid lifetime. Non-NULL only says the pointer value is not zero; it does not prove the memory is valid, correctly sized, owned, or still alive. Safe alternatives are (1) copy into native-owned memory and define who frees it, or (2) retain a strong reference/exporter or explicit owner object until native use has definitely ended, with a safe close/release lifecycle. With `ctypes`, keep the exporter/buffer owner alive and make the C API's pointer-plus-length and ownership contract explicit. With `cffi`, `ffi.new` allocations are owned by the corresponding cdata object and must remain referenced; `ffi.from_buffer` also depends on the exported buffer's lifetime. ABI mode calls a library using declarations supplied to `cdef`, while API mode compiles against headers/declarations and can catch some declaration mismatches at build time; neither mode automatically fixes use-after-free or invalid ownership. Avoid asynchronous retention unless the wrapper can enforce lifetime. Add stress tests, repeated allocation/GC tests, and native ASan/debugger runs where supported. Never dereference an unvalidated pointer in a test.

### C05 — Vectorization, Numba, native extension

A reasonable first experiment is vectorized NumPy because the operation is expressible as array arithmetic and data is already contiguous. Verify output and compare end-to-end time, including conversion if needed. Numba is a good candidate for a custom numerical loop with supported types when compilation/warm-up is acceptable. PyO3/pybind11 may be justified for custom kernels, integration with an existing native library, or a need not served by existing tools, but introduces compiler, ABI, wheel, and debugging cost. Retaining Python is reasonable if profiling shows the loop is not material, the data is small, or the alternatives' complexity outweighs gains. Choose from measurements and constraints, not language branding.

### C06 — Build configuration and release evidence

- `[build-system]` specifies the PEP 517 backend and its build requirements.
- `[project]` contains distribution metadata and supported Python-version declaration; it does not prove binary compatibility.
- `Cargo.toml` defines Rust crate metadata, crate type, dependencies, and features. `maturin` coordinates the Python packaging/build integration for the PyO3 project; the Rust crate and PyO3 module configuration still need to agree on the extension module name and initialization.
- For a C++/`pybind11` project, CMake describes native targets and linking, while `scikit-build-core` acts as the PEP 517 backend that drives CMake as part of Python package builds. Neither backend by itself proves the wheel works on every target platform.
- The module initialization/import name must match the extension name expected by the build and Python import.
- Support claims require a declared matrix of Python versions, OS/architectures, ABI tags, and dependencies; CI build logs, tests on produced wheels in clean environments, and release records. Inspect and test the actual built wheels, not just source configuration.
- `abi3` can reduce the number of CPython-version-specific wheels for extensions that truly use the Limited API and whose binding framework supports the chosen mode. It does not guarantee OS/architecture portability, free-threaded compatibility, or that arbitrary CPython APIs are stable.
- Controls include pinned/reviewed build dependencies, lock/provenance records, reproducible build settings, wheel inspection, vulnerability/license checks, SBOM generation, and trusted publishing. Accept any two with appropriate context.

### C07 — Native boundary cost

A useful model is:

\[
T_{\text{total}} =
T_{\text{convert,in}} + T_{\text{boundary}} + T_{\text{kernel}} +
T_{\text{convert,out}} + T_{\text{allocation}}
\]

The Rust kernel may be fast while list-to-`Vec<f64>` conversion and allocation dominate. Kernel-focused comparison preconstructs each implementation's input representation and times only its operation; end-to-end comparison starts from the same user-facing input and includes all conversion/allocation that production pays. Also consider correctness/semantics, peak memory, latency distribution, portability, build/maintenance cost, security, concurrency behavior, and team expertise.

### C08 — Native crash diagnosis

1. Preserve environment/build identifiers and reduce the input to a minimal reproducer.
2. Enable `faulthandler` (for example `python -X faulthandler script.py`) to obtain Python stack context on fatal signals; it may not identify the exact native instruction.
3. Reproduce with a symbolized debug build under `gdb`, `lldb`, or the platform debugger and capture native backtraces.
4. Use ASan/UBSan or other supported sanitizers in a compatible build to find certain memory/undefined-behavior defects; sanitizer success is not proof of correctness.
5. Investigate out-of-bounds access, use-after-free, invalid pointer/length, ABI mismatch, data races, and native dependency defects.
A segmentation fault terminates the process and is not normally converted to a Python `Exception`; `try/except` cannot reliably recover from it.

### C09 — Respond to “Rust is always faster”

A strong memo rejects the premise without rejecting native code categorically. First establish correctness and profile the same representative workload. The stated repeated list-membership scan may be an \(O(n^2)\) algorithm; converting the lookup collection to a set or building an index may improve complexity more simply than a native rewrite. Benchmark the refactor and test duplicates/order/edge cases. If the remaining hot path is numerical and data is array-like, compare vectorization or Numba. A native extension becomes a candidate if a material CPU hot spot remains, the operation is coarse-grained, and end-to-end tests show a repeatable gain after conversion. The team must own Rust/C++ toolchains, wheels, platform/ABI testing, native crash debugging, dependency security, and future upgrades. A justified “not yet” is a sound decision.

### C10 — Incident: native regression for small batches

Measure end-to-end latency by batch size, including list-to-vector conversion, allocations, and result conversion; separately time the kernel only if that measurement can be isolated accurately. Use sizes from empty/tiny to production-scale, repeated trials, identical data, and correctness checks. Potential explanations include conversion overhead, per-call boundary cost, different data layout, compiler settings, small-input overhead, different benchmark setup, or the large synthetic test not representing production. If larger batches amortize conversion, batching may help. If an existing array API avoids copies, change the data interface. If no meaningful production gain remains, retain Python or roll back. Make the decision from repeated production-like measurements, not one median alone.

### C11 — Incident: native threads and p99 regression

Measure request p50/p95/p99 latency, throughput, CPU utilization, runnable thread count, context switches, native thread-pool size, queue depth, and event-loop lag. Compare one request, bounded concurrency, and production-like concurrency. Nested thread pools can oversubscribe CPUs; native locking or memory-bandwidth contention can reduce throughput; a synchronous native call can block the event-loop thread even if it releases the GIL; and GIL release only helps when the native region is safe to execute detached and the workload can use the available concurrency. Limit native threads if oversubscription correlates with p99, move blocking work off the event loop if it blocks callbacks, batch if boundary overhead dominates, or revert if the change violates latency SLOs. Use repeated tests and preserve correctness.

### C12 — Capstone evaluation rubric

A strong submission contains all eight requested work items, with evidence artifacts and clear distinctions among measured facts, interpretations, and unknowns. Grade on:

- **Correctness (25%):** output/error semantics tested against a reference; regression tests retained or strengthened.
- **Measurement quality (20%):** reproducible commands, controlled inputs, repeated unprofiled timing, `pytest-benchmark` or a justified substitute, profile interpretation, and no comparison of incompatible metrics.
- **Memory reasoning (15%):** distinguishes traced, native, cumulative, retained, peak, and RSS measures; investigates lifecycle/retention; includes `pytest-memray` or a justified alternative memory regression check.
- **Optimization reasoning (15%):** algorithm/data layout and existing-library options considered before native code; conversion costs included.
- **Engineering quality (15%):** safe change, test/CI evidence, memory and performance regressions considered, risks documented.
- **Report quality (10%):** concise `PERF_REPORT.md` with commands, environment, before/after evidence, limitations, and deliberately rejected optimizations.

The roadmap's 3× speed-up or 50% peak-memory reduction is a target for the selected final scenario, not a universal guarantee. A lower gain can still be a high-quality result if the experiment is sound, the improvement is real, and limitations are explained. A large claimed gain without correctness and reproducibility does not pass.

---

## Coverage and scoring guide

Suggested grading: 2–4 points per question based on complexity, with capstone scored separately using the rubric above. For every answer, reward explicit assumptions, valid reasoning, and an appropriate next measurement. Do not reward unsupported certainty or a number that was not measured.

The assessment intentionally does not prescribe universal timing thresholds. Timing depends on interpreter version, build, CPU, OS, filesystem/cache state, data shape, dependency versions, and workload. Deterministic correctness properties and reproducible procedures are the acceptance criteria; performance measurements are evidence to interpret, not magic constants.
