# cProfile, pstats and Flame Graphs

> **Stage 1 — Programming & Computational Thinking · Module 17 · Lesson 01**  
> Target runtime: **Python 3.12+**. The core APIs in this lesson also work on earlier supported CPython versions unless explicitly noted. Commands assume a shell in the project environment.

## 1. Why this lesson matters

Performance intuition is unreliable. A loop that looks complicated may be cheap, while a tiny helper called millions of times may dominate runtime. Profiling gathers evidence about where execution time and call activity are concentrated. The goal is not to make every function faster; it is to identify the few changes that can materially improve the workload while preserving correctness and maintainability.

The governing sequence is:

1. Define the workload and the performance question.
2. Establish a repeatable baseline and verify correctness.
3. Profile representative input.
4. Form a specific hypothesis from the profile.
5. Make one focused change.
6. Re-run correctness checks and collect a second profile.
7. Compare evidence, document limitations, and decide whether the change is worth keeping.

A profile is evidence, not a verdict. It can reveal expensive functions and call patterns, but it does not automatically explain why a function is expensive, prove a root cause, or establish production latency.

## 2. Prerequisites and learning objectives

### Prerequisites

You should be comfortable with Python functions and call stacks, loops, lists, dictionaries and sets, file/CSV processing, command-line execution, tests and assertions, and the idea that algorithmic complexity affects runtime. The broader module also expects the profiling mindset from Module 1.10 lesson 06, the object/generator concepts from Module 1.9, and testing/CI foundations from Modules 1.7 and 1.16.

### By the end, you should be able to

- Run `cProfile` from the command line or around a selected section of code.
- Interpret `ncalls`, `tottime`, `cumtime`, and `percall` without confusing inclusive and exclusive time.
- Use `pstats.Stats` to sort, filter, inspect callers and callees, and save/reopen profiles.
- Choose a visualization tool and read its representation correctly.
- Narrow a suspicious function with `line_profiler` only after function-level evidence points there.
- Explain deterministic profiler overhead and limitations across threads, async tasks, and processes.
- Use a profile to construct a hypothesis, apply Amdahl's law, compare before/after evidence, and create a useful CI artifact.
- Produce a reproducible performance investigation report.

## 3. Concept sequence: measurement before optimization

### 3.1 What profiling is—and is not

**Profiling** records execution observations such as function calls and timing. **Deterministic profiling** instruments function-call/return events and records the observed events rather than periodically sampling stacks. Python's `cProfile` is a deterministic profiler implemented largely in C to reduce the overhead of the profiling machinery relative to the pure-Python `profile` module.

Use it when you need to answer questions such as:

- Which Python functions account for the most inclusive runtime?
- Which functions spend the most time in their own bodies?
- Is an expensive helper being called far more often than expected?
- Which caller leads into a hot function, and what functions does it call?

It is less suitable for measuring exact production latency, low-overhead continuous observation, or attributing every native instruction inside a C extension. It also does not replace a benchmark, a memory profiler, a database query plan, or system-level observability.

**Measurement first** matters because optimizing a non-bottleneck has little effect on end-to-end runtime. First verify the program does the right thing. Then measure it under a representative workload. Avoid changing multiple things at once: otherwise you cannot attribute the result to a specific change.

### 3.2 The main time concepts

For a profiled function:

- **Internal/exclusive time (`tottime`)**: time attributed to the function body itself, excluding time spent in its subcalls.
- **Cumulative/inclusive time (`cumtime`)**: time spent in the function and all subcalls beneath it. Nested cumulative times overlap, so adding `cumtime` values across rows double-counts time.
- **Call count (`ncalls`)**: number of calls observed. For recursive functions, the column can show `total/primitive`, such as `120/1`: 120 calls in total and 1 primitive (non-recursive) call. A primitive call is one that was not itself entered through recursion; this distinction affects how per-call values are calculated.
- **Per-call (`percall`)**: a time divided by a call count. Standard `pstats` output has a per-call value for internal time and another for cumulative time. Read the column position and header carefully: the denominators differ for recursive functions, so these values need not match.

A function with high `cumtime` but low `tottime` is often a coordinator whose callees do the work. Inspect its callees and callers. A function with high `tottime` is a candidate for expensive work directly in its body. High call count can also matter even when each call is cheap.

### 3.3 Amdahl's law: why the biggest fraction matters

If a fraction `p` of total runtime is improved by a factor `s`, the idealized overall speed-up is:

\[
S = \frac{1}{(1-p) + p/s}
\]

If a component accounts for 30% of runtime and becomes twice as fast, the ideal total speed-up is `1 / (0.70 + 0.30/2) ≈ 1.176`, or about 17.6% faster overall—not 2×. Real outcomes can differ because costs move, contention changes, or the profile itself has overhead. Use this law to prioritize effort, not to predict exact benchmark results.

## 4. First run: profile a script

Create a small file named `profile_demo.py`:

```python
from collections import Counter


def normalize(value: str) -> str:
    return value.strip().lower()


def count_words(lines: list[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in lines:
        for word in line.split():
            counts[normalize(word)] += 1
    return counts


def main() -> None:
    lines = ["INFO worker ready", "WARN queue full", "INFO worker ready"] * 10_000
    counts = count_words(lines)
    print(f"unique words: {len(counts)}; total words: {sum(counts.values())}")


if __name__ == "__main__":
    main()
```

Run the program normally first:

```bash
python profile_demo.py
```

Then profile and save the raw profile data:

```bash
python -m cProfile -o out.prof profile_demo.py
```

The command executes the script and writes a binary `.prof` file. The profile is data, not a human-readable report. Keep it alongside the exact code revision, input description, Python version and command that produced it.

Print a report sorted by cumulative time:

```bash
python -m cProfile -s cumtime profile_demo.py
```

Other useful sort keys include `tottime`, `calls`, `pcalls`, `name`, and `filename` where supported by the `pstats` interface. Prefer the standard spelling `cumulative` when using `pstats.Stats.sort_stats()`; the CLI accepts the abbreviated `cumtime` form shown above.

### 4.1 How to read the output

A typical report has columns resembling:

```text
   270,000 function calls in 0.350 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.010    0.010    0.350    0.350 profile_demo.py:17(main)
        1    0.090    0.090    0.340    0.340 profile_demo.py:8(count_words)
    90000    0.060    0.000    0.090    0.000 profile_demo.py:4(normalize)
```

**This is illustrative output only.** Timings and call counts vary with Python version, platform, and the exact script. Do not expect these numbers from your machine. The example demonstrates the shape and column meanings; actual reports usually include additional rows for built-ins and interpreter support functions.

Interpretation:

1. Start with the top 10 rows sorted by cumulative time. This points to the parts of the call tree that own the most inclusive time.
2. Re-sort by `tottime`. This helps distinguish a function doing expensive work itself from one whose callees dominate.
3. Read `ncalls` before optimizing. A tiny function called millions of times can create substantial total overhead.
4. Inspect callers and callees before concluding that a function is the root cause.
5. Do not sum the `cumtime` column. Nested rows count some of the same time more than once.

## 5. Profile a selected region in Python

Use `cProfile.Profile()` as a context manager when you want to profile a particular operation rather than imports, setup, and unrelated work. Context-manager support is available in modern Python versions; this lesson targets Python 3.12+.

```python
import cProfile
import pstats


def main() -> None:
    # Replace with the workload you want to investigate.
    values = [str(number) for number in range(100_000)]
    normalized = [value.strip().lower() for value in values]
    print(len(normalized))


if __name__ == "__main__":
    with cProfile.Profile() as profiler:
        main()

    stats = pstats.Stats(profiler)
    stats.strip_dirs().sort_stats("cumulative").print_stats(15)
```

The context manager enables profiling on entry and disables it on exit. The profile is available through the `Profile` object and can be wrapped in `pstats.Stats` for inspection. Profiling only the target region reduces unrelated noise, but make sure setup costs that matter to the real workload are not accidentally excluded.

To write a profile from a selected region:

```python
profiler.dump_stats("selected-region.prof")
```

To load it later:

```python
import pstats

stats = pstats.Stats("selected-region.prof")
stats.strip_dirs().sort_stats("cumulative").print_stats(20)
```

A `.prof` file is normally tied to the program execution that generated it. Preserve the matching source revision and input/workload details; comparing profiles produced by different Python versions or materially different inputs can be misleading.

## 6. Working with `pstats.Stats`

`pstats` is the standard-library reporting layer for profile data. It lets you sort, filter, inspect call relationships, and print reports without rerunning the workload.

### 6.1 The core methods

```python
import pstats

stats = pstats.Stats("out.prof")
stats.strip_dirs()                 # shorten paths in displayed function keys
stats.sort_stats("cumulative")    # inclusive time, largest first
stats.print_stats(15)              # first 15 matching rows
```

Important operations:

- `strip_dirs()` removes directory prefixes from filenames in report keys to make output easier to read. It can make functions with identical basenames harder to distinguish, so retain the original profile and use full paths when that distinction matters.
- `sort_stats(*keys)` sorts by one or more supported keys. Common keys include `"cumulative"`, `"tottime"`, `"calls"`, `"pcalls"`, `"name"`, and `"filename"`. Valid keys depend on Python's `pstats` documentation; prefer documented constants/strings for your target version.
- `print_stats(*restrictions)` prints the report. Restrictions can limit the number of rows or filter by a string/regular expression. Apply filters after sorting when you want the highest-ranked matching rows.
- `print_callers(function)` displays which functions call the selected function.
- `print_callees(function)` displays functions called by the selected function.
- `dump_stats(filename)` saves profile data to a file.
- `add(*filenames)` combines compatible profile files. Merging can be useful for separate processes, but only when profiles represent comparable code/workload and the merge's interpretation is understood.

### 6.2 Filtering a report

```python
import pstats

stats = pstats.Stats("out.prof")
stats.strip_dirs().sort_stats("cumulative")
stats.print_stats(r"parse|normalize|aggregate")
```

The regular expression filters function entries by their displayed function identity (filename, line number and function name). It does not magically filter source lines within a function. If you filter too early or too narrowly, you can hide the caller that explains why a function is hot. First inspect the broad top-level report, then filter to investigate a hypothesis.

To inspect a call relationship, use a function identifier that matches the report's function key, or call the method with a suitable string restriction:

```python
stats.print_callers("normalize")
stats.print_callees("count_words")
```

The exact formatting of caller/callee details varies by Python version and by whether the selected function identity is unambiguous. If several functions share a name, use the full `filename:line(function)` identity printed in the report or inspect the full report first.

For pytest suites, the optional `pytest-profiling` plugin provides profile-oriented test-run workflows; its options and command-line flags are plugin-version-specific. Install the plugin in the project environment and confirm its installed help/documentation before using a command such as `pytest --profile`—do not assume that flag exists in plain pytest. For a one-off investigation, profiling a script entry point or a narrowly selected function is often simpler and easier to reproduce.

### 6.3 Callers and callees: a practical reading strategy

Suppose `parse_timestamp()` appears near the top of cumulative time. That observation alone does not tell you whether timestamp parsing is intrinsically slow or simply called far too often.

- **Callers** answer: who invokes it, and how frequently?
- **Callees** answer: what work happens below it?
- **Call count** answers: is the work repeated more often than the business requirement suggests?
- **Internal time** answers: is the function itself expensive, excluding its children?

For example, a high cumulative time in `process_file()` may be expected because it coordinates parsing, validation, database calls, and output. The useful next question is which child dominates and whether the number of calls is expected. For an N+1 database pattern, the Python profile may show a query wrapper called once per row; the database's own query metrics are still needed to understand database execution time accurately.

## 7. Visualization: call trees and flame graphs

Text reports are often enough to find a hot function. Visualizations help when a call tree is deep, many callers converge on a shared helper, or a profile contains many rows.

### 7.1 SnakeViz

SnakeViz presents `cProfile` data as an interactive visualization (commonly a sunburst/icicle-style view). It is useful for exploring nested calls and drilling into a hot branch.

Install it in a development environment:

```bash
uv add --dev snakeviz
```

Create and open a profile:

```bash
python -m cProfile -o etl.prof etl.py data/sample.csv
uv run snakeviz etl.prof
```

The second command starts the local visualization server/browser workflow. Keep the profile and its matching source available. Avoid sharing profiles from sensitive production systems without reviewing their paths, function names, and other metadata.

### 7.2 `gprof2dot` and Graphviz

`gprof2dot` converts supported profiler output into a call-graph description; Graphviz renders it. Install `gprof2dot` in the project environment (for example, `uv add --dev gprof2dot`) and install Graphviz separately through the operating system/package manager. Graphviz's `dot` executable must be available on `PATH`.

A typical workflow is:

```bash
python -m cProfile -o etl.prof etl.py data/sample.csv
uv run gprof2dot -f pstats etl.prof | dot -Tsvg -o callgraph.svg
```

Check `gprof2dot --help` for the installed version's supported input formats and options. Call graphs show relationships and weighted nodes/edges; a large node can be a useful entry point, but graph labels and weights depend on the converter and options. Do not assume every graph uses exactly the same inclusive/exclusive metric.

### 7.3 Flame graphs and width semantics

A flame graph arranges stack traces so that each horizontal frame's width represents the amount of observed activity attributed to that stack/frame under the tool's aggregation rules. **Width is not a timeline**: adjacent x positions do not mean “earlier” and “later.” The vertical axis represents stack depth, with callers below callees in the usual flame-graph convention. Depending on the renderer, widths may represent sampled stack counts or time attributed from deterministic profile data; always identify the source and tool before interpreting them.

The data source determines the meaning of width:

- `cProfile` records deterministic function events and is often visualized as a call tree or converted into a graph.
- `py-spy` samples stack traces from a running process; its flame graph width reflects sample counts, an estimate of observed activity over the sample interval. After installing `py-spy` and checking permissions for the target process, a common command is `py-spy record --format flamegraph -o flame.svg -- python etl.py data/big.csv`. This is a sampling profile, not a `cProfile` report. The command's options and operating-system permissions should be checked against the installed `py-spy` version.
- `flameprof` can render `cProfile` data in a flame-graph style. Install it in the project environment if available (for example, `uv add --dev flameprof`), then check `uv run flameprof --help` for the installed version's exact syntax and output format; a common form is `uv run flameprof etl.prof > flame.svg`.

Do not conflate deterministic and sampling profiles. A sampled profile is a statistical estimate and may miss short-lived functions between samples. A deterministic profile sees call events but can impose substantial overhead, especially when the workload makes millions of small calls.

## 8. Narrow a function with `line_profiler`

Function-level profiling should normally come first. Once the profile suggests that one Python function is expensive, line-level profiling can identify which statements inside it deserve attention.

Install the development tool:

```bash
uv add --dev line_profiler
```

The conventional `kernprof` workflow uses a `@profile` decorator injected by the runner. A script can define a fallback decorator so normal execution does not require `kernprof` to inject the name. This is the legacy-compatible workflow; `line_profiler` 4.1+ also supports an explicit `from line_profiler import profile` decorator, which is a no-op unless line profiling is enabled according to that version's documentation:

```python
try:
    profile
except NameError:
    def profile(function):
        return function

@profile
def transform_rows(rows):
    output = []
    for row in rows:
        timestamp = row["timestamp"].strip()
        level = row["level"].upper()
        output.append((timestamp, level, row["message"].strip()))
    return output


if __name__ == "__main__":
    sample_rows = [
        {"timestamp": " 2026-01-01T12:00:00Z ", "level": "info", "message": " worker ready "},
        {"timestamp": " 2026-01-01T12:01:00Z ", "level": "warn", "message": " queue full "},
    ]
    print(transform_rows(sample_rows))
```

Run it with the installed tool, for example:

```bash
kernprof -lv line_target.py
```

Consult `kernprof --help` and the installed `line_profiler` version if command options differ. Line-level timings add their own overhead and are not a production latency benchmark. Use the line profile to form a more specific hypothesis, then validate the change with an ordinary workload run and a function-level profile or benchmark.

## 9. The slowlog project: a deliberately inefficient CSV analytics workload

This section provides one coherent exercise: process CSV log events and count records by severity. The intentionally poor implementation repeatedly rebuilds a list of accepted levels inside the row loop. That repeated setup is easy to miss in code review and provides a profile-led optimization opportunity. The workload is synthetic and self-contained; replace generated input with a representative, sanitized data fixture when applying the method to a real pipeline.

### 9.1 Create `slowlog.py`

```python
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ACCEPTED_LEVELS = ("INFO", "WARN", "ERROR")


def generate_csv(path: Path, rows: int) -> None:
    """Create deterministic sample input for repeatable local experiments."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("timestamp", "level", "message"))
        writer.writeheader()
        for index in range(rows):
            level = ACCEPTED_LEVELS[index % len(ACCEPTED_LEVELS)]
            writer.writerow({
                "timestamp": f"2026-01-{(index % 28) + 1:02d}T12:00:00Z",
                "level": level.lower() if index % 7 == 0 else level,
                "message": f"worker={index % 17} processed record {index}",
            })


def analyze_slow(path: Path) -> dict[str, int]:
    counts: Counter[str] = Counter()
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            # Deliberately inefficient: recreate a list for every row and then
            # perform membership against that list.
            accepted = list(ACCEPTED_LEVELS)
            level = row["level"].strip().upper()
            if level in accepted:
                counts[level] += 1
    return dict(sorted(counts.items()))


def analyze_fast(path: Path) -> dict[str, int]:
    counts: Counter[str] = Counter()
    accepted = frozenset(ACCEPTED_LEVELS)
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            level = row["level"].strip().upper()
            if level in accepted:
                counts[level] += 1
    return dict(sorted(counts.items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--generate", type=int, metavar="ROWS",
                        help="generate deterministic sample input, then exit")
    parser.add_argument("--mode", choices=("slow", "fast"), default="slow")
    parser.add_argument("--json", action="store_true", help="print result as JSON")
    args = parser.parse_args()

    if args.generate is not None:
        if args.generate < 0:
            parser.error("ROWS must be non-negative")
        generate_csv(args.csv_path, args.generate)
        return

    result = analyze_slow(args.csv_path) if args.mode == "slow" else analyze_fast(args.csv_path)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(result)


if __name__ == "__main__":
    main()
```

The slow and fast implementations intentionally have the same output contract. `frozenset` is used for a fixed membership collection, and it is created once outside the row loop. The main hypothesis is not “sets are always faster”; it is that the slow implementation repeatedly allocates and fills a list even though the accepted levels do not change. On larger inputs, this repeated work may show up in the profile. Measure it rather than assuming the magnitude of the benefit.

### 9.2 Generate representative input and check correctness

Create the `data` directory first if it does not exist, then generate the deterministic fixture and compare the outputs:

```bash
mkdir -p data
python slowlog.py data/slowlog.csv --generate 200000
python slowlog.py data/slowlog.csv --mode slow --json
python slowlog.py data/slowlog.csv --mode fast --json
```

Both modes should produce the same counts for the same file. Verify that explicitly before comparing performance. A reusable correctness check can be kept in `test_slowlog.py`:

```python
import tempfile
import unittest
from pathlib import Path

from slowlog import analyze_fast, analyze_slow, generate_csv


class SlowlogTests(unittest.TestCase):
    def test_fast_and_slow_match(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            generate_csv(path, 500)
            self.assertEqual(analyze_slow(path), analyze_fast(path))

    def test_empty_input_has_empty_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            generate_csv(path, 0)
            self.assertEqual({}, analyze_slow(path))
            self.assertEqual({}, analyze_fast(path))


if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
python -m unittest -v
```

For a real ETL pipeline, add malformed-row, unexpected-level, empty-file, encoding, and failure-path tests according to the actual input contract. The small tests above establish parity for the example; they do not constitute complete production data-quality validation.

### 9.3 Collect a baseline profile

Profile the slow implementation with a representative row count:

```bash
python -m cProfile -o slow-before.prof slowlog.py data/slowlog.csv --mode slow --json
python -m cProfile -s cumtime slowlog.py data/slowlog.csv --mode slow --json
```

Inspect the saved profile with a focused script, `pstats`:

```bash
python - <<'PY'
import pstats

stats = pstats.Stats("slow-before.prof")
stats.strip_dirs().sort_stats("cumulative").print_stats(20)
print("\nHighest internal-time rows")
stats.sort_stats("tottime").print_stats(20)
PY
```

The profile may show CSV parsing and row processing as major costs, and it may show many calls to list construction or membership-related operations. Exact function names, call counts, timing values and ranking depend on Python version and profiler attribution. **Do not copy invented timings into your report.** Save the actual output from your own environment.

Use the evidence to test the hypothesis. If the profile does not show the repeated list work as material, investigate the actual hot path instead of forcing the expected answer. File I/O, the CSV parser, string normalization, or the overall workload shape may dominate for a particular input.

### 9.4 Apply the focused optimization and profile again

The change is to create a `frozenset` once per analysis call rather than a list on every row. The `analyze_fast()` function above implements that change. Run the same data through both paths, verify identical counts, then collect the second profile:

```bash
python -m cProfile -o slow-after.prof slowlog.py data/slowlog.csv --mode fast --json
python -m cProfile -s cumtime slowlog.py data/slowlog.csv --mode fast --json
```

Inspect both profiles with the same reporting commands. A simple manual comparison:

```bash
python - <<'PY'
import pstats

for filename in ("slow-before.prof", "slow-after.prof"):
    print(f"\n===== {filename} =====")
    pstats.Stats(filename).strip_dirs().sort_stats("cumulative").print_stats(15)
PY
```

The two profile runs should use the same input, environment, Python build, and comparable command path. The slow/fast mode dispatch itself is small, but the profile includes command-line parsing and output. For a cleaner comparison, profile only the analysis function in a dedicated harness or call it from a context-managed `cProfile.Profile` around the same function. Also run unprofiled timings separately; do not treat profiled wall time as production latency.

### 9.5 What counts as evidence?

A defensible conclusion should include:

- The input path or fixture identity, row count and relevant data shape.
- Python version, OS/CPU context, command and revision.
- Correctness parity between the two implementations.
- The top cumulative and internal-time rows before and after.
- Call-count changes that support the hypothesis (for example, list construction should no longer occur once per row in the optimized path).
- Repeated unprofiled wall-clock measurements under controlled conditions if making a speed claim.
- Trade-offs and residual bottlenecks. Once the repeated allocation is removed, CSV parsing or normalization may become a larger share of total time even if its absolute cost barely changes.

No fixed speed-up is promised. The purpose is to demonstrate the investigation method, not to guarantee a particular benchmark result.

## 10. Representative workloads and profiler overhead

### 10.1 Use realistic inputs

A toy dataset may not reveal the dominant cost at production scale. Match the workload's important properties: row count, row width, field cardinality, malformed-input rate, number of files, cache state, database/network behavior, and concurrency. If a pipeline has separate extract, parse, transform, join and write stages, profile both end-to-end and targeted stages when necessary.

Use warm-cache and cold-cache runs intentionally. Do not compare a warm-cache optimized run with a cold-cache baseline. Run multiple times and record the spread. Keep inputs deterministic when possible and avoid background jobs that compete for CPU or I/O.

### 10.2 Deterministic profiling changes the workload

`cProfile` incurs work when function calls/returns are observed and recorded. Its relative overhead can be large when a workload consists of many tiny Python function calls. The profiler can change timings and sometimes change the apparent ranking or relative proportions of functions. Therefore:

- Use profiles to find structure, call counts and candidate hotspots.
- Use unprofiled timing/benchmarking to evaluate end-to-end latency or throughput.
- Compare profiled runs to other profiled runs only when the setup is controlled and the profiler overhead is understood.
- Do not report profiled runtime as production latency.

The profile is not “wrong” because it adds overhead; it answers a different question under instrumentation. For lower-overhead observation of a running process, the neighboring lesson covers sampling profilers such as `py-spy`.

## 11. Advanced interpretation cases

### 11.1 Recursion and cumulative time

Recursive calls complicate reading because a function may appear both as a recursive call and as a primitive call. `cumtime` includes time in descendants, including recursive descendants, so do not sum it across rows or treat the same inclusive time as independent work. Look at the recursive call count notation and inspect the caller/callee relationships.

### 11.2 Built-ins and C functions

Built-ins and extension functions may appear with names such as `{built-in method ...}` or similar runtime-specific labels. The profile can show time attributed to a C-level call as a unit, but it generally does not give Python source-line detail inside that native implementation. A high cost in a C-backed operation is not proof the C implementation is inefficient; the operation may be doing a lot of work or processing a large input. Consider the amount of data, call count, algorithm, and library-specific tools.

### 11.3 Generators, comprehensions and lambdas

Generators suspend and resume execution; time may be attributed across generator frames and the caller that consumes them. A generator expression's work often occurs as it is iterated, not when the generator object is created. Comprehensions and lambdas can appear under generated or source-associated names depending on Python version. Do not infer that an expression is cheap merely because object creation is cheap—the work may be attributed to iteration or to an enclosing call. Map profile entries back to source and inspect the call tree.

### 11.4 `async` functions and waiting

`cProfile` observes function-call events in the thread where profiling is active; it is not an async-aware distributed tracer. A coroutine is suspended while an `await` waits for an event or I/O completion, so the elapsed wait generally should not be interpreted as CPU time spent executing that coroutine. Time in nested Python functions that actually execute can appear in the profile, and synchronous blocking work on the event-loop thread can delay other tasks, but the profile alone does not reliably explain remote service latency, queueing, or time spent suspended. Correlate with request timings, async-aware tracing/instrumentation, event-loop diagnostics, and external service metrics. Be explicit about whether the metric is CPU time, elapsed request latency, or wait time.

### 11.5 Threads and multiprocessing

A `cProfile.Profile` instance generally instruments the thread in which it is enabled; profiling the main thread does not automatically produce a complete profile for every other thread. To study threaded work, arrange profiling for each relevant thread (for example by creating/enabling a profile within that thread) and keep the profiles distinct until you understand their meaning. Thread support details can depend on Python version and how the application creates threads; verify the API behavior for the exact runtime.

Each multiprocessing worker is a separate process. A profile saved by the parent process does not include worker execution that happened in other processes. Instrument each worker or run each worker's workload under a profiler, write one profile per process, and merge only comparable profiles when aggregation makes sense. Preserve worker identifiers and avoid concurrent workers overwriting the same profile path.

In all cases, first decide whether you need CPU time, wall time, waiting time, per-thread behavior, or end-to-end throughput. A single deterministic profile cannot answer every concurrency question.

## 12. Differential profiling and CI evidence

### 12.1 Compare before and after carefully

A differential investigation compares a baseline profile with a profile after one change. Keep constant:

- Input fixture and workload parameters.
- Python version/build and dependencies.
- Profiling scope and command options.
- Machine conditions as far as practical.
- Correctness contract and output verification.

Look for both intended changes and unintended regressions. For example, a membership optimization may reduce repeated setup calls but expose string normalization as the next bottleneck. That does not mean the first change failed; it means the distribution of cost changed. Use the profile to decide whether another optimization is worthwhile.

Raw `.prof` files are not always easy to compare visually and their internal representation is not a stable cross-version interchange format. For formal comparisons, use a documented profile-diff tool compatible with your profile format, or generate normalized reports and compare those with the caveat that function identities and timings can shift across revisions. Never compare profiles from different workload sizes as if they were equivalent.

### 12.2 Performance checks in CI

Timing-based CI gates can be noisy because shared runners vary in CPU frequency, contention, filesystem cache, and virtualization. For this lesson, prefer stable structural evidence where appropriate:

- Correctness tests must always run.
- Assert that known repeated operations or calls do not grow unexpectedly with input size, where the behavior can be tested reliably.
- Save `.prof` files or text summaries as build artifacts for investigation.
- Run benchmarks on controlled/dedicated runners before enforcing strict latency budgets.
- Use repeated measurements and tolerant thresholds rather than failing on a single noisy run.

Do not make a brittle test that asserts exact wall-clock seconds. Also avoid asserting private implementation details unless the call-count contract represents a meaningful performance invariant. A test that merely verifies output equality cannot prove a speed improvement; profile/benchmark evidence is still required.

An example CI command sequence might be:

```bash
python -m unittest -v
python -m cProfile -o artifacts/slowlog.prof slowlog.py data/fixture.csv --mode fast --json
python -m cProfile -s cumtime slowlog.py data/fixture.csv --mode fast --json > artifacts/profile-summary.txt
```

Create `artifacts/` before running commands, and make sure the fixture is checked into the repository or generated deterministically. Configure your CI system to upload the artifacts on failure and, where useful, on success. The commands above illustrate a workflow; the exact artifact-upload syntax depends on the CI platform.

## 13. Common production bottlenecks to recognize

A profile often points toward one of these patterns. Treat each as a hypothesis to validate with the right data source.

| Pattern | Profile clue | Follow-up investigation |
|---|---|---|
| Repeated parsing/compiling (regex or timestamp formats) | Parser/compile helper called per row | Reuse compiled patterns or parsed format state where safe; validate cache behavior and input diversity. |
| N+1 database queries | Query wrapper called once per record or entity | Inspect database query logs/plans and network timing; batch queries if semantics allow. |
| Inefficient membership checks | Membership helper inside a large loop; list scans repeated | Check collection cardinality and access pattern; compare list/set/dict choices with representative input. |
| Logging overhead | Formatting, handlers or I/O prominent, especially in hot loops | Check log level, eager string formatting, handler configuration and output destination. Do not suppress required audit logs blindly. |
| JSON encode/decode | Serializer/deserializer high in cumulative or internal time | Measure payload size, repeated conversion, schema and alternative libraries; preserve wire-format compatibility. |
| Row-wise pandas `apply` | Python callback dominates large table processing | Consider vectorized/columnar operations in the appropriate data-engineering stage; verify null/type semantics. |
| Repeated string concatenation | Many concatenation operations and growing strings | Check whether repeated copying is occurring; collect fragments and join when appropriate. |
| Excessive tiny function calls | Very high call count, moderate per-call cost | First remove repeated work or improve algorithm/data layout; only inline helpers if evidence supports it. |
| Serialization/copying across processes | Pickle/encode/decode and worker handoff costs | Measure payload sizes, batching, shared-memory options and total parallel efficiency. |

The function profile is one layer of evidence. Use database plans, distributed traces, OS metrics, sampling profiles, or memory tools when the question falls outside its visibility.

## 14. `sys.monitoring` and newer profiling APIs

Python 3.12 introduced `sys.monitoring`, a low-level monitoring interface that lets tools register callbacks for selected interpreter events. It is part of the evolving runtime instrumentation landscape and is relevant when designing profilers, debuggers, coverage tools, or specialized monitoring. It is **not the same API as `cProfile`** and should not be treated as a drop-in replacement for `cProfile.Profile` or `pstats.Stats`.

The broader module roadmap flags newer low-overhead profiling APIs and later-version developments for awareness. Their availability and behavior are version-specific; verify the official documentation for the Python version you deploy rather than assuming a future API is present in every Python 3.12+ environment. This lesson focuses on the stable, widely used `cProfile`/`pstats` workflow.

## 15. Troubleshooting

### The profile is dominated by `main()` or a top-level function

That function may coordinate most of the workload. Sort by `cumtime`, inspect its callees, and profile a narrower region only after confirming what setup is included. Do not assume the top row itself needs rewriting.

### The top rows change between runs

Check input size/shape, cache warmth, background load, CPU frequency, external I/O, and whether the run is too short. Repeat the workload, record the spread, and use a representative fixture. Deterministic instrumentation does not eliminate environmental noise.

### The profile says a function is cheap, but the job is slow

The delay may be in another process/thread, waiting on I/O, a remote database/service, or native code that the current profile does not break down. Confirm the instrumented scope and use a sampling profiler, trace, query metrics, or system tools as appropriate.

### A saved profile cannot be interpreted as expected

Use the same Python version and source revision if possible. Check that the file is a real `cProfile` output and was not overwritten by concurrent workers. Use `pstats.Stats("file.prof")` to confirm it loads, and keep the exact command with the artifact.

### `snakeviz`, `kernprof`, `gprof2dot` or `dot` is not found

Confirm the development environment is active and the dependency is installed. Check `uv run <command> --help` or the tool's installed help. `dot` is supplied by Graphviz, not by Python's standard library. Some operating systems require installing Graphviz separately.

### Profiled time is much slower than normal time

That is expected for some workloads, especially many small function calls. Use the profile to understand call structure; use repeated unprofiled runs or a benchmark tool to measure actual latency.

## 16. Common mistakes checklist

- [ ] Optimizing based on intuition or a toy input rather than representative evidence.
- [ ] Reading only `tottime` and ignoring expensive callees—or reading only `cumtime` and mistaking a coordinator for the root cause.
- [ ] Summing cumulative times, which double-counts nested work.
- [ ] Comparing profiled wall-clock time directly with unprofiled production latency.
- [ ] Treating a profile from one thread or process as a complete application profile.
- [ ] Treating flame-graph width as time order rather than aggregated activity.
- [ ] Making several changes before collecting the next profile.
- [ ] Reporting a speed-up without correctness checks, repeated unprofiled timing, and workload details.
- [ ] Assuming a visualization tool's node/edge weight means the same thing across formats.
- [ ] Publishing sensitive production profiles without reviewing their metadata.

## 17. Practical exercises

### Exercise 1 — column literacy

Run `profile_demo.py` under `cProfile`. Write down the five largest cumulative-time entries and the five largest internal-time entries. For two functions, explain why their ranking changes between the reports. Do not use the illustrative output as your answer.

### Exercise 2 — caller/callee investigation

Choose one high-cumulative-time function. Record its callers, callees and call counts. State a hypothesis that can be tested. Explain what evidence would disprove it.

### Exercise 3 — slowlog baseline and change

Run the slowlog example with at least two input sizes. Save a baseline profile, inspect both cumulative and internal time, optimize only after a profile-supported hypothesis, verify identical outputs, and save a second profile. Include actual output from your environment and identify the next bottleneck, if any.

### Exercise 4 — visualization comparison

Open one `.prof` file in SnakeViz and create a call graph with `gprof2dot`/Graphviz if available. Compare what each visualization makes easy to see and what it hides. Explain the meaning of width/weights for the specific tool used.

### Exercise 5 — concurrency scope

Create a small program that performs work in a worker thread or process. Profile the parent, then instrument the worker and compare the resulting evidence. Explain why the first profile did or did not include the worker's work. Do not merge profiles until you can explain what each represents.

### Exercise 6 — CI evidence design

Write a short CI plan that runs correctness tests, saves a profile artifact, and avoids a fragile exact-seconds assertion. Identify one meaningful call-count or workload invariant and explain why it matters to performance.

## 18. Self-check questions

1. What is the difference between `tottime` and `cumtime`? Why should cumulative times not be added across rows?
2. Why can deterministic profiling mislead when code makes millions of tiny calls?
3. What does a high cumulative time with low internal time suggest? What should you inspect next?
4. How do `strip_dirs`, `sort_stats`, `print_stats`, `print_callers` and `print_callees` support an investigation?
5. How does a sampled flame graph differ from a visualization of deterministic profile data? What does width mean in each case?
6. Why should `line_profiler` usually be applied after function-level profiling?
7. Why does a profile in the main thread or parent process not automatically represent all worker activity?
8. How does Amdahl's law constrain the impact of optimizing a function that accounts for only a small fraction of runtime?
9. What evidence would you require before claiming that the slowlog optimization improved performance?
10. What is `sys.monitoring`, and why should it not be confused with `cProfile`?

## 19. Final hands-on investigation and report template

Complete the investigation on the slowlog workload or a similarly representative log/CSV ETL script. Fill every field with measured evidence; if a value was not measured, say so explicitly.

```markdown
# Performance Investigation: <workload and date>

## 1. Question and impact
- User/business impact:
- Performance symptom and target metric (latency, throughput, CPU, etc.):
- Scope included/excluded:

## 2. Environment and reproducibility
- Git revision:
- Python version/build:
- OS/CPU and relevant resource limits:
- Dependency versions:
- Exact command:
- Input fixture, row count, shape, and data characteristics:
- Cache state and run protocol:

## 3. Correctness baseline
- Expected behavior/output:
- Tests run and results:
- Data-quality assumptions and edge cases:

## 4. Baseline measurements
- Unprofiled timing method and repeated results/spread:
- Throughput or other relevant metrics:
- Profile artifact path:
- Top cumulative-time functions:
- Top internal-time functions:
- Important call counts and caller/callee observations:
- Profiler overhead/limitations:

## 5. Hypothesis
- Profile evidence:
- Proposed cause:
- Prediction that could disprove the hypothesis:

## 6. Change
- Minimal code change:
- Why it should help:
- Correctness or compatibility risks:

## 7. Verification and comparison
- Correctness tests after change:
- Same-workload second profile and artifact path:
- Before/after call-count and profile observations:
- Repeated unprofiled timings/spread:
- Other metrics and any regressions:
- Amdahl's-law estimate, if useful, with assumptions:

## 8. Decision and follow-up
- Keep/revert decision and rationale:
- Remaining bottleneck:
- Operational risks and rollback plan:
- Reproduction steps for another engineer:
```

### Completion criteria

The investigation is complete only when the output is correct, the profile supports the hypothesis, the optimization is narrow and explainable, the second profile has been collected under comparable conditions, and the report distinguishes measured results from interpretation. A visually attractive flame graph or a lower profiled runtime alone is not sufficient proof.

## 20. Lesson summary

`cProfile` and `pstats` help answer where Python execution time and calls are concentrated. Begin with cumulative time to find expensive call paths, then internal time to find work done directly in a function. Inspect callers and callees before assigning root cause. Use visualizations to explore relationships, and line profiling only after narrowing the investigation. Keep workloads representative, account for deterministic profiler overhead, and treat thread/process boundaries explicitly. Finally, verify correctness and compare before/after evidence; use unprofiled measurements for performance claims and document the environment, workload, results, caveats, and trade-offs.

## References and version notes

- [Python 3.12 `profile` / `cProfile` documentation](https://docs.python.org/3.12/library/profile.html) — profiler behavior, `Profile`, command-line options and context-manager support.
- [Python 3.12 `pstats` documentation](https://docs.python.org/3.12/library/pstats.html) — sort keys, restrictions, callers/callees and report fields.
- [SnakeViz documentation](https://jiffyclub.github.io/snakeviz/) — interactive visualization of Python profile files.
- [`gprof2dot` project](https://github.com/jrfonseca/gprof2dot) — supported profile formats and graph conversion options.
- [`py-spy` project](https://github.com/benfred/py-spy) — sampling profiler and flame-graph command options.
- [`flameprof` on PyPI](https://pypi.org/project/flameprof/) — conversion of `cProfile` data to a flame-graph SVG.
- [`line_profiler` / `kernprof` documentation](https://kernprof.readthedocs.io/en/stable/auto/kernprof.html) — legacy `kernprof -l` and modern explicit decorator workflows.

The lesson targets Python 3.12+. Third-party CLI flags and compatibility vary by installed tool version; check the exact installed version's help and documentation before treating an example command as portable. The commands above are documented workflows, not a claim that optional tools were installed or executed during this audit.

**Next lesson:** `02-sampling-profilers-with-py-spy.md` covers lower-overhead stack sampling and investigation of running processes.
