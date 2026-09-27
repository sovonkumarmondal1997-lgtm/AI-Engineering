# Profiling and Measuring Before Optimizing in Python

**Stage 1 — Programming & Computational Thinking → 10 — Production Habits for Python Programs**

> **Core principle:** Measure before optimizing.

A performance problem should be treated as an engineering investigation, not a guessing contest. A reliable workflow is:

```text
observe
  ↓
measure
  ↓
identify bottleneck
  ↓
form hypothesis
  ↓
optimize
  ↓
measure again
  ↓
compare
  ↓
keep or revert
```

This chapter teaches standard-library tools first: `time`, `timeit`, `cProfile`, `pstats`, and `tracemalloc`. It intentionally stays focused on Python-level measurement and profiling rather than becoming a full performance-engineering or distributed-systems course.

## 1. Overview

When a developer says, “This program is slow,” the statement is incomplete. Slow compared with what, for which input, on which machine, under what workload, and measured how?

A production engineer turns the complaint into measurable questions:

- How much wall-clock time does the workload take?
- How much CPU time does the process consume?
- Is the job CPU-bound, I/O-bound, or memory-constrained?
- Which functions contribute most to elapsed execution time?
- How much memory is allocated or retained?
- Did a proposed change actually improve the relevant metric?
- Did the optimization preserve correctness and acceptable maintainability?

The objective is not to make every line of Python as fast as possible. The objective is to improve the system's important performance characteristics where evidence shows improvement is useful.

## 2. Learning Objectives

- Define latency, throughput, wall-clock time, CPU time, memory use, peak memory, allocation behavior, and scalability.
- Measure elapsed time correctly with `time.perf_counter()`.
- Use `timeit.timeit()`, `timeit.repeat()`, and `timeit.Timer` for controlled microbenchmarks.
- Explain why one timing run is noisy and why benchmark setup must be separated from the target operation.
- Use `cProfile` and `pstats` to find function-level time hotspots and interpret `ncalls`, `tottime`, `cumtime`, `percall`, callers, and callees.
- Use `tracemalloc` to investigate Python allocation behavior and compare snapshots.
- Distinguish CPU-bound, I/O-bound, and memory-related problems.
- Establish a baseline, form an optimization hypothesis, change one meaningful thing, measure again, and make a keep/revert decision.
- Apply the workflow to data processing, evaluation, embedding, retrieval, and batch AI workloads.

## 3. What Does "Performance" Mean?

Performance is not a single number. It describes how a program behaves with respect to time, resource consumption, and workload.

For a command-line batch job, total elapsed runtime may matter most. For a service, latency and throughput may matter. For a data pipeline, records per second and peak memory may matter. For an AI workload, external request latency, local preprocessing time, batching efficiency, and memory pressure can all matter.

**Latency** is the time associated with an individual operation or request.

**Throughput** is the amount of useful work completed per unit time.

**Wall-clock time** is the elapsed real-world duration between two points.

**CPU time** is time the process actually spends consuming CPU, rather than waiting.

**Peak memory** is the highest observed amount of memory in the chosen measurement scope.

**Scalability** describes how resource usage or performance changes as workload size changes.

```python
import time

def work():
    total = 0
    for value in range(1_000_000):
        total += value
    return total

start = time.perf_counter()
result = work()
elapsed = time.perf_counter() - start

print(f"result={result}")
print(f"wall_clock_seconds={elapsed:.6f}")
```

The number printed by this example is a measurement of one execution under the current machine and operating conditions. It is not a universal runtime for `work()`.

A useful performance statement is therefore closer to:

> “On this machine, with this Python version and this input size, this workload took roughly this long under this measurement method.”

That wording keeps the evidence attached to its conditions.

## 4. Why We Measure Before Optimizing

“I think this function is slow” is a hypothesis. It is not evidence.

A developer may spend an hour rewriting a loop while the real bottleneck is file I/O, JSON serialization, an external API request, an inefficient algorithm elsewhere, or millions of calls to a tiny function.

Measurement changes optimization from intuition-driven editing to hypothesis testing:

```text
Observation
  ↓
Measurement
  ↓
Bottleneck identification
  ↓
Optimization hypothesis
  ↓
One meaningful change
  ↓
Functional tests
  ↓
Measurement again
  ↓
Comparison
```

| Situation | Likely mistake | Measurement question |

| --- | --- | --- |

| A loop looks expensive | Optimize the loop immediately | How much total time is actually inside the loop? |

| A tiny function is very fast | Ignore it because one call is cheap | How many times is it called? |

| A parser is complex | Assume parser is the bottleneck | What does the profiler show? |

| A batch job feels slow | Measure only one record | How does runtime scale with realistic batch sizes? |

| An AI pipeline is slow | Optimize prompt construction first | How much time is spent waiting on external inference? |

## 5. What Is a Bottleneck?

A bottleneck is a part of a system that materially limits the performance characteristic you care about.

In a sequential Python program, a function consuming 70% of cumulative runtime is often more important to investigate than a function consuming 0.2%. In another workload, memory pressure or external waiting may be the real constraint.

Bottlenecks are relative to a goal. If a batch job is already comfortably inside its schedule window, reducing one function by 5% may have little business value. If a pipeline misses a hard deadline, the same improvement might matter.

Never infer the bottleneck from code appearance alone.

## 6. Types of Performance Problems

| Type | Typical symptoms | First questions |

| --- | --- | --- |

| CPU-bound | High CPU usage; expensive computation | Which functions consume CPU? Is the algorithm appropriate? |

| I/O-bound | Process spends time waiting | How much time is spent on file/database/network waits? |

| Memory-related | Large resident memory, allocation growth, swapping risk | What objects are being allocated or retained? |

| Mixed | Several resource types interact | Which resource is currently limiting the target metric? |

```python
import time

def cpu_work():
    total = 0
    for i in range(2_000_000):
        total += i * i
    return total

def waiting_work():
    time.sleep(0.05)

start = time.perf_counter()
cpu_work()
print(f"cpu_work wall time: {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
waiting_work()
print(f"waiting_work wall time: {time.perf_counter() - start:.4f}s")
```

Both operations consume wall-clock time, but their resource stories are different. `waiting_work()` mostly waits; `cpu_work()` actively computes. This is why using one performance metric blindly can produce the wrong diagnosis.

## 7. Measurement vs Benchmarking vs Profiling

| Concept | Main question | Typical tool |

| --- | --- | --- |

| Measurement | How long did this operation or phase take? | `perf_counter()` |

| Benchmarking | How does a small operation behave under repeatable conditions? | `timeit` |

| Profiling | Where is the program spending execution time? | `cProfile` + `pstats` |

| Memory profiling | Where is Python memory being allocated or changing? | `tracemalloc` |

Think of the tools as complementary.

Timing can tell you that a pipeline takes 8 seconds. Profiling can tell you that 5 seconds are spent in parsing. A microbenchmark can then compare two parsing techniques on representative data. `tracemalloc` can investigate whether the change reduces or increases Python allocation behavior.

A profiler and a benchmark answer different questions; neither replaces the other.

## 8. Basic Timing with Python

For elapsed-duration measurement, start and end around the work you actually want to measure. `time.perf_counter()` is designed for measuring short durations using a high-resolution performance counter. Its absolute reference point is not meaningful; the difference between readings is what matters. The clock includes time spent sleeping, which makes it appropriate for elapsed wall-clock timing. citeturn130118search0

## 9. `time.perf_counter()`

```python
import time

start = time.perf_counter()

total = sum(range(1_000_000))

elapsed = time.perf_counter() - start
print(f"elapsed_seconds={elapsed:.6f}")
print(f"total={total}")
```

Line by line:

1. `import time` loads the standard-library time functions.
2. `perf_counter()` records the starting clock reading.
3. `sum(range(...))` is the target workload.
4. The second `perf_counter()` reading is subtracted from the first.
5. The result is a duration in fractional seconds.

The clock's value itself is not useful for logging a calendar timestamp; use an appropriate wall-clock timestamp mechanism for that job.

## 10. Measuring a Single Operation

```python
import time

def transform(value: int) -> int:
    return value * value + 1

start = time.perf_counter()
result = transform(123)
elapsed = time.perf_counter() - start

print(result)
print(f"elapsed={elapsed:.9f}s")
```

Microsecond- or nanosecond-scale single-call timings can be dominated by measurement overhead, scheduler activity, cache state, interpreter state, and other noise. Use this style to instrument meaningful application phases, not to make strong claims about tiny operations after one run.

## 11. Measuring Repeated Operations

```python
import time

def transform(value: int) -> int:
    return value * value + 1

values = list(range(100_000))

start = time.perf_counter()
results = [transform(value) for value in values]
elapsed = time.perf_counter() - start

print(f"items={len(results)}")
print(f"elapsed={elapsed:.6f}s")
```

Measuring a realistic unit of work often gives a stronger signal than measuring one tiny call. Notice that the setup—constructing `values`—happens outside the measured region because the question here is about transformation cost.

## 12. Why One Timing Run Is Not Reliable

A single timing result can move because of operating-system scheduling, CPU frequency changes, background programs, cache state, garbage collection, and I/O variability. Repeating measurements makes the variation visible.

Manual repetition with `perf_counter()` is useful for learning, but `timeit` is usually a better fit for small, repeatable Python benchmarks because it handles repeated execution mechanics for you.

```python
import time

def benchmark_once() -> float:
    start = time.perf_counter()
    total = sum(range(100_000))
    _ = total
    return time.perf_counter() - start

measurements = [benchmark_once() for _ in range(5)]
for value in measurements:
    print(f"{value:.6f}s")
```

## 13. `timeit`

The `timeit` module is intended for measuring small pieces of Python code. Its design helps avoid several common mistakes in microbenchmarking, including accidentally including repeated setup or relying on one execution.

For application-level timing, `perf_counter()` remains useful. For controlled microbenchmarks of alternative Python implementations, `timeit` is usually more appropriate.

## 14. `timeit.timeit()`

```python
import timeit

duration = timeit.timeit(
    "sum(range(1000))",
    number=10_000,
)

print(f"total_seconds={duration:.6f}")
print(f"seconds_per_call={duration / 10_000:.9f}")
```

`statement` is the code being measured. `number` controls how many times the statement runs. The returned value is total elapsed time for all repetitions in that run.

When using strings, keep the benchmark expression small and obvious. Callable usage is often clearer for reusable Python functions.

```python
import timeit

def calculate() -> int:
    return sum(range(1000))

duration = timeit.timeit(calculate, number=10_000)
print(f"total_seconds={duration:.6f}")
```

Callable benchmarking avoids embedding a function call inside an `exec` string. `timeit` accepts a callable plus positional and keyword arguments in versions where the API supports them, but passing a zero-argument callable is an easy beginner pattern.

## 15. `timeit.repeat()`

```python
import timeit

def calculate() -> int:
    return sum(range(1000))

results = timeit.repeat(
    calculate,
    number=10_000,
    repeat=5,
)

for index, value in enumerate(results, start=1):
    print(f"batch={index} total_seconds={value:.6f}")
```

`repeat()` runs several benchmark batches. The resulting list lets you inspect variation instead of pretending the process has one exact runtime.

Do not blindly interpret one statistic as universally “correct.” The summary you choose should match the question. For example, a lower-bound view can be useful for asking “how fast is this when interference is minimal,” while a median or distribution view may better represent typical behavior under repeated local conditions.

## 16. `timeit.Timer`

```python
import timeit

def calculate() -> int:
    return sum(range(1000))

timer = timeit.Timer(calculate)

single_batch = timer.timeit(number=5_000)
batches = timer.repeat(repeat=3, number=5_000)

print(f"single_batch={single_batch:.6f}s")
print(f"repeated={batches}")
```

`Timer` packages the benchmark target so you can call related methods repeatedly. Important methods for this chapter are `timeit()`, `repeat()`, and `autorange()`.

## 17. `timeit.default_timer`

```python
import timeit

timer_function = timeit.default_timer

start = timer_function()
total = sum(range(100_000))
elapsed = timer_function() - start

print(total)
print(f"elapsed={elapsed:.6f}s")
```

`timeit.default_timer` provides the timer that `timeit` selects for the current platform. It is intended for timing rather than for calendar timestamps. Treat it as a platform-appropriate high-resolution elapsed-time clock.

## 18. Avoiding Common Benchmarking Mistakes

- Measuring input construction when the target is only processing.
- Printing inside the measured loop.
- Changing both the implementation and the workload at the same time.
- Benchmarking one implementation on tiny data and another on large data.
- Comparing results from different Python versions or hardware without documenting the difference.
- Calling a benchmark “10% faster” when the observed variance is larger than the difference.

## 19. Benchmark Design

A good benchmark defines a precise question.

Bad question:

> Which function is faster?

Better question:

> For 100,000 integers on Python 3.x on this machine, which implementation computes the same result with lower median elapsed time over repeated benchmark batches?

Control what you can:

1. Choose representative input.
2. Prepare shared input outside the measured region when setup is not part of the target.
3. Measure equivalent work.
4. Repeat the benchmark.
5. Record the environment and assumptions.
6. Inspect variance instead of hiding it.
7. Validate correctness separately.

```python
import timeit

data = list(range(10_000))

def sum_loop() -> int:
    total = 0
    for value in data:
        total += value
    return total

def sum_builtin() -> int:
    return sum(data)

loop_times = timeit.repeat(sum_loop, number=1_000, repeat=5)
builtin_times = timeit.repeat(sum_builtin, number=1_000, repeat=5)

print("loop:", loop_times)
print("builtin:", builtin_times)
```

The functions share the same `data`. The benchmark isolates the computation. A real engineering decision would also verify that both functions return the same value and would interpret the measurements together with maintainability and workload requirements.

## 20. CPU Time vs Wall-Clock Time

```python
import time

start_wall = time.perf_counter()
start_cpu = time.process_time()

time.sleep(0.05)

wall_elapsed = time.perf_counter() - start_wall
cpu_elapsed = time.process_time() - start_cpu

print(f"wall_elapsed={wall_elapsed:.4f}s")
print(f"cpu_elapsed={cpu_elapsed:.4f}s")
```

`perf_counter()` measures elapsed duration and includes time spent sleeping. `process_time()` measures CPU time consumed by the current process and does not advance during sleep. The two readings therefore answer different questions. citeturn130118search0

For I/O-bound programs, wall-clock time captures user-visible waiting. CPU time can help determine whether the process itself is actually consuming CPU or mostly waiting.

## 21. Algorithmic Complexity vs Actual Runtime

Big-O notation describes how a resource requirement scales with input size. It does not directly give the runtime of one execution on one machine.

An `O(n)` algorithm can beat an `O(log n)` implementation at tiny sizes if the constant costs and setup differ. Conversely, an algorithm with a worse asymptotic complexity can look fine at small inputs and become unacceptable at larger scales.

```python
def linear_search(items: list[int], target: int) -> bool:
    for item in items:
        if item == target:
            return True
    return False

def set_contains(items: list[int], target: int) -> bool:
    lookup = set(items)
    return target in lookup
```

The first function performs a linear scan. The second builds a set and then performs membership lookup. The second function has setup work, so it is not automatically faster for one lookup. If many lookups are performed against the same data, the setup cost can become worthwhile.

This is exactly why complexity analysis and measurements complement each other.

## 22. Big-O and Real Measurements

```python
import timeit

data = list(range(10_000))

linear = lambda: linear_search(data, 9_999)

lookup_set = set(data)
set_lookup = lambda: 9_999 in lookup_set

linear_times = timeit.repeat(linear, number=10_000, repeat=5)
set_times = timeit.repeat(set_lookup, number=10_000, repeat=5)

print("linear search:", linear_times)
print("set lookup:", set_times)
```

The benchmark deliberately reuses the set so it answers a lookup question. Including set construction inside every timing run would answer a different question.

Do not use a lambda merely because it is short; named benchmark functions are generally easier to inspect, explain, and maintain.

## 23. Why a Better Big-O Algorithm Can Still Be Slower for Small Inputs

Asymptotic complexity ignores constant factors. A different data structure may have extra allocation, hashing, setup, or conversion costs. For small inputs, those fixed costs can dominate.

The right reasoning is:

```text
complexity analysis → expected scaling
benchmark → observed behavior under chosen workload
```

Neither should be used as a substitute for the other.

**Key Takeaway:** Optimize for the workload you actually care about, then verify that the observed improvement matters.

# Profiling

## 24. Profiling

A profiler records execution statistics so you can investigate where time is being spent. Instead of asking “which line looks complicated?”, you ask “which functions and call paths account for meaningful execution cost?”

Profiling is especially useful when the program contains many functions and you do not know which part dominates.

## 25. What a Profiler Does

```python
def parse(values):
    return [int(value) for value in values]

def transform(values):
    return [value * value for value in values]

def summarize(values):
    return sum(values)

def main():
    raw = ["1", "2", "3"] * 10_000
    parsed = parse(raw)
    transformed = transform(parsed)
    return summarize(transformed)

if __name__ == "__main__":
    print(main())
```

If this program becomes slow, timing only `main()` tells you the total duration. Profiling can reveal whether parsing, transformation, or summarization dominates.

## 26. Deterministic Profiling

Python's `cProfile` provides deterministic profiling: it records statistics about function calls and timing while the program runs. The standard library describes `cProfile` as the implementation recommended for most users, while noting that profiling itself has overhead. citeturn130118search7

“Deterministic” here means instrumentation records execution events in a deterministic fashion; it does not mean the measured program has deterministic runtime.

## 27. `cProfile`

```python
import cProfile

def work() -> int:
    total = 0
    for i in range(200_000):
        total += i * i
    return total

def main() -> None:
    print(work())

if __name__ == "__main__":
    cProfile.run("main()")
```

The string passed to `cProfile.run()` is executed in the `__main__` namespace. For maintainable code, the programmatic `Profile` interface is usually clearer because it avoids string-based execution and gives explicit control over the profile lifecycle.

## 28. Running `cProfile`

From a shell, the standard command-line form is:

```bash
python -m cProfile script.py
```

The module interface can also profile a module with `-m`, and profiling results can be written to a file with `-o` for later inspection. Python's current documentation supports these command-line forms. citeturn130118search7

## 29. `python -m cProfile`

```text
# Save as a normal Python program and run from the shell:
#
# python -m cProfile -s cumulative app.py
```

The command is shown as shell syntax rather than Python source. `-s cumulative` is useful when you want output sorted by cumulative time. For larger investigations, saving a profile file and reading it with `pstats` is often more manageable.

## 30. `cProfile.Profile`

```python
import cProfile

def compute() -> int:
    total = 0
    for i in range(100_000):
        total += i ** 2
    return total

profiler = cProfile.Profile()
profiler.enable()
result = compute()
profiler.disable()

print(f"result={result}")
profiler.print_stats(sort="cumulative")
```

`Profile` lets you choose exactly what code is inside the profiling window. This makes it useful when you want to profile one phase of a larger program instead of every startup action.

## 31. `enable()`

```python
import cProfile

def work() -> int:
    return sum(i * i for i in range(10_000))

profiler = cProfile.Profile()
profiler.enable()

result = work()

profiler.disable()
print(result)
```

`enable()` starts collecting profiling information for subsequent execution. Start it as close as practical to the workload you want to investigate.

## 32. `disable()`

```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()
sum(range(50_000))
profiler.disable()

profiler.print_stats()
```

`disable()` stops collecting profile events. You can leave the profiler object in memory and inspect the accumulated statistics afterward.

## 33. `create_stats()`

```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()
sum(range(100_000))
profiler.disable()

profiler.create_stats()
profiler.print_stats()
```

`create_stats()` creates the internal statistics representation from collected profiling data. `print_stats()` can then display those statistics. Modern versions of `cProfile.Profile.print_stats()` also accept sorting parameters, but using `pstats.Stats` gives more explicit report control.

## 34. `print_stats()`

```python
import cProfile

def work() -> int:
    return sum(i * i for i in range(10_000))

profiler = cProfile.Profile()
profiler.enable()
work()
profiler.disable()
profiler.print_stats(sort="cumulative")
```

`print_stats()` produces a human-readable report. The report is a starting point for investigation, not an automatic list of instructions to optimize.

## 35. `runcall()`

```python
import cProfile

def work(size: int) -> int:
    return sum(i * i for i in range(size))

profiler = cProfile.Profile()
result = profiler.runcall(work, 20_000)

print(result)
profiler.print_stats(sort="cumulative")
```

`runcall()` profiles a function call and returns that function's return value. It is convenient when the boundary of the workload is one function.

## 36. `run()`

```python
import cProfile

profiler = cProfile.Profile()

profiler.run("result = sum(range(20_000))")
profiler.print_stats(sort="cumulative")
```

`run()` profiles code executed through `exec()` in the profiler's environment. It can be useful for exploratory work, but for application code an explicit function call is easier to reason about.

## 37. `runctx()`

```python
import cProfile

data = {"values": range(10_000)}
profiler = cProfile.Profile()

profiler.runctx(
    "result = sum(values)",
    {"values": data["values"]},
    {},
)
profiler.print_stats(sort="cumulative")
```

`runctx()` is like `run()` but lets you supply explicit globals and locals mappings for the executed string. This is mainly useful when you need controlled execution context. Prefer direct Python function calls for normal application profiling.

## 38. Understanding `cProfile` Output

```python
import cProfile
import io
import pstats

def slowish() -> int:
    total = 0
    for i in range(100_000):
        total += i * i
    return total

profiler = cProfile.Profile()
profiler.enable()
slowish()
profiler.disable()

stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats("cumulative").print_stats(10)
print(stream.getvalue())
```

A typical report contains columns that describe call counts and timing. The exact numbers depend on the machine, Python version, and run. Focus on relationships and hotspots rather than memorizing sample values.

## 39. `ncalls`

`ncalls` reports call counts. A high count is a clue, not a verdict.

A function that takes 2 microseconds and runs 10 million times may matter enormously. A function that takes 2 seconds and runs once may matter even more. Compare count with time spent.

## 40. `tottime`

`tottime` is the time spent inside the function itself, excluding the time spent in functions it calls. A high `tottime` suggests self-work in that function may be worth investigating.

## 41. `cumtime`

`cumtime` is cumulative time spent in the function, including the time spent in its subcalls. High cumulative time often identifies an important call path, but you still need to inspect which child functions contribute to that total.

## 42. `percall`

`percall` is a derived time figure. Its exact meaning depends on the column it accompanies. In the standard profile report it commonly represents a time-per-call calculation based on `tottime` or `cumtime`.

Do not memorize one fixed interpretation without checking the column context.

## 43. `filename:lineno(function)`

The location field identifies the Python file, line number, and function name associated with the entry. It lets you connect a profile row to source code.

A useful investigation loop is:

```text
profile row
→ source location
→ understand work
→ inspect callers/callees
→ form hypothesis
```

## 44. Sorting and Reading Profile Results

```python
import cProfile
import pstats

def work() -> int:
    total = 0
    for i in range(100_000):
        total += i * i
    return total

profiler = cProfile.Profile()
profiler.enable()
work()
profiler.disable()

stats = pstats.Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumtime")
stats.print_stats(20)
```

Sorting by cumulative time is a good first investigation because it surfaces functions and call paths that account for substantial total execution time. Sorting by `tottime` asks a different question: which functions themselves consume the most self-time?

## 45. `pstats`

`pstats` is the standard-library module used to analyze and format profiling statistics. A `pstats.Stats` object can be created from an in-memory `Profile` object or from profile-data files. citeturn130118search4

## 46. `pstats.Stats`

```python
import cProfile
import pstats

def workload() -> int:
    return sum(i * i for i in range(20_000))

profiler = cProfile.Profile()
profiler.runcall(workload)

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)
```

`Stats` is the analysis object. It lets you transform a raw profile into a focused report. The goal is not to print everything; the goal is to ask useful questions and narrow attention to evidence.

## 47. Common `pstats` Operations

The most useful beginner-to-intermediate operations for this chapter are:

- `strip_dirs()` to reduce path noise.
- `sort_stats(...)` to choose an ordering.
- `print_stats(...)` to print a focused report.
- `print_callers(...)` to inspect who calls a function.
- `print_callees(...)` to inspect what a function calls.

## 48. `strip_dirs()`

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.runcall(lambda: sum(range(10_000)))

stats = pstats.Stats(profiler)
stats.strip_dirs()
stats.print_stats(5)
```

`strip_dirs()` removes leading path information from filenames in the displayed stats, making reports easier to scan. It mutates the `Stats` object.

## 49. `sort_stats()`

```python
import cProfile
import pstats

def work():
    return sum(i * i for i in range(10_000))

profiler = cProfile.Profile()
profiler.runcall(work)

stats = pstats.Stats(profiler)
stats.sort_stats("tottime")
stats.print_stats(5)
```

Sort by `tottime` when you want to investigate self-time. Use `cumtime` when you want to investigate total time through a call path.

## 50. `print_stats()`

```python
import cProfile
import pstats

def work():
    return sum(i * i for i in range(10_000))

profiler = cProfile.Profile()
profiler.runcall(work)

pstats.Stats(profiler).sort_stats("cumulative").print_stats(10)
```

Passing a numeric limit such as `10` focuses the report on the first rows after sorting. Focused output is often easier to reason about than an unfiltered wall of statistics.

## 51. `print_callers()`

```python
import cProfile
import pstats

def child():
    return sum(range(5_000))

def parent():
    return child()

profiler = cProfile.Profile()
profiler.runcall(parent)

stats = pstats.Stats(profiler)
stats.print_callers("child")
```

`print_callers()` helps answer: “Who calls this function?” That can reveal that a slow function is invoked from an unexpected path or repeated far more often than intended.

## 52. `print_callees()`

```python
import cProfile
import pstats

def child():
    return sum(range(5_000))

def parent():
    return child()

profiler = cProfile.Profile()
profiler.runcall(parent)

stats = pstats.Stats(profiler)
stats.print_callees("parent")
```

`print_callees()` helps answer: “What does this function call?” It is useful for breaking down cumulative time.

## 53. Understanding Caller/Callee Relationships

Think of a call graph as a tree:

```text
main()
 └── process_data()
      ├── parse()
      └── save()
```

`print_callers()` moves upward from a function to its callers. `print_callees()` moves downward to the functions it invokes.

A useful question is not simply “what is slow?” but:

> “Which call path causes this expensive function to execute so often?”

## 54. Profiling Function Calls

```python
import cProfile
import pstats

def normalize(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values]

def score(values: list[str]) -> int:
    return sum(len(value) for value in values)

def pipeline(values: list[str]) -> int:
    normalized = normalize(values)
    return score(normalized)

values = [" Alpha ", " Beta ", " Gamma "] * 10_000

profiler = cProfile.Profile()
profiler.runcall(pipeline, values)

pstats.Stats(profiler).sort_stats("cumulative").print_stats(15)
```

Profile the whole meaningful function boundary first. If the profile says `score()` contributes little and `normalize()` dominates, optimize neither blindly: inspect why normalization costs so much, verify the workload, then decide whether the improvement is valuable.

## 55. Profiling a Real Python Program

A useful profiling session has three artifacts in your reasoning, even if the artifacts are not saved to disk:

1. **Baseline** — what the program currently does.
2. **Profile evidence** — where time appears to go.
3. **Hypothesis** — one concrete explanation you can test.

Avoid starting with a code edit. A profiler is most useful when it answers a question you already care about.

## 56. Profiling CLI Programs

```python
import cProfile

def main() -> int:
    total = sum(i * i for i in range(100_000))
    print(total)
    return 0

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    exit_code = main()
    profiler.disable()
    profiler.print_stats(sort="cumulative")
    raise SystemExit(exit_code)
```

This pattern lets the real CLI entry point run under the profiler. In a normal run, the profiler wrapper can be omitted. In larger applications, it is often cleaner to keep profiling activation in a command-line or development-only path rather than changing the business logic.

## 57. Profiling Data Processing Code

```python
import cProfile
import pstats

def parse(rows: list[str]) -> list[int]:
    return [int(row) for row in rows]

def transform(values: list[int]) -> list[int]:
    return [value * value for value in values]

def aggregate(values: list[int]) -> int:
    return sum(values)

def pipeline(rows: list[str]) -> int:
    values = parse(rows)
    values = transform(values)
    return aggregate(values)

rows = [str(i) for i in range(50_000)]

profiler = cProfile.Profile()
profiler.runcall(pipeline, rows)
pstats.Stats(profiler).sort_stats("cumulative").print_stats(20)
```

Use realistic data sizes. Profiling ten rows can hide bottlenecks that appear when processing fifty thousand or five million rows.

## 58. Profiling I/O-Bound Code

```python
import cProfile
import time

def wait_for_input() -> None:
    time.sleep(0.05)

def main() -> None:
    wait_for_input()

profiler = cProfile.Profile()
profiler.runcall(main)
profiler.print_stats(sort="cumulative")
```

A deterministic profiler can show that time is associated with the waiting call, but it cannot tell you every detail of the external system causing real-world I/O latency. For network and database work, instrument the I/O boundary and measure the external operation separately where possible.

## 59. Profiling CPU-Bound Code

```python
import cProfile
import pstats

def cpu_bound(size: int) -> int:
    total = 0
    for value in range(size):
        total += value * value
    return total

profiler = cProfile.Profile()
profiler.runcall(cpu_bound, 1_000_000)
pstats.Stats(profiler).sort_stats("tottime").print_stats(10)
```

When CPU work dominates, algorithm choice, repeated Python-level loops, avoidable conversions, and data structures become plausible optimization hypotheses.

## 60. Memory Measurement

CPU profiling and memory measurement are different activities. A function can be CPU-cheap while allocating large objects. Another function can be fast but retain data for a long time.

Memory questions include:

- Where are allocations coming from?
- Is current traced memory growing?
- What allocations differ between two points?
- Is a new implementation reducing memory or merely moving it elsewhere?

## 61. Why CPU Profiling Is Not Memory Profiling

`cProfile` tells you about function execution statistics. It does not provide a complete picture of process resident memory or every allocation made outside Python's traced allocation mechanisms.

Use a memory-specific tool when the question is memory-specific. The standard library's `tracemalloc` module tracks Python memory allocations and can compare snapshots, but it should not be presented as a complete replacement for operating-system-level memory metrics.

## 62. `tracemalloc`

`tracemalloc` traces memory allocations made by Python. It can record current and peak traced memory and produce snapshots that show where traced allocations came from.

## 63. `tracemalloc.start()`

```python
import tracemalloc

tracemalloc.start()

data = [str(i) for i in range(50_000)]

current, peak = tracemalloc.get_traced_memory()
print(f"current={current:,} bytes")
print(f"peak={peak:,} bytes")

tracemalloc.stop()
```

Call `start()` before the workload whose allocations you want to observe. The amount of traceback information stored can affect overhead; use the smallest useful scope for the investigation.

## 64. `tracemalloc.stop()`

```python
import tracemalloc

tracemalloc.start()
values = [i for i in range(10_000)]

current, peak = tracemalloc.get_traced_memory()
print(current, peak)

tracemalloc.stop()
```

`stop()` stops tracing and discards the traced allocation history. It is useful when a measurement phase is complete and you do not want tracing overhead to affect subsequent work.

## 65. `tracemalloc.take_snapshot()`

```python
import tracemalloc

tracemalloc.start()

before = tracemalloc.take_snapshot()
values = [str(i) for i in range(20_000)]
after = tracemalloc.take_snapshot()

top = after.compare_to(before, "lineno")

for stat in top[:5]:
    print(stat)

tracemalloc.stop()
```

A snapshot captures the current traced allocation state. Comparing two snapshots can identify where traced allocations increased, decreased, or changed.

## 66. `tracemalloc.get_traced_memory()`

```python
import tracemalloc

tracemalloc.start()

values = [bytearray(100) for _ in range(2_000)]
current, peak = tracemalloc.get_traced_memory()

print(f"current={current:,}")
print(f"peak={peak:,}")

tracemalloc.stop()
```

The function returns the current and peak size of traced memory. It is useful for quick allocation/peak checks around a workload.

## 67. `tracemalloc.reset_peak()`

```python
import tracemalloc

tracemalloc.start()

small = [bytearray(100) for _ in range(1_000)]
_, first_peak = tracemalloc.get_traced_memory()

tracemalloc.reset_peak()

larger = [bytearray(100) for _ in range(2_000)]
_, second_peak = tracemalloc.get_traced_memory()

print(first_peak, second_peak)

tracemalloc.stop()
```

`reset_peak()` resets the peak counter while leaving tracing enabled. That makes it useful for measuring the next phase independently.

## 68. `tracemalloc.get_tracemalloc_memory()`

```python
import tracemalloc

tracemalloc.start()

values = [str(i) for i in range(1_000)]
overhead = tracemalloc.get_tracemalloc_memory()

print(f"tracemalloc_overhead={overhead:,} bytes")

tracemalloc.stop()
```

This reports memory used internally by the tracing machinery. It is useful when understanding profiler overhead, not as a substitute for total process memory measurement.

## 69. `Snapshot`

```python
import tracemalloc

tracemalloc.start()
values = [str(i) for i in range(5_000)]

snapshot = tracemalloc.take_snapshot()
print(type(snapshot).__name__)

tracemalloc.stop()
```

A `Snapshot` is an allocation snapshot that can be filtered, summarized, and compared with another snapshot.

## 70. `Snapshot.compare_to()`

```python
import tracemalloc

tracemalloc.start()

before = tracemalloc.take_snapshot()
values = [str(i) for i in range(10_000)]
after = tracemalloc.take_snapshot()

differences = after.compare_to(before, "lineno")

for difference in differences[:5]:
    print(difference)

tracemalloc.stop()
```

`compare_to()` produces `StatisticDiff` entries describing differences between snapshots, grouped according to the key you choose.

## 71. `Snapshot.statistics()`

```python
import tracemalloc

tracemalloc.start()

values = [str(i) for i in range(10_000)]
snapshot = tracemalloc.take_snapshot()

stats = snapshot.statistics("lineno")
for stat in stats[:5]:
    print(stat)

tracemalloc.stop()
```

`statistics()` groups traced allocation data into `Statistic` objects. Grouping by `lineno` is a useful starting point for source-level investigation.

## 72. `Statistic`

A `Statistic` describes grouped allocation information such as the size, count, and traceback/location represented by that group. Treat it as evidence about traced Python allocations, not a complete map of process memory.

## 73. `StatisticDiff`

A `StatisticDiff` represents the difference between two snapshots. It helps answer “what changed between these two points?” rather than merely “what exists now?”

## 74. `tracemalloc` Filters

```python
import tracemalloc

tracemalloc.start()

values = [str(i) for i in range(5_000)]
snapshot = tracemalloc.take_snapshot()

filtered = snapshot.filter_traces((
    tracemalloc.Filter(True, __file__),
))

print("filtered traces:", len(filtered.traces))

tracemalloc.stop()
```

A filter can focus a snapshot on traces matching filename or other supported criteria. Filtering is especially useful in larger programs where library allocations create noise. For a learning example, the important idea is that a snapshot can be narrowed before analysis.

## 75. Finding Memory Growth

```python
import tracemalloc

def build_values() -> list[str]:
    return [str(i) for i in range(20_000)]

tracemalloc.start()

before = tracemalloc.take_snapshot()
values = build_values()
after = tracemalloc.take_snapshot()

for difference in after.compare_to(before, "lineno")[:10]:
    print(difference)

tracemalloc.stop()
```

A growth report is useful for finding changed allocation sites. It does not prove that a memory leak exists; temporary allocations can also appear as growth between two snapshots.

## 76. Understanding Allocations vs Current Memory

A high allocation count does not automatically mean high retained memory. A program can allocate many short-lived objects and still have modest current memory. Conversely, a smaller number of long-lived objects can hold substantial memory.

Ask two separate questions:

```text
How much allocation activity occurred?
How much traced memory remains?
```

For a full process-memory picture, use operating-system or runtime-level monitoring in addition to `tracemalloc`.

## 77. CPU Bottleneck vs Memory Bottleneck

| Question | Useful first action |

| --- | --- |

| Which functions consume execution time? | Run `cProfile` and inspect `pstats`. |

| How long does this tiny operation take? | Use `timeit`. |

| Where are traced Python allocations increasing? | Compare `tracemalloc` snapshots. |

| What is total process RSS? | Use an appropriate OS/process measurement tool in the environment. |

## 78. Time/Space Trade-offs

An optimization can reduce time while increasing memory. For example, precomputing a lookup structure may avoid repeated work but consume additional memory.

A production decision therefore considers:

```text
time
+
memory
+
complexity
+
correctness
+
operational cost
```

Do not call a change an improvement until the relevant constraints are considered.

## 79. Profiling and Data Structures

```python
import timeit

data = list(range(100_000))
lookup = set(data)

def list_membership() -> bool:
    return 99_999 in data

def set_membership() -> bool:
    return 99_999 in lookup

print("list:", timeit.repeat(list_membership, number=10_000, repeat=5))
print("set :", timeit.repeat(set_membership, number=10_000, repeat=5))
```

The benchmark illustrates a data-structure choice, but it should not be interpreted as a universal result for all membership workloads. Input distribution, object type, cache behavior, and setup can change practical performance.

## 80. Profiling Loops

```python
import cProfile
import pstats

def loop_work(values):
    total = 0
    for value in values:
        total += value * value
    return total

values = list(range(200_000))

profiler = cProfile.Profile()
profiler.runcall(loop_work, values)

pstats.Stats(profiler).sort_stats("tottime").print_stats(10)
```

A loop is not automatically a problem. Measure its contribution to total runtime and ask whether an algorithmic or data-structure change could remove work rather than merely making each iteration slightly faster.

## 81. Profiling Function Calls

```python
import cProfile
import pstats

def tiny(value):
    return value + 1

def repeated(values):
    return [tiny(value) for value in values]

values = list(range(100_000))

profiler = cProfile.Profile()
profiler.runcall(repeated, values)
pstats.Stats(profiler).sort_stats("ncalls").print_stats(10)
```

High call counts can reveal call-overhead opportunities, but call count alone does not establish that call overhead is the dominant cost.

## 82. Profiling Serialization

```python
import cProfile
import json
import pstats

data = [{"id": i, "value": i * 2} for i in range(20_000)]

def serialize() -> str:
    return json.dumps(data, separators=(",", ":"))

profiler = cProfile.Profile()
profiler.runcall(serialize)

pstats.Stats(profiler).sort_stats("cumulative").print_stats(15)
```

Serialization is a common place to measure in data pipelines because it sits at the boundary between in-memory structures and external representation.

## 83. Profiling File Processing

```python
import cProfile
import io
import pstats

def process_file(stream: io.TextIOBase) -> int:
    total = 0
    for line in stream:
        total += len(line.strip())
    return total

content = "\n".join(f"record-{i}" for i in range(50_000))
stream = io.StringIO(content)

profiler = cProfile.Profile()
profiler.runcall(process_file, stream)

pstats.Stats(profiler).sort_stats("cumulative").print_stats(15)
```

Use an in-memory stream when you are testing parsing logic and do not want physical disk variability to dominate the benchmark. Then measure real disk behavior separately when storage performance itself is the question.

## 84. Profiling JSON/CSV Processing

```python
import cProfile
import csv
import io
import json
import pstats

records = [{"id": i, "value": i * 2} for i in range(10_000)]

def json_round_trip() -> int:
    text = json.dumps(records)
    loaded = json.loads(text)
    return len(loaded)

def csv_round_trip() -> int:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["id", "value"])
    writer.writeheader()
    writer.writerows(records)

    buffer.seek(0)
    reader = csv.DictReader(buffer)
    return sum(1 for _ in reader)

for func in (json_round_trip, csv_round_trip):
    profiler = cProfile.Profile()
    profiler.runcall(func)
    print(f"--- {func.__name__} ---")
    pstats.Stats(profiler).sort_stats("cumulative").print_stats(8)
```

This example compares workload shapes, not general format superiority. JSON and CSV solve different data representation needs, so correctness and interoperability remain part of the decision.

## 85. Profiling API/Network-Adjacent Code

```python
import cProfile
import time

def external_call_simulation() -> str:
    time.sleep(0.02)
    return "ok"

def pipeline() -> str:
    payload = {"prompt": "hello"}
    _ = payload
    return external_call_simulation()

profiler = cProfile.Profile()
profiler.runcall(pipeline)
profiler.print_stats(sort="cumulative")
```

The simulated wait shows why local CPU optimization may have little impact when most latency comes from waiting on a remote operation. In real systems, instrument the boundary so you can separate local preparation time, waiting time, response parsing, and persistence.

## 86. Measuring Before and After

Never stop at “the new code looks faster.” Run the same meaningful workload before and after the change.

A useful record is:

```text
workload
environment
baseline metric
profile evidence
hypothesis
change
functional-test result
post-change metric
variance
decision
```

## 87. Establishing a Baseline

```python
import timeit

def baseline(values):
    total = 0
    for value in values:
        total += value * 2
    return total

values = list(range(10_000))

times = timeit.repeat(lambda: baseline(values), number=1_000, repeat=5)
print("baseline_times=", times)
print("baseline_min=", min(times))
```

The baseline is not “the truth about runtime.” It is a documented measurement under defined conditions. The same measurement procedure should be applied after the change.

## 88. Defining a Performance Hypothesis

A hypothesis should connect evidence to a proposed change.

Weak:

> “I will use a clever one-liner.”

Strong:

> “The profile shows repeated linear membership checks consuming substantial cumulative time. Reusing a set for repeated membership queries may reduce the lookup work while preserving the same results.”

The strong statement is testable.

## 89. Making One Meaningful Change

```python
def baseline(values, target):
    found = 0
    for _ in range(100):
        for value in values:
            if value == target:
                found += 1
    return found

def candidate(values, target):
    lookup = set(values)
    found = 0
    for _ in range(100):
        if target in lookup:
            found += 1
    return found
```

The optimization changes a data structure strategy while preserving the logical question. A real investigation would benchmark both and add correctness tests before accepting the change.

## 90. Re-running the Measurement

```python
import timeit

values = list(range(10_000))
target = 9_999

def baseline():
    found = 0
    for _ in range(100):
        for value in values:
            if value == target:
                found += 1
    return found

lookup = set(values)

def candidate():
    found = 0
    for _ in range(100):
        if target in lookup:
            found += 1
    return found

before = timeit.repeat(baseline, number=100, repeat=5)
after = timeit.repeat(candidate, number=100, repeat=5)

print("before:", before)
print("after :", after)
```

## 91. Comparing Results

```python
before = 1.42
after = 1.11

improvement = (before - after) / before * 100
print(f"improvement={improvement:.1f}%")
```

This arithmetic is valid for those example numbers, but the numbers themselves are illustrative. In a real benchmark, compute the comparison from repeated measurements and include the workload and environment in the report.

A useful interpretation asks:

- Is the change large relative to variance?
- Is correctness unchanged?
- Did memory usage worsen?
- Did code complexity increase materially?
- Does the workload match production?

## 92. Statistical Noise and Variance

```python
import statistics

samples = [1.02, 1.05, 1.01, 1.08, 1.03]

print(f"mean={statistics.mean(samples):.4f}")
print(f"median={statistics.median(samples):.4f}")
print(f"stdev={statistics.stdev(samples):.4f}")
```

Variance is information. If two versions differ by 1% while the benchmark naturally varies by 5%, the evidence is weak.

For small benchmark sets, descriptive statistics are often enough for a first engineering pass. Larger performance studies need stronger experimental design and statistical analysis than this chapter attempts to teach.

## 93. Regression Detection

A performance regression is a meaningful deterioration after a code change.

Functional tests can all pass while a regression exists:

```text
behavior: correct
runtime: worse
memory: worse
```

Performance checks should therefore be treated as a separate test dimension when a project has a meaningful performance budget.

```python
def within_budget(measured_seconds: float, budget_seconds: float) -> bool:
    return measured_seconds <= budget_seconds

measured = 1.85
budget = 2.0

assert within_budget(measured, budget)
```

This is a simple conceptual budget check, not a reliable CI benchmark by itself. Timing-based tests need careful tolerance and environment control.

## 94. Optimization Decision-Making

| Question | Why it matters |

| --- | --- |

| Did the target metric improve? | Optimization must solve the stated problem. |

| Is correctness preserved? | A faster wrong result is not an improvement. |

| Is the change robust? | Fragile gains may disappear under realistic workloads. |

| Did memory usage change? | Time and space can trade off. |

| Did complexity rise? | Maintenance has a real engineering cost. |

| Does the gain matter? | A tiny local gain may have no system-level effect. |

## 95. Premature Optimization

Premature optimization means changing implementation details for performance before understanding whether the change is necessary or where the actual cost lies.

The problem is not optimization itself. The problem is optimizing without enough information.

The disciplined alternative is:

```text
make it correct
→ make the workload measurable
→ find the bottleneck
→ optimize the bottleneck
```

## 96. Micro-optimization

Micro-optimization changes small implementation details to reduce tiny amounts of work. Sometimes this is valuable—especially inside code that executes enormous numbers of times—but it should follow evidence.

Do not spend an hour removing a small allocation if profiling shows a database call consumes 95% of the end-to-end latency.

## 97. Readability vs Performance

```python
def normalize(values):
    return [value.strip().lower() for value in values]
```

Compact code is not automatically faster, and verbose code is not automatically slower. Choose the clearest correct implementation first. When profiling identifies the function as important, compare alternatives using the same workload.

## 98. Maintainability vs Performance

A change may reduce runtime but increase cognitive load, code paths, testing burden, or operational risk.

A production decision should consider:

```text
performance benefit
vs
complexity cost
```

A 2% gain from a fragile trick may be less valuable than a straightforward 20% gain from a better algorithm.

## 99. Correctness Before Performance

Functional correctness is a prerequisite to accepting performance work.

A reliable workflow is:

```text
baseline correctness
→ baseline performance
→ optimization
→ correctness tests
→ performance measurement
```

Never allow an optimization to silently change semantics just because the benchmark improved.

## 100. Performance Budgets

A performance budget is a stated limit or target tied to a real workload.

Examples:

- CLI finishes the daily dataset inside the operational window.
- Pipeline processes at least a defined number of records per minute.
- Memory remains below a defined ceiling on the production-sized dataset.
- Evaluation completes before a scheduled downstream task begins.

A budget should specify the workload, environment, metric, and acceptable tolerance. “Fast” is not a budget.

## 101. Performance Regression Tests

Performance regression testing should be designed carefully. CI machines are shared and variable, so a naive assertion such as “this function must always complete in 10 ms” can be flaky.

Prefer tests that validate broad budgets on sufficiently large workloads, use tolerances, and are supplemented by dedicated benchmark runs for more sensitive comparisons.

```python
def performance_budget_ok(seconds: float) -> bool:
    return seconds < 3.0

measured_seconds = 2.4
assert performance_budget_ok(measured_seconds)
```

## 102. Production Performance Measurement

Production measurement focuses on real workloads without turning every process into a heavily instrumented laboratory.

Useful production metrics can include:

- job duration;
- records processed;
- throughput;
- failure count;
- queue or wait time;
- batch sizes;
- memory peaks where measurable;
- selected phase durations.

Use the least expensive measurement that answers the operational question.

## 103. Logging Performance Metrics Safely

```python
import logging
import time

logger = logging.getLogger(__name__)

def process(values):
    start = time.perf_counter()
    result = sum(values)
    elapsed = time.perf_counter() - start

    logger.info(
        "processing_complete item_count=%d elapsed_seconds=%.6f",
        len(values),
        elapsed,
    )
    return result
```

The log records useful operational evidence without dumping the data itself. In production, avoid logging sensitive payloads merely to measure performance.

## 104. Profiling in Development vs Production

Development profiling is usually the easiest place to use deterministic instrumentation. Production profiling requires stronger care because profiling overhead can alter runtime and because capturing detailed call information may have operational or privacy implications.

A practical strategy is:

```text
development
→ detailed profiling

staging
→ representative workload profiling

production
→ lightweight metrics / targeted diagnostics
```

Use heavier profiling in production only when its diagnostic value justifies the operational cost and risk.

## 105. Sampling vs Deterministic Profiling — Conceptual Overview

Deterministic profiling records execution events so it can attribute work to function calls. Sampling profilers instead take periodic observations of where execution is occurring.

At this level, remember:

- deterministic profiling is detailed but adds instrumentation overhead;
- sampling can have a lighter impact and can be useful for production diagnosis;
- neither should be treated as an oracle.

The standard library tools in this chapter emphasize deterministic profiling.

## 106. Profiling Overhead

Instrumentation takes time. A profiler can make a program run differently from its unprofiled form.

Therefore:

```text
profiled runtime
≠
production runtime
```

The profile is primarily diagnostic evidence: “this path accounts for a large share of work under this instrumented run.”

## 107. Why Profilers Can Change Program Behavior

- Function-call instrumentation adds work.
- Timing changes can affect scheduling and interaction with I/O.
- Memory tracing adds bookkeeping overhead.
- Profiler output itself can consume time and memory.

> **Production Note:** Use profiling to identify where to investigate. After optimizing, re-run the unprofiled workload or the appropriate benchmark to measure actual performance improvement.

## 108. Benchmark Environment Control

Document the conditions that influence results:

- Python implementation and version;
- operating system;
- machine/CPU context;
- input size and shape;
- configuration;
- whether the machine is under load;
- whether the benchmark includes startup/import/setup time.

You do not need a laboratory-perfect environment for every engineering task. You do need enough control to make the comparison meaningful.

## 109. Warm-up Effects

The first execution may differ because of imports, caches, allocation state, file caches, or other initialization work. Python does not have the exact same JIT warm-up model as some JIT-compiled runtimes, but “warm-up” is still a useful broad term for startup and state effects.

When benchmarking a steady-state operation, separate initialization from the measured region.

## 110. Cache Effects

Repeated operations can interact with CPU and memory caches, filesystem caches, or application-level caches. That means a repeated local benchmark may be intentionally measuring warm-cache behavior.

Decide which question matters:

```text
cold-start behavior
or
steady-state behavior
```

Then design the measurement accordingly.

## 111. Garbage Collection Effects

Python memory-management activity can affect timing. A benchmark that creates many temporary objects may experience different allocation and garbage-collection behavior across runs.

Do not disable garbage collection just to make a benchmark look cleaner unless you can explain why the resulting workload is representative of the production question.

## 112. System Load

A benchmark running alongside editors, browsers, builds, containers, or other workloads can vary. Shared CPU and I/O resources introduce noise.

When the performance difference is small, reduce unrelated load or repeat the measurement enough to determine whether the difference persists.

## 113. CPU Frequency and Scheduling Effects

Modern systems dynamically change CPU frequency. Operating-system scheduling also moves time between processes and threads.

This is another reason benchmark values should be treated as measurements under conditions rather than fixed constants.

## 114. I/O Variability

Disk, filesystem cache state, storage hardware, and network conditions can change results. A benchmark that reads a file from memory cache is answering a different question from one measuring a cold storage read.

For I/O-heavy systems, separate compute timing from I/O timing when that makes the bottleneck clearer.

## 115. Benchmarking Database/Network Operations

Database and network operations are often dominated by external waiting, not Python execution. Microbenchmarks of the local Python wrapper can therefore be misleading.

Measure both:

```text
local preparation
+
external operation latency
+
response parsing
+
persistence
```

When you cannot control the external system, record enough context to understand the measurement's variability.

## 116. Measuring the Wrong Thing

A benchmark can be perfectly accurate and still answer the wrong question.

Examples:

- Measuring list construction when the production problem is parsing.
- Measuring JSON serialization without measuring the write that follows it.
- Benchmarking one record while production processes millions.
- Measuring a cached database query when production is mostly uncached.

Before writing benchmark code, write one sentence:

> “This measurement exists to answer ______.”

## 117. Common Profiling Mistakes

- Profiling a workload that is too small to resemble production.
- Optimizing the first suspicious function instead of the biggest measured contributor.
- Reading `ncalls` without considering time.
- Reading `cumtime` without inspecting child calls.
- Treating profiler numbers as production-latency guarantees.
- Measuring memory allocations while forgetting total process memory.
- Making multiple unrelated changes before re-measuring.

## 118. Anti-Patterns

| Anti-pattern | Why it is dangerous | Better approach |

| --- | --- | --- |

| Optimize before measuring | May solve the wrong problem | Measure first |

| Time once | High noise can dominate | Repeat |

| Benchmark setup + target together | Misleading result | Isolate target |

| Ignore input size | Results may not scale | Use realistic workloads |

| Trust one benchmark number | Environment varies | Compare repeated measurements |

| Optimize for fewer lines | Code size ≠ runtime | Measure |

| Sacrifice readability blindly | Maintenance cost | Justify with evidence |

| Ignore memory | CPU may improve while memory worsens | Measure both when relevant |

| Assume Big-O tells everything | Constants and workload matter | Combine analysis + measurement |

| Treat profiler output as perfect truth | Profiling has overhead | Interpret diagnostically |

## 119. Applied AI Engineering Examples

Applied AI systems contain many boundaries where measurement helps separate local Python work from expensive or variable external operations.

### Data preprocessing

A document or dataset pipeline might look like:

```text
CSV/JSON
→ parsing
→ cleaning
→ transformation
→ batching
```

Profile local Python phases. Measure representative input sizes. If parsing is dominant, optimize parsing. If an external inference call dominates, local loop micro-optimizations are unlikely to move end-to-end latency much.

```python
import time

def preprocess(records):
    start = time.perf_counter()
    cleaned = [record.strip().lower() for record in records if record.strip()]
    elapsed = time.perf_counter() - start
    print(f"preprocess_seconds={elapsed:.6f}")
    return cleaned

records = ["  Document A  ", "", "Document B  "] * 10_000
preprocessed = preprocess(records)
print(len(preprocessed))
```

### Embedding pipeline

For an embedding pipeline, measure the stages separately:

```text
load documents
→ chunk
→ normalize
→ embedding request
→ store
```

Stable stage boundaries let you distinguish local preprocessing from external embedding latency. Benchmark the local stages; measure the service boundary as an integration metric.

### LLM batch processing

A batch inference pipeline may be:

```text
load inputs
→ validate
→ prompt construction
→ model request
→ response parsing
→ persistence
```

The important lesson is not that one stage is always slow. It is that the pipeline should expose enough measurements to prove which stage is consuming the budget.

### Retrieval pipeline

For retrieval:

```text
query
→ embedding
→ vector search
→ reranking
→ prompt construction
```

Measure each stage if the end-to-end latency is too high. A single end-to-end stopwatch tells you there is a problem; phase measurements help localize it.

### Evaluation pipeline

Evaluation commonly has:

```text
load dataset
→ inference
→ scoring
→ aggregation
→ report
```

Throughput and total runtime matter for batch work. Memory measurement matters if the evaluator loads the entire dataset or retains large intermediate results.

## 120. Production Workflow

Use this workflow whenever performance becomes a real engineering concern:

```text
1. Define the performance goal.
2. Choose the workload.
3. Establish a baseline.
4. Measure end-to-end duration.
5. Profile the meaningful scope.
6. Identify the bottleneck.
7. Form one testable hypothesis.
8. Make one meaningful change.
9. Run correctness tests.
10. Re-run the benchmark.
11. Compare results and variance.
12. Check memory and other trade-offs.
13. Decide whether the gain matters.
14. Keep or revert.
15. Document the decision.
```

**Key Takeaway:** The final proof is not “the code looks better.” The proof is that the measured workload improved in the desired dimension while correctness and acceptable engineering properties remained intact.

# Complete Production-Oriented Example

## 121. Exercises

Each exercise follows the learning loop: understand → predict → implement → test → inspect → explain.

### Beginner 1 — Measure elapsed time

**Problem**  
Use `time.perf_counter()` to measure a function that sums integers.

**Requirements**  
Keep setup outside the measured region.

**Hints**  
Use a start timestamp, run the function, subtract the second timestamp.

**Expected behavior**  
The program prints one elapsed duration and the computed result.

**Solution**

```python
print("Implement the exercise using the required tools and verify the expected behavior.")
```

**Explanation**  
The measurement shows one execution under the current conditions.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Beginner 2 — Compare two implementations

**Problem**  
Write two functions that compute the same result and time each one.

**Requirements**  
Use identical input and verify equal results.

**Hints**  
Use `timeit.repeat()` with the same `number` and `repeat`.

**Expected behavior**  
Both implementations return the same answer and produce comparable timing data.

**Solution**

```python
import timeit

data = list(range(10_000))

def loop_sum():
    total = 0
    for value in data:
        total += value
    return total

def builtin_sum():
    return sum(data)

assert loop_sum() == builtin_sum()

print(timeit.repeat(loop_sum, number=1_000, repeat=5))
print(timeit.repeat(builtin_sum, number=1_000, repeat=5))
```

**Explanation**  
A fair comparison keeps the workload constant.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Beginner 3 — Repeat manual measurements

**Problem**  
Measure a small function five times with `perf_counter()`.

**Requirements**  
Store each duration.

**Hints**  
Use a list comprehension around a timing helper.

**Expected behavior**  
Print all five durations.

**Solution**

```python
import time

def work():
    return sum(i * i for i in range(20_000))

samples = []
for _ in range(5):
    start = time.perf_counter()
    work()
    samples.append(time.perf_counter() - start)

print(samples)
```

**Explanation**  
Repeated results reveal variance.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Beginner 4 — Use `timeit.timeit()`

**Problem**  
Benchmark `sum(range(1000))` 10,000 times.

**Requirements**  
Measure only the target expression.

**Hints**  
Use `timeit.timeit(statement, number=...)`.

**Expected behavior**  
Print total and per-call time.

**Solution**

```python
import timeit

duration = timeit.timeit("sum(range(1000))", number=10_000)
print(duration)
print(duration / 10_000)
```

**Explanation**  
`timeit` is designed for small repeated benchmarks.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Beginner 5 — Identify CPU vs waiting

**Problem**  
Measure a loop and a `sleep()` operation with both wall and CPU clocks.

**Requirements**  
Compare the two time domains.

**Hints**  
Use `perf_counter()` and `process_time()`.

**Expected behavior**  
The sleeping function should show a larger wall/CPU difference than CPU work.

**Solution**

```python
import time

start_wall = time.perf_counter()
start_cpu = time.process_time()
sum(i * i for i in range(200_000))
cpu_wall = time.perf_counter() - start_wall
cpu_cpu = time.process_time() - start_cpu

start_wall = time.perf_counter()
start_cpu = time.process_time()
time.sleep(0.02)
wait_wall = time.perf_counter() - start_wall
wait_cpu = time.process_time() - start_cpu

print(cpu_wall, cpu_cpu)
print(wait_wall, wait_cpu)
```

**Explanation**  
You learn that wall and CPU time answer different questions.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Intermediate 6 — Design a fair benchmark

**Problem**  
Compare list membership with set membership for repeated lookups.

**Requirements**  
Build the set outside the benchmark.

**Hints**  
Benchmark with shared data and repeated runs.

**Expected behavior**  
Both functions must answer the same logical question.

**Solution**

```python
import timeit

data = list(range(10_000))
lookup = set(data)

def list_lookup():
    return 9_999 in data

def set_lookup():
    return 9_999 in lookup

assert list_lookup() == set_lookup()
print(timeit.repeat(list_lookup, number=10_000, repeat=5))
print(timeit.repeat(set_lookup, number=10_000, repeat=5))
```

**Explanation**  
The benchmark separates setup from lookup.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Intermediate 7 — Inspect `cProfile`

**Problem**  
Profile a pipeline containing parse, transform, and aggregate stages.

**Requirements**  
Use `pstats.Stats` and sort by cumulative time.

**Hints**  
Use `cProfile.Profile().runcall(...)`.

**Expected behavior**  
Print the top functions.

**Solution**

```python
import cProfile
import pstats

def parse(rows):
    return [int(row) for row in rows]

def transform(values):
    return [value * value for value in values]

def main():
    rows = [str(i) for i in range(20_000)]
    values = transform(parse(rows))
    return sum(values)

profiler = cProfile.Profile()
exit_code = 0
try:
    result = profiler.runcall(main)
    print(result)
except Exception:
    exit_code = 1
finally:
    pstats.Stats(profiler).sort_stats("cumulative").print_stats(15)

raise SystemExit(exit_code)
```

**Explanation**  
You practice bottleneck discovery.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Intermediate 8 — Inspect callers

**Problem**  
Create a function called from two different paths and inspect `print_callers()`.

**Requirements**  
Keep the workload deterministic.

**Hints**  
Use `pstats.Stats.print_callers()`.

**Expected behavior**  
The report identifies callers.

**Solution**

```python
import cProfile
import pstats

def target():
    return sum(range(2_000))

def caller_a():
    return target()

def caller_b():
    return target()

def main():
    return caller_a() + caller_b()

profiler = cProfile.Profile()
profiler.runcall(main)
pstats.Stats(profiler).print_callers("target")
```

**Explanation**  
You learn to trace why a function is executed.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Intermediate 9 — Inspect callees

**Problem**  
Profile a parent function that calls two children.

**Requirements**  
Use `print_callees()` after sorting.

**Hints**  
Use `pstats.Stats.print_callees()`.

**Expected behavior**  
The report shows the child relationships.

**Solution**

```python
import cProfile
import pstats

def child_a():
    return sum(range(1_000))

def child_b():
    return sum(i * i for i in range(1_000))

def parent():
    return child_a() + child_b()

profiler = cProfile.Profile()
profiler.runcall(parent)
pstats.Stats(profiler).print_callees("parent")
```

**Explanation**  
You learn to decompose cumulative time.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Intermediate 10 — Memory snapshot

**Problem**  
Use `tracemalloc` snapshots before and after creating a list of strings.

**Requirements**  
Compare by line.

**Hints**  
Use `start`, `take_snapshot`, `compare_to`, `stop`.

**Expected behavior**  
The changed allocation site appears in the statistics.

**Solution**

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()

values = [str(i) for i in range(20_000)]

after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:5]:
    print(stat)

tracemalloc.stop()
```

**Explanation**  
You learn the basic memory-investigation loop.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Intermediate 11 — Reset a memory peak

**Problem**  
Measure one allocation phase, reset the peak, then measure another phase.

**Requirements**  
Do not stop tracing between phases.

**Hints**  
Use `reset_peak()`.

**Expected behavior**  
Print two peak readings.

**Solution**

```python
import tracemalloc

tracemalloc.start()

first = [bytearray(100) for _ in range(500)]
_, first_peak = tracemalloc.get_traced_memory()

del first
tracemalloc.reset_peak()

second = [bytearray(100) for _ in range(1_000)]
_, second_peak = tracemalloc.get_traced_memory()

print(first_peak, second_peak)
tracemalloc.stop()
```

**Explanation**  
You learn phase-specific peak measurement.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 12 — Baseline report

**Problem**  
Create a small benchmark report containing workload, environment assumptions, and repeated measurements.

**Requirements**  
Do not invent universal claims.

**Hints**  
Use `platform.python_version()` plus `timeit.repeat()`.

**Expected behavior**  
The report states exactly what was measured.

**Solution**

```python
import platform
import timeit

data = list(range(100_000))

def workload():
    return sum(data)

print("python=", platform.python_version())
print("samples=", timeit.repeat(workload, number=100, repeat=5))
```

**Explanation**  
Performance evidence is contextual.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 13 — Hypothesis-driven optimization

**Problem**  
Profile a deliberately inefficient membership check and hypothesize a reusable lookup structure.

**Requirements**  
Preserve the result semantics.

**Hints**  
Use `cProfile`, then `timeit`.

**Expected behavior**  
Measure before and after.

**Solution**

```python
import cProfile
import pstats
import timeit

values = list(range(20_000))
target = 19_999

def baseline():
    return any(value == target for value in values)

lookup = set(values)

def candidate():
    return target in lookup

assert baseline() == candidate()

profiler = cProfile.Profile()
profiler.runcall(baseline)
pstats.Stats(profiler).sort_stats("cumulative").print_stats(10)

print(timeit.repeat(baseline, number=1_000, repeat=5))
print(timeit.repeat(candidate, number=1_000, repeat=5))
```

**Explanation**  
The workflow links profile evidence to the change.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 14 — Regression detector

**Problem**  
Write a budget check that accepts a range rather than a single exact runtime.

**Requirements**  
Keep the threshold realistic for the environment.

**Hints**  
Use a tolerance or broad budget.

**Expected behavior**  
The test explains that CI timing can be noisy.

**Solution**

```python
def within_budget(measured, budget, tolerance=0.10):
    return measured <= budget * (1 + tolerance)

measured = 1.05
budget = 1.00

assert within_budget(measured, budget)
```

**Explanation**  
You learn not to build brittle performance tests.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 15 — CPU vs memory trade-off

**Problem**  
Compare a streaming approach with a materialized list for a large logical sequence.

**Requirements**  
Measure both elapsed time and traced peak memory.

**Hints**  
Use `perf_counter()` plus `tracemalloc`.

**Expected behavior**  
Explain which resource improved and which changed.

**Solution**

```python
import tracemalloc
import time

def streaming(n):
    total = 0
    for i in range(n):
        total += i
    return total

def materialized(n):
    values = list(range(n))
    return sum(values)

for func in (streaming, materialized):
    tracemalloc.start()
    start = time.perf_counter()
    result = func(100_000)
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(func.__name__, result, elapsed, current, peak)
```

**Explanation**  
You practice multi-dimensional optimization.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 16 — I/O stage analysis

**Problem**  
Build a pipeline with local preprocessing, simulated waiting, and output formatting.

**Requirements**  
Time each phase separately.

**Hints**  
Use a small phase-timing helper.

**Expected behavior**  
The report shows which phase dominates.

**Solution**

```python
import time

def phase(name, func):
    start = time.perf_counter()
    result = func()
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed:.6f}s")
    return result

records = phase("preprocess", lambda: [str(i).strip() for i in range(20_000)])
phase("external_wait", lambda: time.sleep(0.02))
phase("format", lambda: ",".join(records))
```

**Explanation**  
You learn to avoid optimizing the wrong stage.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 17 — Profiling CLI

**Problem**  
Wrap a `main()` function with `cProfile.Profile` and preserve its exit code.

**Requirements**  
Do not embed profiler logic in business functions.

**Hints**  
Use `raise SystemExit(exit_code)`.

**Expected behavior**  
The CLI still returns its normal result.

**Solution**

```python
import cProfile
import pstats

def parse(rows):
    return [int(row) for row in rows]

def transform(values):
    return [value * value for value in values]

def main():
    rows = [str(i) for i in range(20_000)]
    values = transform(parse(rows))
    return sum(values)

profiler = cProfile.Profile()
exit_code = 0
try:
    result = profiler.runcall(main)
    print(result)
except Exception:
    exit_code = 1
finally:
    pstats.Stats(profiler).sort_stats("cumulative").print_stats(15)

raise SystemExit(exit_code)
```

**Explanation**  
Profiling should be separable from application logic.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 18 — Input-size scaling

**Problem**  
Benchmark the same algorithm at several input sizes and record runtime.

**Requirements**  
Keep the implementation unchanged.

**Hints**  
Use a small loop around `time.perf_counter()` or `timeit`.

**Expected behavior**  
Print size/runtime pairs.

**Solution**

```python
print("Implement the exercise using the required tools and verify the expected behavior.")
```

**Explanation**  
You connect complexity to empirical scaling.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 19 — Build an optimization decision memo

**Problem**  
Given before/after timings, memory usage, and added code complexity, write a keep/revert recommendation.

**Requirements**  
Do not optimize only for runtime.

**Hints**  
Compare all provided dimensions.

**Expected behavior**  
The decision states evidence and trade-offs.

**Solution**

```python
before_seconds = 2.0
after_seconds = 1.8
before_memory_mb = 100
after_memory_mb = 145
complexity_increased = True

print("runtime_change_percent:", (before_seconds - after_seconds) / before_seconds * 100)
print("memory_change_mb:", after_memory_mb - before_memory_mb)
print("complexity_increased:", complexity_increased)
```

**Explanation**  
You practice engineering judgment.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

### Advanced 20 — Applied AI pipeline investigation

**Problem**  
Design a measurement plan for a batch inference pipeline with preprocessing, external inference, parsing, and persistence.

**Requirements**  
Identify which stages need local benchmarks vs integration measurements.

**Hints**  
Separate phase timing from microbenchmarking.

**Expected behavior**  
Produce a stage-by-stage measurement plan.

**Solution**

```python
stages = [
    ("load", "time the data-loading phase"),
    ("preprocess", "benchmark local preprocessing separately"),
    ("inference", "measure external call latency as an integration metric"),
    ("parse", "time local response parsing"),
    ("persist", "time result persistence"),
]

for name, measurement in stages:
    print(f"{name}: {measurement}")
```

**Explanation**  
You practice applying the methodology to an AI workload.

**Common mistakes**  
Do not optimize before confirming what the measurement actually includes.

## 122. Debugging Scenarios

### Scenario 1 — “Python program is slow.”

**Problem:** The complaint has no defined metric or workload.

**How to Think:** Convert “slow” into a measurable statement. Identify workload, input size, environment, and acceptable target.

**Diagnosis:** Measure end-to-end duration first, then profile the meaningful execution path. Do not start by rewriting the first loop you notice.

**Solution:** Establish a baseline, inspect profile data, identify the dominant contributor, form a hypothesis, change one thing, and re-measure.

**Production Lesson:** A performance incident begins with measurement, not code editing.

### Scenario 2 — Function appears slow but another function dominates

**Problem:** A developer suspects `parse()` but the profile shows `save()` dominates cumulative time.

**How to Think:** The profile is evidence about the measured workload. Re-check the call path and determine whether the metric is local CPU time or end-to-end time.

**Diagnosis:** Inspect `cumtime`, `tottime`, callers, and callees. Then time the save phase separately if it is I/O-bound.

**Solution:** Investigate `save()` rather than optimizing `parse()` unless a separate measurement proves parsing matters.

**Production Lesson:** Optimize the bottleneck, not the most suspicious function.

### Scenario 3 — Benchmark changes every run

**Problem:** The same benchmark produces noticeably different times.

**How to Think:** Variability can come from scheduling, CPU frequency, caches, garbage collection, background load, or I/O.

**Diagnosis:** Repeat the benchmark, inspect the distribution, reduce unrelated load, and document conditions.

**Solution:** Compare repeated samples and ask whether the candidate improvement is larger than normal variance.

**Production Lesson:** Noise is part of the evidence.

### Scenario 4 — Optimized code is slower

**Problem:** A “faster” algorithm measures worse on the chosen workload.

**How to Think:** Check that the benchmark is fair, the result is correct, and the workload matches the optimization's assumptions.

**Diagnosis:** Confirm setup is outside the measured region when appropriate; compare representative input sizes and repeated measurements.

**Solution:** Revert the change if the evidence does not support it, or refine the hypothesis and test a different workload if a real scaling advantage is expected.

**Production Lesson:** An optimization label means nothing until measurement supports it.

### Scenario 5 — Runtime improved but memory increased

**Problem:** The new implementation is faster but uses substantially more memory.

**How to Think:** This is a time/space trade-off.

**Diagnosis:** Use `tracemalloc` for Python allocation differences and an appropriate process-memory metric for overall memory.

**Solution:** Decide using the actual memory budget and workload. Keep the change only if the new trade-off is acceptable.

**Production Lesson:** Performance has multiple dimensions.

### Scenario 6 — Millions of function calls appear in profile

**Problem:** One helper has a huge `ncalls` value.

**How to Think:** Call count is only one piece of evidence.

**Diagnosis:** Compare `ncalls`, `tottime`, `cumtime`, and per-call cost. A huge count with tiny total time may not matter.

**Solution:** Investigate only when the aggregate cost is material or when the call pattern suggests a higher-level algorithmic change.

**Production Lesson:** Frequency and cost must be considered together.

### Scenario 7 — CI benchmark is noisy

**Problem:** The same benchmark passes locally but fails intermittently in CI.

**How to Think:** CI machines may vary in CPU, load, virtualization, scheduling, and background activity.

**Diagnosis:** Inspect the magnitude of the threshold, repeat counts, workload size, and whether the test is too strict.

**Solution:** Use broad regression checks, dedicated benchmark jobs, or environment-controlled benchmark runs rather than fragile millisecond assertions.

**Production Lesson:** Functional CI tests and high-fidelity benchmarking are different activities.

## 123. Mini-Project — Python Performance Investigation CLI

**Project Goal**

Build a self-contained CLI-style investigation tool that runs a deterministic data-processing workload and reports baseline timing, repeated benchmark timing, a CPU profile, and optional memory measurements.

The project is deliberately educational. It uses standard-library tools and keeps the workload local so the measurements are understandable.

**Architecture**

```text
CLI / main()
   ↓
load workload
   ↓
baseline elapsed measurement
   ↓
timeit benchmark
   ↓
cProfile
   ↓
pstats inspection
   ↓
optional tracemalloc measurement
   ↓
optimization hypothesis
   ↓
optimized implementation
   ↓
functional verification
   ↓
before/after comparison
```

**Requirements**

- Use a realistic but deterministic dataset.
- Keep benchmark setup outside the measured operation when appropriate.
- Time the baseline with `perf_counter()` and `timeit`.
- Profile the meaningful pipeline with `cProfile`.
- Inspect results with `pstats`.
- Use `tracemalloc` when memory behavior is relevant.
- Make one meaningful optimization.
- Re-run correctness checks.
- Benchmark again under the same workload.
- Report before/after results as measurements under stated conditions.

```python
import cProfile
import pstats
import time
import timeit
import tracemalloc

def baseline(values):
    result = []
    for value in values:
        if value % 2 == 0:
            result.append(value * value)
    return result

def optimized(values):
    return [value * value for value in values if value % 2 == 0]

def measure(func, values):
    start = time.perf_counter()
    result = func(values)
    elapsed = time.perf_counter() - start
    return result, elapsed

def profile(func, values):
    profiler = cProfile.Profile()
    result = profiler.runcall(func, values)
    print(f"\nProfile: {func.__name__}")
    pstats.Stats(profiler).sort_stats("cumulative").print_stats(10)
    return result

def memory_measure(func, values):
    tracemalloc.start()
    tracemalloc.reset_peak()

    result = func(values)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, current, peak

def main():
    values = list(range(100_000))

    baseline_result, baseline_seconds = measure(baseline, values)
    optimized_result, optimized_seconds = measure(optimized, values)

    assert baseline_result == optimized_result

    baseline_times = timeit.repeat(
        lambda: baseline(values),
        number=10,
        repeat=5,
    )
    optimized_times = timeit.repeat(
        lambda: optimized(values),
        number=10,
        repeat=5,
    )

    profile(baseline, values)
    profile(optimized, values)

    _, baseline_current, baseline_peak = memory_measure(baseline, values)
    _, optimized_current, optimized_peak = memory_measure(optimized, values)

    print("\nMeasured comparison")
    print(f"baseline wall time:  {baseline_seconds:.6f}s")
    print(f"optimized wall time: {optimized_seconds:.6f}s")
    print(f"baseline timeit:     {baseline_times}")
    print(f"optimized timeit:    {optimized_times}")
    print(f"baseline memory:     current={baseline_current}, peak={baseline_peak}")
    print(f"optimized memory:    current={optimized_current}, peak={optimized_peak}")

if __name__ == "__main__":
    main()
```

**How to use the project**

1. Run the baseline and verify correctness.
2. Record the baseline measurements.
3. Read the profile instead of guessing.
4. Explain your optimization hypothesis in one paragraph.
5. Apply one change.
6. Run functional verification.
7. Repeat the benchmark with the same input.
8. Compare timing and memory.
9. Decide whether the improvement is meaningful.
10. Write a short decision note.

**Production Improvements**

A production system would usually separate benchmark code from application code, define representative workloads, capture environment metadata, avoid expensive profilers in normal runs, establish meaningful performance budgets, and retain benchmark results in a controlled performance-test workflow.

## 124. Interview Questions

### 1. What is profiling?

**How to Think:** Think about location, not just total runtime.

**Answer:** Profiling records execution statistics so you can identify where time or resources are being spent.

**Why It Matters:** It is the step between knowing there is a performance problem and knowing where to investigate.

### 2. Why measure before optimizing?

**How to Think:** Separate hypothesis from evidence.

**Answer:** Because developers commonly optimize code that is not the bottleneck.

**Why It Matters:** It reduces wasted work and makes optimization decisions defensible.

### 3. Difference between profiling and benchmarking?

**How to Think:** Ask what question each tool answers.

**Answer:** Benchmarking compares a defined operation under controlled conditions; profiling helps locate where a program spends execution time.

**Why It Matters:** Both are needed in different phases of investigation.

### 4. What is `time.perf_counter()`?

**How to Think:** Think elapsed duration.

**Answer:** A high-resolution performance counter intended for measuring elapsed durations; compare differences between readings.

**Why It Matters:** It is a standard choice for application timing.

### 5. Why not generally use `time.time()` for precise elapsed timing?

**How to Think:** Think wall-clock adjustments vs duration measurement.

**Answer:** `time.time()` represents wall-clock time; `perf_counter()` is designed for elapsed-duration measurement.

**Why It Matters:** The timer should match the measurement question.

### 6. What is `timeit`?

**How to Think:** Think controlled microbenchmarking.

**Answer:** A standard-library module designed to measure small pieces of Python code repeatedly.

**Why It Matters:** It helps reduce common benchmark mistakes.

### 7. Why repeat a benchmark?

**How to Think:** Think variance.

**Answer:** Repeated runs expose noise and make comparisons more trustworthy.

**Why It Matters:** One number can be an outlier.

### 8. What does `cProfile` do?

**How to Think:** Think function-call statistics.

**Answer:** It collects deterministic profiling data about function calls and timing.

**Why It Matters:** It helps identify likely time hotspots.

### 9. What is `tottime`?

**How to Think:** Think self-time.

**Answer:** Time spent in the function itself, excluding subcalls.

**Why It Matters:** It helps identify self-work.

### 10. What is `cumtime`?

**How to Think:** Think total call-path cost.

**Answer:** Time spent in the function plus its subcalls.

**Why It Matters:** It helps identify expensive call paths.

### 11. What is `ncalls`?

**How to Think:** Think frequency.

**Answer:** Number of calls recorded for a function.

**Why It Matters:** High frequency may matter, but only together with time cost.

### 12. What is `pstats`?

**How to Think:** Think profile analysis.

**Answer:** The standard-library module used to inspect and format profiler statistics.

**Why It Matters:** It lets you sort and focus the profile.

### 13. What is `tracemalloc`?

**How to Think:** Think Python allocation tracking.

**Answer:** A standard-library tool that traces Python memory allocations and supports snapshots and comparisons.

**Why It Matters:** It is useful for investigating allocation behavior.

### 14. How do you investigate memory growth?

**How to Think:** Think before/after snapshots.

**Answer:** Start tracing, take a baseline snapshot, run the workload, take a second snapshot, compare them, and interpret the changed allocation sites.

**Why It Matters:** It provides evidence about traced Python allocations.

### 15. CPU-bound vs I/O-bound?

**How to Think:** Ask whether the process is computing or waiting.

**Answer:** CPU-bound work spends substantial time consuming CPU; I/O-bound work spends substantial time waiting for external resources.

**Why It Matters:** The appropriate optimization strategy differs.

### 16. Why can Big-O and runtime measurements differ?

**How to Think:** Think scaling vs constants.

**Answer:** Big-O describes asymptotic growth, while measurements include constants, implementation, workload, and environment.

**Why It Matters:** Use both analytical and empirical reasoning.

### 17. What is premature optimization?

**How to Think:** Optimization before evidence.

**Answer:** Changing implementation for performance without first establishing a real performance problem or bottleneck.

**Why It Matters:** It increases complexity without a demonstrated benefit.

### 18. Why can profiling change program behavior?

**How to Think:** Think instrumentation overhead.

**Answer:** Profiling adds bookkeeping and can affect runtime and memory behavior.

**Why It Matters:** Profile data is diagnostic evidence rather than a production-latency guarantee.

### 19. How would you investigate a slow batch job?

**How to Think:** Start from the workload boundary.

**Answer:** Measure end-to-end time, profile representative execution, identify the bottleneck, form a hypothesis, optimize, test, and re-measure.

**Why It Matters:** It makes performance work repeatable.

### 20. How do you prove an optimization helped?

**How to Think:** Use the same experiment before and after.

**Answer:** Run equivalent workloads, collect repeated measurements, compare variance, verify correctness, and assess relevant trade-offs.

**Why It Matters:** The proof is empirical, not stylistic.

## 125. Architecture Questions

### 1. How would you profile a large batch inference pipeline?

**Structured Answer:** Define the end-to-end metric, measure stage boundaries, then profile local Python stages. Treat external model calls as integration measurements and avoid heavy production profiling unless justified.

### 2. How would you determine CPU-bound vs memory-bound vs I/O-bound?

**Structured Answer:** Measure wall time and CPU time, profile function costs, inspect memory allocation behavior, and measure key external waits. No single metric establishes all three.

### 3. How would you establish a baseline for an embedding pipeline?

**Structured Answer:** Specify document count, chunking policy, model/configuration assumptions, machine context, and stage metrics. Record repeated measurements for representative workloads.

### 4. How would you measure throughput in a document-processing system?

**Structured Answer:** Define a unit of useful work such as documents or records completed per second, then measure total completed work over a realistic batch and report the workload conditions.

### 5. How would you detect performance regressions?

**Structured Answer:** Define a meaningful performance budget or baseline, run controlled regression measurements, and keep thresholds tolerant enough to avoid flaky infrastructure-driven failures.

### 6. How would you decide whether an optimization is worth more code complexity?

**Structured Answer:** Compare measured benefit to operational requirements, memory effects, correctness risk, maintainability cost, and expected workload frequency.

### 7. How would you profile a pipeline with external API calls?

**Structured Answer:** Separate local preparation, network wait, response parsing, and persistence. Use end-to-end timing plus phase instrumentation rather than assuming local Python code dominates.

### 8. How would you distinguish application latency from external-service latency?

**Structured Answer:** Time the local code before and after the external call and measure the call boundary explicitly. Compare the parts against the total.

### 9. How would you measure memory growth in a long-running batch job?

**Structured Answer:** Use `tracemalloc` snapshots around representative phases, plus an OS/process-memory signal when total process memory matters.

### 10. How would you safely introduce performance optimization into production code?

**Structured Answer:** Start with a baseline and tests, isolate one bottleneck, make one change, validate correctness, run a controlled performance comparison, and deploy with a way to observe whether the intended metric improves.

## 126. Knowledge Check

Answer these without looking back first.

### 1. What does `perf_counter()` measure?

**Answer:** Elapsed time between readings using a performance counter.

### 2. Why can one timing run mislead you?

**Answer:** Scheduling, frequency changes, caches, GC, background load, and I/O can change the result.

### 3. What is the difference between benchmarking and profiling?

**Answer:** Benchmarking compares a defined operation under controlled repetition; profiling identifies where execution time is spent.

### 4. What does `tottime` exclude?

**Answer:** Time spent in subcalls.

### 5. What does `cumtime` include?

**Answer:** Time spent in the function and its subcalls.

### 6. Why is `ncalls` insufficient by itself?

**Answer:** Call count does not tell you the cost per call or total time.

### 7. What does `tracemalloc` track?

**Answer:** Python memory allocations that it is tracing; it is not the complete process-memory picture.

### 8. Why separate benchmark setup from the target?

**Answer:** Otherwise the result answers a different question and can hide the cost of the operation you actually care about.

### 9. Why can a better Big-O algorithm lose on small inputs?

**Answer:** Constant factors, setup overhead, implementation details, and workload shape can dominate at small sizes.

### 10. What is the evidence for an optimization?

**Answer:** A controlled before/after comparison showing the target metric improved while correctness and acceptable trade-offs are preserved.

### 11. A profile shows a function called one million times but 0.5% cumulative time. Should you optimize it immediately?

**Answer:** No. Call count alone does not make it the bottleneck.

### 12. A new implementation is 3% faster, but benchmark variance is 5%. Is the result conclusive?

**Answer:** No. The observed gain is smaller than normal variation, so stronger measurement is needed.

### 13. Why can a profiler make runtime measurements higher?

**Answer:** Instrumentation adds overhead.

### 14. Why should realistic input sizes matter?

**Answer:** Different algorithms and memory behaviors can change dramatically as workload size grows.

### 15. What is a performance budget?

**Answer:** A defined performance limit or target tied to a workload and environment.

## 127. Completion Checklist

## Completion Checklist

### Foundations
- [ ] I understand what performance means in software.
- [ ] I can distinguish latency and throughput.
- [ ] I understand elapsed wall-clock time.
- [ ] I understand CPU time.
- [ ] I understand peak memory and traced allocations.
- [ ] I understand scalability at a conceptual level.

### Measurement
- [ ] I can use `time.perf_counter()`.
- [ ] I understand why `time.time()` is not the general precision timer for elapsed benchmarks.
- [ ] I understand `time.process_time()`.
- [ ] I can measure a meaningful application phase.
- [ ] I know why one timing run is unreliable.

### Benchmarking
- [ ] I understand `timeit`.
- [ ] I can use `timeit.timeit()`.
- [ ] I can use `timeit.repeat()`.
- [ ] I can use `timeit.Timer`.
- [ ] I understand `timeit.default_timer`.
- [ ] I can separate setup from the target operation.
- [ ] I can control the workload.
- [ ] I can interpret variance instead of hiding it.

### Profiling
- [ ] I understand what a profiler does.
- [ ] I can run `python -m cProfile`.
- [ ] I can use `cProfile.Profile`.
- [ ] I understand `enable()`.
- [ ] I understand `disable()`.
- [ ] I understand `create_stats()`.
- [ ] I understand `print_stats()`.
- [ ] I understand `runcall()`.
- [ ] I understand `run()`.
- [ ] I understand `runctx()`.
- [ ] I can read `ncalls`.
- [ ] I can read `tottime`.
- [ ] I can read `cumtime`.
- [ ] I understand `percall`.
- [ ] I can identify `filename:lineno(function)`.
- [ ] I can use `pstats.Stats`.
- [ ] I can use `strip_dirs()`.
- [ ] I can use `sort_stats()`.
- [ ] I can use `print_stats()`.
- [ ] I can use `print_callers()`.
- [ ] I can use `print_callees()`.

### Memory
- [ ] I understand why CPU profiling is not memory profiling.
- [ ] I can use `tracemalloc.start()`.
- [ ] I can use `tracemalloc.stop()`.
- [ ] I can use `take_snapshot()`.
- [ ] I can use `get_traced_memory()`.
- [ ] I can use `reset_peak()`.
- [ ] I know what `get_tracemalloc_memory()` measures.
- [ ] I understand `Snapshot`.
- [ ] I can use `Snapshot.compare_to()`.
- [ ] I can use `Snapshot.statistics()`.
- [ ] I understand `Statistic` and `StatisticDiff`.
- [ ] I understand basic tracing filters.
- [ ] I know that traced Python allocations are not the same as total process memory.

### Optimization
- [ ] I can establish a baseline.
- [ ] I can form a performance hypothesis.
- [ ] I can change one meaningful thing.
- [ ] I can run correctness tests before accepting the optimization.
- [ ] I can measure again under the same workload.
- [ ] I can compare before and after.
- [ ] I can reason about statistical noise.
- [ ] I can detect a meaningful regression.
- [ ] I can weigh time, memory, complexity, and correctness.
- [ ] I understand premature optimization.
- [ ] I can explain why Big-O and benchmarking complement each other.

### Production / Applied AI
- [ ] I can investigate CPU-bound Python work.
- [ ] I can investigate I/O-heavy work.
- [ ] I can investigate Python allocation growth.
- [ ] I can profile data-processing pipelines.
- [ ] I can design measurements for embedding pipelines.
- [ ] I can design measurements for LLM batch processing.
- [ ] I can separate external-service latency from local application work.
- [ ] I understand profiling overhead.
- [ ] I can explain when detailed profiling belongs in development versus production.


# Final Mental Model

When someone says:

> “I think my Python program is slow.”

Do this:

```text
DEFINE THE PROBLEM
      ↓
CHOOSE THE WORKLOAD
      ↓
MEASURE END-TO-END
      ↓
PROFILE THE MEANINGFUL SCOPE
      ↓
IDENTIFY THE BOTTLENECK
      ↓
FORM A HYPOTHESIS
      ↓
MAKE ONE MEANINGFUL CHANGE
      ↓
RUN CORRECTNESS TESTS
      ↓
BENCHMARK AGAIN
      ↓
COMPARE VARIANCE + TRADE-OFFS
      ↓
KEEP OR REVERT
      ↓
DOCUMENT THE DECISION
```

The most important distinctions are:

```text
Measurement
= What happened?

Benchmark
= How does this operation perform under controlled repetition?

Profiler
= Where is execution time being spent?

Memory profiler
= Where is traced memory being allocated or changing?

Optimization
= A change intended to improve a measured performance characteristic.
```

And the core loop is:

```text
MEASURE
   ↓
UNDERSTAND
   ↓
OPTIMIZE
   ↓
MEASURE AGAIN
```

not:

```text
GUESS
   ↓
OPTIMIZE
```

**Final principle:** performance engineering begins with evidence. A performance improvement is valuable when the right workload becomes measurably better, correctness remains intact, and the trade-offs remain acceptable.

# References and Version Notes

The examples in this chapter use Python standard-library behavior. For exact version-specific semantics, consult the Python documentation for your installed interpreter.

The current Python 3.14.7 documentation was used as an accuracy reference for `time.perf_counter()`, `time.process_time()`, the profiling interfaces, and `tracemalloc`. citeturn130118search0turn130118search4turn130118search7

# Self-Review

### Coverage
- Validation of the requested scope against the specification.
- Beginner foundations before advanced terminology.
- Timing, benchmarking, profiling, and memory measurement are taught separately.
- The observe → measure → identify bottleneck → hypothesis → optimize → re-measure loop is reinforced.
- Applied AI/data examples are included.
- Exercises, solutions, mini-project, debugging scenarios, interview questions, architecture questions, knowledge check, and completion checklist are included.

### Technical Accuracy
- `perf_counter()` is treated as an elapsed-duration timer, not a calendar clock.
- `process_time()` is treated as process CPU time and excludes sleep.
- `timeit` is treated as a microbenchmarking tool rather than a universal production predictor.
- `cProfile` statistics are described as diagnostic evidence with instrumentation overhead.
- `tottime`, `cumtime`, and `ncalls` are distinguished.
- `tracemalloc` is described as Python allocation tracing rather than total process-memory monitoring.
- No benchmark number is presented as a universal performance guarantee.
- Big-O is presented as complementary to, not a replacement for, empirical measurement.

### File-Scope Verification
- The requested target is `06-profiling-and-measuring-before-optimizing.md`.
- No companion exercise, solution, Python, configuration, or project files are intentionally created by this chapter.
- `/mnt/data` is the working artifact location for the requested Markdown deliverable; repository-level Git status cannot be inferred from the artifact-generation environment unless the repository itself is mounted and available.
