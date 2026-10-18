# `timeit` and Microbenchmark Pitfalls

> **Stage 1 — Programming & Computational Thinking · Module 17: Profiling, Memory and Runtime Performance**  
> **Lesson 03 · Target runtime: Python 3.12+**  
> **Purpose:** Design controlled Python benchmarks that measure equivalent work, report uncertainty honestly, and support defensible performance decisions.

---

## 1. Where this lesson fits

Module 17 follows the rule introduced in Module 1.10, lesson 06: **measure before you optimise**. Lesson 01 introduced deterministic profiling with `cProfile` and `pstats`; Lesson 02 introduced sampling profilers such as `py-spy`. This lesson answers a different question: **under a controlled experiment, how much time does a specific operation take, and is a difference large and repeatable enough to matter?**

The shared practice application is the deliberately inefficient `slowlog` log/CSV analytics job. Use small, isolated benchmarks to test a hypothesis about a specific operation, then verify the effect in a representative workload. This lesson does not replace profiling, memory analysis, or the later CPython-idioms lesson.

The module roadmap is authoritative for the syllabus. It calls out `timeit`, `pyperf`, `pytest-benchmark`, `asv`, measurement traps, scaling experiments, GC, Python build differences, and performance regression gates. The project tree places this lesson at `Stage 1 — Programming & Computational Thinking/17-Profiling-Memory-and-Runtime-Performance/03-timeit-and-microbenchmark-pitfalls.md`.

## 2. Prerequisites

You should already be comfortable with:

- Python functions, loops, imports, collections, and running scripts from a terminal.
- Big-O notation and choosing data structures (Module 1.4).
- Basic profiling and the principle of measuring before changing code (Modules 1.10 and 17, lessons 01–02).
- Unit tests and assertions (Module 1.7); benchmarks must preserve correctness.
- Basic CPU, memory, cache, process, and operating-system vocabulary (Stage 0).

## 3. Learning objectives

By the end of this lesson, you should be able to:

1. Choose `timeit`, `pyperf`, `pytest-benchmark`, or `asv` for a specific measurement job.
2. Separate setup, warm-up, timed work, and result validation.
3. Compare equivalent operations on identical and representative inputs.
4. Use repeated measurements, per-operation normalisation, and robust summaries without overstating certainty.
5. Explain how GC, caches, CPU state, Python builds, data shape, and environment noise affect results.
6. Benchmark list and set membership across input sizes and explain the expected complexity trend without inventing measurements.
7. Distinguish microbenchmark results from end-to-end user-visible performance.
8. Propose a defensible CI regression gate and produce a reproducible benchmark report.

---

## 4. What a microbenchmark measures

A **microbenchmark** measures a small operation or tightly scoped code path under controlled conditions. Examples include membership checks, parsing one representative record, a conversion, or one pure-Python function call.

Microbenchmarks are useful when:

- comparing two implementations of the same contract;
- estimating the cost of a hot primitive identified by a profile;
- checking how cost scales as input size changes;
- testing whether a proposed local optimisation has an effect above measurement noise;
- tracking a stable, repeatable operation across Python versions or builds.

They are not automatically useful for deciding which change will improve a production service. A tiny benchmark can exclude allocations, conversions, I/O, scheduling, contention, and caller overhead that dominate the real workload. The smaller the timed region, the more carefully you must control the experiment.

### 4.1 Three distinct questions

| Question | Suitable evidence | What it does not prove |
|---|---|---|
| Which function dominates this workload? | `cProfile`, `py-spy`, tracing, service telemetry | That a tiny rewrite is faster in isolation |
| Is implementation A faster than B for this operation? | Controlled `timeit` or `pyperf` benchmark | That the whole application improves by the same ratio |
| Does the deployed system meet latency/throughput goals? | Representative macrobenchmark, load test, production telemetry | Which line of Python caused the result without further diagnosis |

A good investigation moves between these levels: profile or observe the system, formulate a narrow hypothesis, microbenchmark the relevant operation, then validate with the larger workload.

### 4.2 Elapsed duration is not a wall-clock timestamp

Use `time.perf_counter()` for ad-hoc elapsed-duration measurements. It is a high-resolution performance counter whose differences are appropriate for timing; its absolute reference point is unspecified. On supported Python versions it is monotonic. Do not interpret the returned value as a date or time of day.

`time.time()` returns a wall-clock timestamp. System clock corrections can make wall-clock readings jump, so it is not the preferred clock for elapsed durations. Use `datetime.now()` for human-readable timestamps, not as a benchmark timer.

```python
from time import perf_counter

start = perf_counter()
result = sum(range(100_000))
elapsed_seconds = perf_counter() - start
print(f"elapsed={elapsed_seconds:.6f}s; result={result}")
```

This is useful for a coarse, end-to-end timing around a meaningful operation. For tiny operations, timer-call overhead, scheduling noise, and one-off state can be comparable to the operation itself; use `timeit` or `pyperf` instead.

---

## 5. Beginner: `timeit` fundamentals

### 5.1 `timeit.timeit`, `timeit.repeat`, and `Timer.autorange`

- `timeit.timeit(...)` runs a statement a specified number of times and returns the total elapsed seconds for those executions.
- `timeit.repeat(...)` repeats a timed run and returns one total duration per repeat.
- `timeit.Timer.autorange()` chooses a loop count large enough for the timed run to last roughly at least 0.2 seconds. It returns `(number, elapsed_seconds)`; it is calibration, not a statistical guarantee.
- `python -m timeit` offers a quick command-line interface.

For a repeated run with `number = 20_000`, if a result is `0.40` seconds, the normalised time is `0.40 / 20_000 = 0.00002` seconds per operation, or 20 microseconds. The total is not the latency of one operation.

```python
import timeit

setup = "values = list(range(10_000))"
stmt = "sum(values)"

timer = timeit.Timer(stmt=stmt, setup=setup)
number, calibration_seconds = timer.autorange()
samples = timer.repeat(repeat=7, number=number)
per_operation = [seconds / number for seconds in samples]

print(f"iterations per sample: {number}")
print(f"calibration duration: {calibration_seconds:.6f}s")
print(f"minimum: {min(per_operation) * 1e6:.2f} us/op")
print(f"median: {sorted(per_operation)[len(per_operation) // 2] * 1e6:.2f} us/op")
```

The example deliberately reports both a minimum and a median. For an even number of samples, use `statistics.median()` rather than selecting the middle item; here seven samples are used, so the middle sorted value is the median. For reusable analysis, prefer `statistics.median(per_operation)` for clarity.

`setup` is executed outside the timed statement for each timing run. With `Timer` you can also pass `globals={...}` to provide objects without string-based setup code:

```python
import timeit

values = list(range(10_000))
timer = timeit.Timer("sum(values)", globals={"values": values})
number, _ = timer.autorange()
seconds = timer.timeit(number=number)
print(f"{seconds / number:.9g} seconds per operation")
```

For ordinary function benchmarks, `Timer` also accepts a callable only through the `timeit` API's callable statement form; in practice, `timeit.Timer(lambda: fn(arg))` is a convenient pattern, but remember that the lambda/function-call wrapper is part of the timed path. `pyperf` is often a better choice for results that need stronger process isolation and statistical handling.

### 5.2 A quick command-line benchmark

```bash
python -m timeit -n 10000 -r 7 -s "values = list(range(1000))" "sum(values)"
```

Here `-n` sets the number of executions per repeat, `-r` sets the number of repeats, `-s` supplies setup code, and the final quoted expression is timed. The exact output formatting can vary by Python version. The setup creates the list outside each timed loop; list construction is therefore **not** included. If construction is part of the real operation, benchmark it separately or deliberately include it.

### 5.3 Setup, timed work, and validation

Keep these phases conceptually separate:

1. **Prepare:** construct inputs, seed random generators, load fixture data, and create reusable objects.
2. **Warm up, if relevant:** run enough work to reach the intended steady state. State whether warm-up is included or excluded.
3. **Time:** measure only the operation that answers the stated question.
4. **Validate:** assert outputs are equivalent and satisfy the contract, preferably outside the timed region unless validation is itself the target.
5. **Report:** save the exact command, environment, iteration count, repetitions, and summary statistic.

Correctness checks must not silently disappear just because the benchmark is fast. Run correctness tests before measuring, and retain a small validation step in the benchmark harness when it guards against comparing different work.

### 5.4 Why repeat measurements?

A run is affected by operating-system scheduling, interrupts, background processes, CPU power state, thermal state, cache state, allocator state, and other transient factors. Repeats help reveal variability and reduce dependence on one lucky or unlucky run. Repeats do not eliminate systematic bias: if A includes conversion but B does not, repeating the experiment makes the unfair comparison more precise, not more valid.

No single statistic is best for every question:

- **Minimum:** often used in small `timeit` experiments as a low-interference estimate because many disturbances add delay. It is useful as a rough lower-bound-like observation, but it is sensitive to sample count, can select an unusually favourable run, and does not represent typical production latency.
- **Median:** robust to a few high outliers; useful for a typical observed run under the benchmark's conditions.
- **Mean:** useful when the mean itself is the target and the measurement process is well understood, but sensitive to skew and outliers.
- **Spread / quantiles:** show instability that a single summary hides. Report individual samples or at least a spread measure when the decision depends on a small difference.

The module roadmap explicitly introduces the minimum repeat as a low-interference estimate. Treat it as one diagnostic summary, not as a universal estimator of performance and certainly not as a production p50/p95/p99 latency. For service latency, measure requests in a representative system and report the appropriate latency distribution.

**Pitfall 1 — “The minimum proves the true speed.”**  
**Why it fails:** the minimum is selected from a finite sample and changes as the number of repeats changes. It can hide scheduling pauses and does not capture typical users' experience.  
**Detect it:** compare the minimum with the median and spread; repeat the experiment in a fresh process or on a second controlled run.  
**Correct it:** report multiple summaries, explain why the minimum is included, and use a macrobenchmark for user-facing latency.

---

## 6. Intermediate: design a fair comparison

### 6.1 Equivalent work is the non-negotiable requirement

Before timing, write down the contract for both implementations: inputs, output, errors, side effects, and whether setup or conversion belongs to the operation. Check equivalence with tests. A comparison is unfair if one implementation parses, normalises, copies, validates, or allocates data that the other receives pre-built.

For example, this compares different work:

```python
# Unfair: conversion happens only for the list implementation.
needle in list(values)
needle in values_set
```

If the production operation converts an incoming list to a set on every call, excluding that conversion answers a narrower question (“membership after the set already exists”), not the end-to-end question. Both questions can be useful, but label them separately.

A controlled harness should define data once and use identical query values:

```python
values = list(range(100_000))
values_set = set(values)
needle = 100_001  # deliberately absent: a full list scan
assert (needle in values) == (needle in values_set)
```

The assertion checks this one case; robust tests should cover hits, misses, duplicates if relevant, and the actual contract. Do not assume that identical-looking code has equivalent semantics for all data types.

**Pitfall 2 — asymmetric setup or conversion.**  
**Why it fails:** setup cost can dominate a small operation, and excluding it from one variant biases the result.  
**Detect it:** annotate each line as setup, timed work, or validation; inspect whether both variants receive the same representation.  
**Correct it:** benchmark lookup-only with both structures prebuilt, then benchmark end-to-end construction-plus-lookup as a separate, explicitly named scenario.

### 6.2 Global lookup, function calls, and the benchmark harness

For tiny operations, the benchmark harness itself can dominate. A global name lookup, attribute access, wrapper function, argument unpacking, and timer overhead can be a meaningful fraction of the measured operation. That does not make such costs “fake”: they matter if they are part of the production call path. The issue is whether they are included consistently and whether the benchmark answers the intended question.

Prefer to benchmark the same call shape for both alternatives. Do not alias one implementation to a local variable while looking up the other globally unless the production code does that and it is the subject of the experiment. If comparing whole functions, pass both functions through the same harness and validate outputs separately.

### 6.3 Never benchmark `print` by accident

Terminal output is slow, buffered, and environment-dependent. Printing inside the timed loop measures output and terminal/pipe behaviour as much as computation.

**Pitfall 3 — printing or logging inside the timed statement.**  
**Why it fails:** I/O cost dwarfs many operations and changes with terminal, buffering, log configuration, and output volume.  
**Detect it:** look for `print`, logging, file writes, network calls, or assertions in the timed path.  
**Correct it:** accumulate results or return them, then print after timing. Benchmark logging separately only when logging is the workload of interest.

### 6.4 Input size, shape, and distribution

A benchmark with one input shape can miss the real performance boundary. Include multiple sizes and relevant distributions:

- small inputs where constant overhead dominates;
- medium and large inputs where algorithmic complexity dominates;
- hits near the beginning and end of a list, absent keys, and realistic hit/miss ratios;
- sorted, random, clustered, or adversarial values where branch behaviour or algorithm behaviour depends on ordering;
- realistic string lengths, missing values, skew, duplicates, and error rates for data pipelines.

Do not choose only the input that makes the preferred implementation look good. If production traffic has a known distribution, preserve it or state why the synthetic workload is a useful proxy.

**Pitfall 4 — an unrepresentative input.**  
**Why it fails:** early-hit list membership, tiny lists, or unusually uniform data can reverse or shrink the observed trade-off.  
**Detect it:** compare benchmark inputs to production cardinality, hit/miss ratio, value lengths, skew, and error frequency.  
**Correct it:** benchmark several sizes and distributions; publish the workload generator and its seed where randomness is used.

### 6.5 Include costs that the user actually pays

There are two legitimate but different measurements:

- **Kernel/operation benchmark:** inputs are prepared before timing to isolate the operation.
- **End-to-end path benchmark:** parsing, conversion, allocation, validation, and downstream work are included because production pays those costs.

Never compare a kernel result with an end-to-end result. Use names such as `membership_lookup_only` and `construct_set_then_lookup` rather than the vague label `set_is_faster`.

---

## 7. Practical experiment: list versus set membership at several sizes

### 7.1 Hypothesis and expected trend

**Hypothesis:** for a membership check against a prebuilt collection, a set will usually scale better than a list for large collections when hash computation is cheap and hash/equality behaviour is well-behaved.

- List membership is linear in the number of elements in the worst case; an absent needle requires checking all elements, so the work grows roughly with `n`.
- Set membership is expected O(1) on average under ordinary hash-table assumptions, though hash collisions, expensive `__hash__`/`__eq__`, resizing, and pathological inputs can make it worse.
- For very small collections, constants and memory/cache effects can make a list competitive or faster. Big-O does not predict exact timings.

The following script measures **lookup only**. It prebuilds the list and set, uses the same absent needle, checks correctness, calibrates each case, and prints the minimum and median per-operation time from repeated samples. The size series reaches \(10^6\), matching the roadmap's scaling exercise; that case can use substantial memory, so skip it on a constrained machine and record the omission rather than silently changing the workload. It does not embed invented numbers: run it on your own environment and preserve the output with the environment metadata.

Save as `bench_membership.py`:

```python
from __future__ import annotations

import platform
import statistics
import sys
import timeit


def benchmark_lookup(size: int, repeats: int = 7) -> None:
    values = list(range(size))
    values_set = set(values)
    needle = size + 1  # absent: forces a full list scan

    assert len(values) == len(values_set) == size
    assert needle not in values and needle not in values_set

    cases = {
        "list_miss": timeit.Timer(
            "needle in values",
            globals={"needle": needle, "values": values},
        ),
        "set_miss": timeit.Timer(
            "needle in values_set",
            globals={"needle": needle, "values_set": values_set},
        ),
    }

    print(f"\nsize={size:,}; repeats={repeats}; needle=absent")
    numbers = {}
    for name, timer in cases.items():
        numbers[name], _ = timer.autorange()

    # Alternate the order across rounds to reduce systematic order bias.
    per_op = {name: [] for name in cases}
    names = list(cases)
    for round_index in range(repeats):
        order = names if round_index % 2 == 0 else list(reversed(names))
        for name in order:
            elapsed = cases[name].timeit(number=numbers[name])
            per_op[name].append(elapsed / numbers[name])

    for name in names:
        samples = per_op[name]
        print(
            f"{name:10s} number={numbers[name]:>9,d} "
            f"min={min(samples) * 1e6:10.3f} us/op "
            f"median={statistics.median(samples) * 1e6:10.3f} us/op "
            f"range=[{min(samples) * 1e6:.3f}, {max(samples) * 1e6:.3f}] us/op"
        )


def main() -> None:
    print(f"Python: {sys.version.replace(chr(10), ' ')}")
    print(f"Implementation: {platform.python_implementation()}")
    print(f"Platform: {platform.platform()}")
    for size in (10, 1_000, 10_000, 100_000, 1_000_000):
        benchmark_lookup(size)


if __name__ == "__main__":
    main()
```

Run it in a quiet environment:

```bash
python bench_membership.py
```

**How to interpret it:** do not copy expected timings from another machine. Look for the trend across sizes and the variability across repeats. A list miss tends to grow with size; set lookup often remains comparatively flat over these sizes, but the exact curve depends on CPU, Python build, allocator, cache state, and run conditions. At size 10, the difference may be small or reverse. These are expected complexity trends, not guaranteed measured results.

The script calibrates `number` independently for each case so each timing sample lasts long enough for a useful measurement. It alternates list/set order across rounds, and reports minimum, median, and observed range. Because the number of iterations differs across cases, compare per-operation values, not raw totals. Alternation reduces one source of order bias but does not make samples independent or remove cache/thermal effects. Re-run the entire script in a fresh process and record the conditions; for a serious claim, use independent process-level repetitions and consider `pyperf`.

### 7.2 Add hit positions and realistic hit rates

A list hit at index 0 is not equivalent to an absent needle. For a list of size `n`, an absent needle checks all `n` items; a uniformly distributed successful hit checks roughly half the list on average, while an early-biased distribution can check far fewer. Sets do not have a positional search in the same sense, but hash/equality cost and cache locality still matter.

Extend the experiment with separate cases for:

- `needle = 0` (first element hit);
- `needle = size // 2` (middle hit);
- `needle = size - 1` (last element hit);
- absent needle;
- a production-like mix of hits and misses.

Keep each case named and run the same query distribution for both structures. If a random query stream is used, generate it outside the timed region with a fixed seed and use that exact stream for both variants.

### 7.3 Measure conversion cost separately

To answer “I receive a list and need one lookup, should I convert it to a set?”, measure the whole path too:

```python
import timeit

size = 10_000
values = list(range(size))
needle = size + 1

lookup_only_set = timeit.Timer(
    "needle in values_set",
    globals={"needle": needle, "values_set": set(values)},
)
construct_and_lookup = timeit.Timer(
    "needle in set(values)",
    globals={"needle": needle, "values": values},
)

for label, timer in (
    ("lookup_only_set", lookup_only_set),
    ("construct_and_lookup", construct_and_lookup),
):
    number, _ = timer.autorange()
    samples = timer.repeat(repeat=7, number=number)
    print(label, "min seconds/op:", min(samples) / number)
```

This snippet intentionally contrasts two different questions and labels them accordingly. The `lookup_only_set` object is built once in setup; `construct_and_lookup` builds a new set on every timed operation. Do not present them as an apples-to-apples implementation comparison. For an end-to-end comparison against list lookup, add `needle in values` as a third case using the same `values` and `needle`. For repeated lookups, benchmark amortised conversion cost across the realistic number of queries rather than assuming conversion happens once or on every call.

---

## 8. Tool choice: `timeit`, `pyperf`, `pytest-benchmark`, and `asv`

### 8.1 `timeit`: quick, focused experiments

Use `timeit` to explore a small hypothesis, learn how input size changes cost, or make a quick controlled comparison. It is in the standard library and needs no installation. Its convenience does not make it a full benchmarking framework: it runs in one process by default, and environmental noise or benchmark design flaws still matter.

Remember that `timeit` **disables garbage collection by default during timed runs**. This helps reduce noise from cyclic GC, but it may not reflect a production workload where collections occur. If GC cost is part of the operation under study, enable it explicitly in setup or use a harness that models the intended workload. Enabling GC does not mean a collection occurs during every sample; record the intended GC policy.

Example with GC included deliberately:

```python
import gc
import timeit

# This setup runs before each timing run; the timed operation is make_objects().
setup = "import gc; gc.enable(); from workload import make_objects"
timer = timeit.Timer("make_objects()", setup=setup)
number, _ = timer.autorange()
samples = timer.repeat(repeat=7, number=number)
print("median seconds/op:", __import__("statistics").median(samples) / number)
```

Use a real `make_objects()` implementation that creates and releases the relevant object graph. Do not leave cyclic objects accumulating without bounds, and ensure the benchmark measures the same GC policy as the question requires.

### 8.2 `pyperf`: stronger comparisons and stored benchmark suites

`pyperf` is useful when the result will support a performance claim, compare Python builds, or be tracked over time. It provides process-based benchmark runs, calibration, metadata, statistical summaries, and tooling to inspect results. Install it in the project environment:

```bash
uv add --dev pyperf
uv run python -m pyperf --help
uv run python -m pyperf timeit --help
```

Command-line example (the statement is a lookup against prebuilt objects):

```bash
uv run python -m pyperf timeit \
  --name list-membership-miss \
  --setup 'values = list(range(10000)); needle = 10001' \
  -o list-membership.json \
  'needle in values'
```

Check `python -m pyperf timeit --help` for the installed version's exact option names. Save the generated benchmark JSON when comparing runs; do not rely only on terminal text. Compare results collected under compatible machine and runtime conditions.

A small Python benchmark suite can use `pyperf.Runner`:

```python
# bench_pyperf.py
import pyperf

values = list(range(10_000))
values_set = set(values)
needle = 10_001
assert (needle in values) == (needle in values_set)

runner = pyperf.Runner()
runner.bench_func("list-membership-miss", values.__contains__, needle)
runner.bench_func("set-membership-miss", values_set.__contains__, needle)
```

Run with:

```bash
uv run python bench_pyperf.py --help
uv run python bench_pyperf.py -o membership.json
```

The script uses bound `__contains__` methods so the callable shape is explicit; each benchmark invokes one method with the same needle. Validate that this call shape matches the operation you intend to compare. For tiny operations, wrapper and call overhead can affect results; run both through the same harness and interpret the result as a method-call benchmark, not as a pure hardware instruction cost. Use the CLI statement benchmark if you specifically want to measure expression evaluation in a timed loop. The runner's CLI options can vary by version; inspect `--help`.

### 8.3 `pytest-benchmark`: benchmarks beside tests

Use `pytest-benchmark` when a project already uses pytest and you want benchmark cases, fixtures, saved runs, and comparison workflows in the test suite. Install it as a development dependency:

```bash
uv add --dev pytest pytest-benchmark
```

Example `tests/test_membership_benchmark.py`:

```python
import pytest


@pytest.mark.parametrize("size", [10, 1_000, 100_000])
def test_set_membership_benchmark(benchmark, size):
    values = list(range(size))
    values_set = set(values)
    needle = size + 1

    assert needle not in values and needle not in values_set
    result = benchmark(values_set.__contains__, needle)
    assert result is False
```

Run:

```bash
uv run pytest tests/test_membership_benchmark.py --benchmark-only
uv run pytest tests/test_membership_benchmark.py --benchmark-save=baseline
uv run pytest tests/test_membership_benchmark.py --benchmark-compare=0001  # replace 0001 with the saved run ID shown by pytest-benchmark
```

Check the installed plugin's `pytest --help` for exact options. The setup and correctness assertions above occur outside the timed call. This benchmark isolates membership on a prebuilt set; it does **not** compare list versus set or include set construction. Add separate named cases for each question. Do not assume that a benchmark plugin automatically turns a noisy timing into a trustworthy CI gate; runner consistency, repeatability, and a calibrated threshold remain your responsibility.

### 8.4 `asv`: long-term performance across commits and versions

`asv` (airspeed velocity) is suited to tracking a benchmark suite over repository history, commits, and Python versions. It is useful for libraries where a small regression can accumulate unnoticed and where maintainers need to identify which change caused a trend. It is usually excessive for a one-off local question.

Install and inspect the current commands rather than assuming a particular version's config schema:

```bash
uv add --dev asv
uv run asv --help
uv run asv quickstart
```

The quickstart creates a project configuration and benchmark layout; follow the generated configuration and installed version's documentation. Keep benchmark functions deterministic, keep fixtures realistic, and ensure each commit's code is tested against comparable Python versions and machines. An `asv` history is only meaningful if the environment and runner conditions are controlled and documented.

### 8.5 Choosing a tool

| Need | Starting point | Why |
|---|---|---|
| Fast local experiment | `timeit` | Standard library, minimal setup |
| Publish a careful microbenchmark claim | `pyperf` | Process isolation, calibration, result files, statistics |
| Keep performance tests with pytest tests | `pytest-benchmark` | Fixture-based benchmarks and saved-run comparisons |
| Track a library across commits / interpreters | `asv` | Historical benchmark suite and version matrix |
| Find a real application's hot path | `cProfile` / `py-spy` | Identify what deserves a benchmark |
| Validate user-visible latency and throughput | Macrobenchmark / load test | Captures system interactions that a microbenchmark excludes |

---

## 9. Machine and runtime effects you must control or report

### 9.1 CPU frequency, background activity, and thermals

Modern CPUs change frequency based on load, power policy, and temperature. A laptop may run one test while cool and another after sustained load while thermally throttled. Background builds, browser tabs, antivirus scans, virtual machines, CI neighbours, and other processes introduce interference.

- Close avoidable heavy workloads and avoid running unrelated builds during a benchmark.
- Use a consistent power mode and machine for before/after comparisons.
- Let the system reach a stable thermal state for longer runs; note whether the machine is a laptop or shared runner.
- For high-confidence claims, use a dedicated or controlled runner and repeat the whole benchmark session.
- Do not blindly disable power management or pin CPU affinity without understanding the platform; record such controls if used.

**Pitfall 5 — comparing runs on different or drifting machines.**  
**Why it fails:** CPU model, microcode, power policy, thermal state, RAM, OS scheduling, and other load can be larger than the code change.  
**Detect it:** compare metadata and the sample spread; rerun a known control benchmark and check whether it drifted.  
**Correct it:** use the same machine/configuration, alternate A/B run order when practical, repeat in fresh processes, and disclose unavoidable differences.

### 9.2 Python version, build, imports, and caches

Performance can change between Python releases and builds. The specialising adaptive interpreter introduced in CPython 3.11 can optimise hot code based on observed execution; this does not imply every snippet becomes faster or that results transfer unchanged to other interpreters. PGO/LTO build options, debug instrumentation, compiler, linked libraries, and extension versions can all matter.

Import time and first-use work should be treated explicitly:

- If measuring **steady-state function cost**, import modules and warm up outside the timed region.
- If measuring **cold startup**, launch a fresh process and include imports by design; don't use a warmed in-process timer.
- If a cache is part of the intended workload, decide whether the benchmark measures cold cache, warm cache, cache miss, cache hit, or a realistic mix.
- If a regex, parser, serializer, or query plan is compiled/cached on first use, report whether that first-use cost is included.

**Pitfall 6 — accidental warm-cache advantage.**  
**Why it fails:** one variant may reuse memoized results, compiled patterns, open connections, filesystem pages, or interpreter-specialised code while the other pays setup costs.  
**Detect it:** repeat with fresh objects/processes and compare cold and warm paths separately. Inspect caches and initialization performed before timing.  
**Correct it:** define the intended cold/warm scenario and use the same policy for both variants; label each result accordingly.

### 9.3 Garbage collection and allocation

`timeit` disables cyclic garbage collection by default during timed runs. Reference counting still occurs in CPython, but cyclic GC does not run in the timed loop unless re-enabled. This reduces one source of timing noise but may conceal costs that matter when a workload creates cycles or triggers collections. Allocator behaviour, reference counting, object creation, and memory pressure can still affect the result.

Choose deliberately:

- **GC excluded:** appropriate for isolating a small operation when cyclic GC is unrelated to the question.
- **GC enabled:** appropriate when object churn and collection pauses are part of the workload.
- **Production-like allocation loop:** appropriate when allocation patterns, object lifetimes, and collection frequency affect throughput or latency.

State the policy in the report. Avoid global GC tuning just to make a benchmark look better; validate any tuning in a representative workload and keep memory correctness intact.

### 9.4 Constant folding, dead work, and caching

Python is not a C compiler, and it does not generally remove arbitrary Python computations as a C/C++ optimiser might. Still, benchmark code can accidentally avoid the work it claims to measure:

- constant expressions may be computed at compile time or before the timer starts;
- setup may precompute a result, so the timed statement measures only a lookup;
- `functools.cache`, `lru_cache`, application caches, or memoized regex compilation may make repeated calls measure hits rather than computation;
- a result can be calculated once outside the loop and then reused, or the benchmark may omit consuming/validating the result;
- copy-on-write pages after `fork`, warmed filesystem pages, and memory locality can change costs across runs;
- branch prediction and CPU cache effects depend on access order and data distribution.

**Pitfall 7 — timing cached or precomputed work while claiming to time computation.**  
**Why it fails:** the timed path is a cache hit, constant lookup, or repeated access to already-hot data, not the expensive operation in the hypothesis.  
**Detect it:** inspect setup and function state; count cache hits/misses; run cold and warm cases separately; use fresh inputs when that matches the intended contract.  
**Correct it:** name the scenario precisely and prepare a controlled sequence of inputs outside the timer if input generation is not part of the operation. Do not add artificial randomness inside the timed loop unless random generation is genuinely part of production work.

### 9.5 JIT and free-threaded Python: qualify claims by build

The roadmap targets Python 3.12+ and asks for awareness of newer runtime behaviour. Do not generalise one build's result to all Python installations.

- CPython 3.11+ has a specialising adaptive interpreter; it is not the same thing as a general-purpose tracing JIT.
- Experimental JIT support has appeared in newer CPython development/release lines, with availability and activation depending on the exact version, build options, and platform. Do not assume `PYTHON_JIT=1` works or is enabled on every 3.13+ installation. Inspect the exact interpreter's documentation and `sysconfig`/build information, and report the actual build used.
- Free-threaded CPython builds are distinct from conventional GIL-enabled builds and have version- and extension-compatibility constraints. Single-thread overhead, multithreaded throughput, extension behaviour, and contention can differ. Do not infer a universal “free-threading penalty” or speed-up; benchmark the target workload on the target build.
- Compare exact Python patch release, implementation, build flags, and installed extension versions. Never attribute a difference solely to source code when the interpreter build also changed.

---

## 10. Statistical interpretation without overclaiming

### 10.1 Normalise correctly

If each repeat times `number` operations, normalise each repeat individually:

\[
 t_i = \frac{T_i}{N}
\]

where `T_i` is the total duration of repeat `i` and `N` is the operation count for that repeat. Report seconds/op, microseconds/op, or another suitable unit. Do not divide a minimum total from one run by an iteration count from another run.

### 10.2 Effect size and speed-up ratio

For a baseline time `B` and candidate time `C`, define the observed ratio as:

\[
 R = \frac{B}{C}
\]

If `R > 1`, the candidate was faster in that observed comparison. The observed percentage reduction in time is:

\[
 100 \times \frac{B-C}{B}\%.
\]

These formulas describe the measured values; they do not establish that the underlying performance difference is real or practically important. A ratio of 1.02 can be smaller than environmental variability. Always retain units and the underlying sample data.

### 10.3 Variation, confidence intervals, and uncertainty

For a first exploration, report individual repeat results, median, minimum, and range. For more formal comparisons, collect independent process-level runs and use a method appropriate to the data and experimental design. A confidence interval for a median, mean, or ratio depends on the estimator and assumptions; don't present a generic formula as if it applies to every benchmark.

A few important cautions:

- Repeats within one process are not always independent; caches, thermal drift, interpreter state, and workload order can correlate them.
- A narrow confidence interval around a biased comparison is still misleading.
- “The confidence intervals overlap” is not a complete significance test; overlap alone does not settle whether a difference is statistically meaningful.
- Statistical significance does not automatically mean practical significance. A tiny reduction in an operation called once per job may not matter; a smaller per-call saving in a hot path may accumulate.
- Avoid repeated peeking and rerunning until a favourable result appears (“p-hacking”). Define the number of runs and decision rule before interpreting results where possible.

For high-stakes claims, use `pyperf` or a documented statistical workflow, collect enough process-level data, and state the uncertainty method. Do not claim “2× faster” based on one run or on an unrepresentative input. If the observed effect is smaller than the noise, report the result as inconclusive and design a better experiment.

**Pitfall 8 — reporting a speed-up from one noisy run.**  
**Why it fails:** random noise, run order, and selection bias can make either variant look better.  
**Detect it:** inspect the full distribution and repeat in independent processes; compare the effect size with observed variability.  
**Correct it:** predefine repetitions and summary statistics, save raw results, report uncertainty, and call small ambiguous differences inconclusive.

### 10.4 A practical A/B protocol

1. State a falsifiable hypothesis and choose a primary metric before running.
2. Test output equivalence independently of timing.
3. Fix the input and runtime configuration; decide cold/warm and GC policy.
4. Calibrate iteration count; collect multiple samples per variant.
5. Repeat the whole experiment in independent processes or sessions when the claim warrants it.
6. Alternate or randomise A/B order when drift may favour one variant.
7. Save raw results and environment metadata.
8. Report effect size, spread/uncertainty, limitations, and whether the result changes the engineering decision.

---

## 11. Microbenchmarks versus macrobenchmarks and end-to-end performance

A microbenchmark deliberately excludes most system complexity. A **macrobenchmark** measures a larger operation, such as parsing a CSV file, processing a batch, serving requests, or completing an ETL job. An end-to-end benchmark includes the costs users or downstream systems actually experience.

Suppose a function accounts for 1% of end-to-end runtime. Even making that function infinitely fast cannot improve the total by more than about 1% if everything else stays unchanged. This is the practical meaning of Amdahl's law: local speed-ups are bounded by the fraction of total time they affect.

Use both levels:

- Microbenchmark the primitive to understand the mechanism and isolate a trade-off.
- Run a macrobenchmark with realistic data size, data shape, and concurrency.
- Compare correctness, total duration, throughput, and relevant latency percentiles.
- Include data loading, parsing, conversions, allocation, I/O, serialisation, and orchestration when production pays those costs.

A 3× faster loop can be irrelevant if it contributes little to total runtime. Conversely, a modest improvement in a repeated hot path can matter at scale. Always connect the microbenchmark back to the workload profile and the end-to-end acceptance criterion.

### 11.1 I/O, network, and database benchmarks

I/O benchmarks require especially careful naming:

- **Warm filesystem cache** versus cold-ish reads: the OS may serve data from memory. Truly cold-cache experiments may require privileged system controls and should not be attempted casually on shared machines.
- **Warm connection / prepared statement** versus connection setup and query planning.
- **Local loopback** versus realistic network latency, TLS, DNS, routing, and remote service load.
- **Database buffer cache hit** versus storage read; warmed query plans and indexes can change results.
- **Client-side time** versus server-side execution time and queueing.

Do not claim to measure remote latency by looping over an in-process stub or localhost server. Use a test environment representative of the deployment, control concurrency, and record dataset size, cache policy, connection reuse, network topology, server version, and contention. For distributed services, separate latency components where telemetry permits and report p50/p95/p99 when those are the relevant SLO metrics.

---

## 12. Hands-on task: benchmark a `slowlog` hotspot

The module's shared `slowlog` app is a deliberately inefficient log/CSV analysis job. Use the version already present in your project; do not replace it with an unrelated synthetic application. The exact hot path should come from your profile of the actual workload, not from assumption.

### Task A — establish correctness and baseline

1. Identify one pure-Python hot path from Lesson 01/02 evidence (for example, repeated membership against a list, repeated parsing, or repeated conversion).
2. Record the input file or generator parameters, row count, field distribution, Python version/build, and command.
3. Run the existing correctness tests and save the expected output or a deterministic checksum.
4. Measure the end-to-end `slowlog` runtime several times under stable conditions. Do not use a profiler's elapsed time as the benchmark baseline.
5. Write a narrow benchmark for the suspected operation using `timeit` or `pyperf`; separate setup from timed work and validate equivalent results.

### Task B — compare alternatives fairly

1. Write the baseline and candidate implementations with the same contract.
2. Use identical fixtures and input distributions. If a conversion is required in production, include it in an end-to-end scenario.
3. Run multiple sizes and at least one realistic distribution.
4. Save raw measurements and summarize minimum, median, range, and the observed effect size. Do not invent values or assume the candidate wins.
5. Re-run the complete application with the same input and confirm output equivalence.

### Task C — performance regression guard

1. Add a `pytest-benchmark` case for the stable, narrow operation, or add a `pyperf` benchmark suite if process isolation and stored results are more appropriate.
2. Keep correctness tests independent from performance assertions.
3. For CI, use a controlled runner, compare repeated results against a compatible baseline, and choose a threshold larger than normal noise. Store benchmark artifacts for investigation.
4. If the runner is shared/noisy, report regressions for review rather than failing the build on a tiny raw-time difference.
5. Document what is excluded (disk cache, CSV parsing, allocations, conversion, concurrency) and then confirm the result with a macrobenchmark that includes the relevant costs.

**Deliverable:** `PERF_REPORT.md` section describing one `slowlog` hypothesis, the benchmark script and exact command, environment, correctness proof, raw results, chosen statistics, limitations, and end-to-end validation. A benchmark that shows no clear improvement is still a successful experiment if the conclusion is honest and reproducible.

---

## 13. Performance regression gates in CI

Wall-clock thresholds are inherently sensitive to runner variance. Avoid brittle tests such as `assert duration < 0.01` on a general-purpose shared CI runner. Prefer a dedicated, stable runner and compare against a baseline collected under the same environment.

A defensible gate should:

- use a deterministic workload and correctness checks;
- run on the same hardware class, OS image, Python build, dependency set, and power/runner policy;
- collect multiple samples and save raw benchmark artifacts;
- compare a suitable summary or distribution, not just one number;
- use a threshold informed by historical noise and the cost of regressions;
- separate noisy performance reporting from correctness failures;
- include a re-run or human review path for borderline results;
- be recalibrated after Python, hardware, compiler, or dependency upgrades.

A simple relative rule such as “flag if candidate is more than 20% slower across three independent benchmark sessions” can be a starting policy, but it is **not universally valid**. Three sessions may be too few for a noisy benchmark; a 20% threshold may be too permissive for a critical path or too strict for a variable shared runner. Define “slower” using the selected metric, require compatible environments, and confirm that the observed effect exceeds normal baseline variability.

Do not treat `pytest-benchmark --benchmark-compare` as a magical regression oracle. It compares saved benchmark data; the CI policy still needs a stable runner, compatible environment, sensible thresholds, and a process for investigating variance. Store `.json`/benchmark artifacts and logs so reviewers can inspect the evidence.

---

## 14. Benchmark-claim review checklist

Before accepting a claim such as “candidate B is 25% faster than A,” review each item:

- [ ] **Hypothesis:** Is the question precise and falsifiable?
- [ ] **Scope:** Is this lookup-only, function-only, cold-start, or end-to-end?
- [ ] **Correctness:** Do both implementations return equivalent results and preserve errors/side effects?
- [ ] **Inputs:** Are sizes, shapes, distributions, hit rates, and data types identical and representative?
- [ ] **Setup:** Are imports, allocations, conversions, caches, and fixture construction included or excluded consistently?
- [ ] **Timed region:** Is the harness timing the intended operation rather than printing, logging, generating inputs, or validating unrelated work?
- [ ] **Repetitions:** Are there multiple samples and, for important claims, independent process/session repetitions?
- [ ] **Statistics:** Are units, sample count, central summary, spread/uncertainty, and effect size reported?
- [ ] **Noise:** Were background load, CPU frequency, thermal state, and runner consistency considered?
- [ ] **GC:** Is the `timeit` default GC policy appropriate and documented?
- [ ] **Runtime:** Are Python implementation/version/build flags and extension versions recorded?
- [ ] **Caches/warm-up:** Are cold and warm scenarios clearly distinguished?
- [ ] **Practical relevance:** Is the operation important in the profile, and does the gain survive in a macrobenchmark?
- [ ] **Reproducibility:** Are code, command, fixture/generator, seed, raw results, and environment metadata available?
- [ ] **Claim language:** Does the conclusion reflect the evidence, including “inconclusive” when differences are within noise?

Reject a claim if it cannot answer these questions. A precise number is not evidence by itself.

---

## 15. Reproducible benchmark report template

Copy this template into `PERF_REPORT.md` or the project's benchmark record and complete every relevant field. Mark non-applicable fields explicitly rather than silently omitting them.

```markdown
# Benchmark report: <short name>

## Hypothesis
- Question:
- Baseline implementation:
- Candidate implementation:
- Expected mechanism / complexity:
- Primary metric and decision rule:

## Scope
- Operation measured (lookup-only / function / cold start / end-to-end):
- Included costs:
- Excluded costs:
- Why this scope answers the question:

## Environment
- Date/time and operator:
- OS / kernel / container image:
- Hardware / CPU / RAM:
- Power mode / runner type / other workload:
- Python implementation and exact version:
- Python build flags (PGO/LTO/debug/JIT/free-threaded status, if known):
- Compiler / linked libraries (if relevant):
- Dependency and extension versions:
- Benchmark tool and version:
- Exact command:
- Source revision / commit:

## Input characteristics
- Size and shape:
- Data types / field lengths / skew / hit rate:
- Generator, seed, source fixture, and checksum:
- Cold or warm cache policy:
- Warm-up policy:
- GC policy:

## Controls and methodology
- Equivalence/correctness checks:
- Setup versus timed work:
- Iteration calibration and iterations per sample:
- Number of repeats and independent process/session runs:
- A/B order or randomisation policy:
- Outlier handling policy (defined before analysis):
- Known environmental limitations:

## Raw results
- Attach or link raw output files:
- Baseline samples and units:
- Candidate samples and units:
- Sample count:

## Summary statistics
- Primary summary and why selected:
- Minimum / median / mean as appropriate:
- Spread / quantiles / confidence interval method:
- Effect size and formula:
- Observed ratio and percentage change:
- Measurement uncertainty / practical significance:

## Results and interpretation
- Correctness result:
- What changed:
- What was measured:
- What was not measured:
- End-to-end or macrobenchmark confirmation:
- Confounders and alternative explanations:

## Limitations
- Generalisability to production:
- Known bias / noise / sample-size concerns:
- Python-version / machine constraints:

## Conclusion
- Decision: accept / reject / inconclusive / investigate further
- Evidence supporting the decision:
- Follow-up experiment or regression guard:
- Reviewer and review date:
```

---

## 16. Common mistakes: diagnostic summary

| Mistake | Why it misleads | Detection | Correction |
|---|---|---|---|
| Treating minimum as typical latency | Minimum suppresses many disturbances and is sample-count-dependent | Compare min, median, range, and real request latency | Report multiple summaries; use a macrobenchmark for latency |
| Including conversion for only one variant | Variants do unequal work | Trace each timed statement and setup | Measure kernel-only and end-to-end cases separately |
| Printing/logging inside the timer | I/O dominates and varies by environment | Inspect timed path | Return/accumulate results and print afterward |
| Using tiny or biased input | Constants or input distribution dominate | Compare to production shape and size | Benchmark multiple sizes and representative distributions |
| Comparing different machines or thermal states | Environment differences can exceed code effects | Inspect metadata and control benchmarks | Same runner, stable conditions, repeated sessions |
| Measuring a warm cache as computation | Timed work becomes lookup/reuse | Inspect caches and fresh-process behaviour | Name cold/warm cases and control state |
| Making a claim from one run | Noise and run order can reverse results | Inspect samples and rerun independently | Predefine repetitions and report uncertainty |
| Ignoring `timeit`'s GC policy | GC-heavy production behaviour may be absent | Check default and setup | Document and measure intended GC scenario |
| Treating microbenchmark ratio as application speed-up | Other costs dominate end-to-end runtime | Compare with profile and macrobenchmark | Validate full workload and use Amdahl's law |
| Comparing different Python builds as if source alone changed | Interpreter/build effects confound attribution | Record exact version/build | Compare like with like or explicitly study runtime differences |

---

## 17. Troubleshooting

### The measurements vary widely

- Close avoidable background workloads and repeat the entire session.
- Check CPU/thermal/power state and whether a shared CI runner is contended.
- Increase the duration per sample with calibration; don't simply increase the loop count without checking that the workload remains representative.
- Look for allocation bursts, GC, I/O, or asynchronous work inside the timed region.
- Report the variation; if it remains larger than the effect, call the result inconclusive.

### The candidate appears much faster, but the application does not

- Check whether the candidate operation is a small fraction of total runtime.
- Verify that the macrobenchmark includes conversion, parsing, I/O, allocation, and caller overhead as applicable.
- Recheck output equivalence and whether the benchmark measures a cache hit or different input distribution.
- Use the profile to see whether the bottleneck moved or another cost now dominates.

### The result changes across Python versions

- Record exact interpreter version, implementation, build flags, extension versions, and OS image.
- Separate source-code changes from interpreter/build changes; use a version matrix if runtime behaviour is the question.
- Re-run under comparable machine conditions and avoid extrapolating one build's result to all deployments.

### `pytest-benchmark` or `pyperf` command differs from a tutorial

- Run the installed tool's `--help` and inspect its installed version/documentation.
- Keep the raw result file and exact command with the report.
- Do not silently change flags between baseline and candidate runs.

---

## 18. Exercises

1. **Minimum versus median:** run a `timeit.repeat` experiment with a short operation and explain what minimum, median, and range each reveal. Why is the minimum not production p50?
2. **Setup isolation:** benchmark list membership, set membership with a prebuilt set, and `set(values)` plus membership. Name each question accurately and explain which result applies to repeated queries.
3. **Scaling:** run the supplied membership script across all sizes. Plot the measurements if useful; describe the trend and deviations without copying expected numbers from another machine.
4. **Input distribution:** compare first-position hit, middle hit, last-position hit, and absent needle. Explain why a single hit pattern is insufficient.
5. **GC:** benchmark an allocation-heavy operation with GC disabled and enabled. Explain which scenario better matches your production workload and why.
6. **Warm/cold:** benchmark a cached function on cold and warm paths. Demonstrate that the benchmark name and setup make the distinction explicit.
7. **Tool choice:** choose among `timeit`, `pyperf`, `pytest-benchmark`, and `asv` for a local experiment, a CI suite, and a multi-version library. Defend each choice.
8. **Statistics:** given a candidate whose median is slightly faster but whose repeat range overlaps substantially with baseline variation, write a conclusion that does not overclaim.
9. **CI gate:** design a regression gate for a dedicated runner. Define metric, repeats, threshold, baseline update policy, artifacts, and borderline-result handling.
10. **`slowlog` task:** profile the existing app, pick a measured hotspot, implement a candidate, prove correctness, benchmark the narrow operation, and confirm the result end to end.

## 19. Self-check questions

1. What does `timeit.timeit` return, and why divide by `number` to report per-operation time?
2. What does `Timer.autorange()` choose, and what does it not guarantee?
3. Why is `time.perf_counter()` preferred to `time.time()` for elapsed duration?
4. Why does `timeit` disable cyclic GC by default, and when should you re-enable it?
5. Why can the minimum be useful while still being unsuitable as typical production latency?
6. How can a comparison be unfair even when both timed statements look short and simple?
7. Why do absent list membership and set membership show different expected complexity trends?
8. What is the difference between a microbenchmark and an end-to-end benchmark?
9. Why are confidence intervals and effect size not a substitute for equivalent work and sound controls?
10. Which environment details must be recorded before comparing results across Python versions?
11. How can cache state, memory locality, and branch prediction change a benchmark?
12. What evidence would you require before accepting a “25% faster” claim?

## 20. Technical references

The roadmap defines this lesson's curriculum. The following primary documentation was used to check API and tool behavior; command-line details can vary by installed tool version, so retain the exact environment and consult local `--help` output before relying on a CI command.

- Python 3.12 `timeit`: <https://docs.python.org/3.12/library/timeit.html> — `timeit`, `repeat`, `Timer.autorange`, callable statements, setup behavior, and default GC handling.
- Python 3.12 `time`: <https://docs.python.org/3.12/library/time.html> — `perf_counter` and clock semantics.
- `pyperf` command-line documentation: <https://pyperf.readthedocs.io/en/latest/cli.html> and API documentation: <https://pyperf.readthedocs.io/en/latest/api.html>.
- `pytest-benchmark` usage and options: <https://pytest-benchmark.readthedocs.io/en/stable/usage.html>.
- `asv` commands and long-term benchmark workflow: <https://asv.readthedocs.io/en/stable/commands.html> and <https://asv.readthedocs.io/en/stable/using.html>.
- CPython command-line environment options, including build-dependent `PYTHON_JIT`: <https://docs.python.org/3.13/using/cmdline.html>.

These references verify tool/API claims; they do not constitute evidence that the commands were executed in this environment or that any performance result generalises to production.

## 21. Completion criteria

- [ ] I can use `timeit.timeit`, `timeit.repeat`, `Timer.autorange`, and `python -m timeit` correctly.
- [ ] I separate setup, timed work, warm-up, and validation.
- [ ] I compare equivalent work on identical and representative inputs.
- [ ] I can explain minimum, median, spread, effect size, and uncertainty without overstating a result.
- [ ] I have run the list-versus-set benchmark at several sizes and recorded actual results from my own machine.
- [ ] I understand the roles of `pyperf`, `pytest-benchmark`, and `asv`.
- [ ] I have considered GC, caches, CPU state, runtime/build, and cold/warm effects.
- [ ] I have connected a microbenchmark to the shared `slowlog` workload and checked correctness.
- [ ] I can propose a CI regression gate that accounts for noise and stores evidence.
- [ ] I have written a reproducible benchmark report with limitations and a defensible conclusion.

**Next:** Lesson 04 — `04-tracemalloc-and-memory-leak-hunting.md`.
