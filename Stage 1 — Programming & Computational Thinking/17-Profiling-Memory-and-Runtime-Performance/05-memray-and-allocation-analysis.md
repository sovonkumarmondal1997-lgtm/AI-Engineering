# Lesson 05 — Memray and Allocation Analysis

> **Module:** Stage 1 — Programming & Computational Thinking → Module 1.17, Profiling, Memory and Runtime Performance  
> **Target:** Python 3.12+; verify compatibility for the exact interpreter, operating system, and Memray release in your environment.  
> **Position in sequence:** After `04-tracemalloc-and-memory-leak-hunting.md`; before `06-garbage-collector-and-reference-cycles.md`.  
> **Scope:** Attribute Python and native allocation activity, understand peaks, and validate a targeted pipeline change. This lesson is not a replacement for the `tracemalloc` or garbage-collection lessons.

## 1. Why allocation profiling matters

A process can use a lot of memory for several different reasons:

- It allocates a large object and keeps it alive.
- It repeatedly allocates temporary objects, creating high allocation churn.
- It reads an entire file or constructs multiple copies of the same data.
- A native extension allocates buffers that are not fully explained by Python-level tracing.
- A library retains a large base buffer through a small view.
- Memory is freed logically, but the allocator retains pages for reuse, so process RSS does not immediately fall.

These cases require different fixes. A report that says a function allocated many bytes does not, by itself, prove a leak. The function may be allocating temporary objects that are freed promptly. Conversely, a single large buffer can dominate peak memory even if the allocation count is small.

**Memray** is a memory profiler for Python applications that records allocation activity and its call stacks. It can trace Python and, with native tracing enabled, C/C++ stack frames. It produces a capture file that can be explored with reports such as flame graphs, tables, summaries, and statistics. It is especially useful when you need to answer “which call path allocated this memory?” or when Python-level allocation tracing does not explain the full picture.

The Module 1.17 roadmap uses a shared, deliberately inefficient log-analysis/ETL application called `slowlog`. This lesson uses a CSV-to-summary workload compatible with that project: read event rows, validate them, and aggregate by category. The exercise is to find the stage that drives memory use, propose a targeted change, preserve output correctness, and measure again. Do not assume a particular percentage improvement before running the workload.

## 2. Prerequisites and learning objectives

### Prerequisites

- Python objects, containers, iterators, generators, and object lifetime.
- The distinction between shallow size, traced Python memory, and process RSS.
- Basic profiling and command-line usage.
- CSV parsing and basic aggregation.
- Test discipline: correctness must remain invariant when the implementation changes.
- A working Python environment and permission to install development tools.

### Learning objectives

By the end of the lesson, you should be able to:

1. Install Memray and capture a representative program run.
2. Generate and interpret `flamegraph`, `table`, `summary`, and `stats` reports.
3. Distinguish total allocated bytes, allocation count, peak memory, and retained/live allocations.
4. Use `--native`, `--follow-fork`, and `--trace-python-allocators` when the investigation calls for them.
5. Use live tracking and attach workflows where supported, without assuming every platform supports every mode.
6. Identify large temporary objects, full-file reads, copies, intermediate DataFrames, oversized dtypes, and views that retain base buffers.
7. Compare a baseline and a change under the same workload and explain the limits of that comparison.
8. Add memory regression checks using the supported `pytest-memray` markers.
9. Set memory budgets that account for peak concurrency, native buffers, container limits, and operational headroom.
10. Produce a reproducible investigation report with evidence, trade-offs, and explicit limitations.

## 3. Install Memray and verify your environment

Memray installation and support depend on Python version, operating system, architecture, and distribution. Native tracing and process attachment can have additional platform requirements. Prefer an isolated project environment and check the current installation documentation before pinning a production version.

For a project using `uv`:

```bash
uv add --dev memray
uv run memray --help
uv run memray run --help
uv run memray flamegraph --help
uv run memray table --help
uv run memray summary --help
uv run memray stats --help
```

Or with pip in a virtual environment:

```bash
python -m pip install memray
python -m memray --help
```

The Memray documentation and command help for the installed version are authoritative for available options. If a wheel is unavailable for the target platform or Python version, follow the official installation instructions rather than assuming a source build will work without a compiler and system dependencies.

Official references:
- Memray project and overview: https://github.com/bloomberg/memray
- `memray run` CLI reference: https://bloomberg.github.io/memray/run.html
- `pytest-memray` usage and markers: https://pytest-memray.readthedocs.io/en/stable/usage.html

**Environment checklist**

- Record `python --version`, `python -c "import platform; print(platform.platform(), platform.machine())"`, and the Memray version.
- Use the same Python environment to run the workload and generate reports.
- Keep capture files and reports with the environment metadata; native symbol resolution may depend on the libraries and machine used to create the capture.
- Avoid capturing sensitive payloads or publishing allocation reports that reveal private file paths or application structure.
- For production, coordinate tracing duration and resource impact; native tracing can add noticeable overhead.

## 4. First capture: `memray run`

The basic workflow is:

```bash
uv run memray run -o out.bin script.py
```

Memray runs the target program and writes a binary capture file. `out.bin` is not a text report; pass it to a reporter.

For a script with arguments:

```bash
uv run memray run -o slowlog.bin slowlog.py --input data/events.csv
```

The target script must parse those arguments itself. If the application expects positional arguments, supply them after the script name exactly as its CLI expects.

To capture native C/C++ stack frames:

```bash
uv run memray run --native -o slowlog-native.bin slowlog.py --input data/events.csv
```

To record allocations in forked child processes:

```bash
uv run memray run --follow-fork -o slowlog-fork.bin slowlog.py --input data/events.csv
```

These options are not interchangeable. `--native` asks Memray to include native stack frames. `--follow-fork` follows child processes created by a fork-based process model. Neither guarantees that every form of multiprocessing, subprocess creation, GPU allocation, or external service memory is captured. Confirm the exact behavior for the process model and Memray version in use.

For more visibility into allocations made through Python's `pymalloc` allocator:

```bash
uv run memray run --trace-python-allocators -o slowlog-allocators.bin slowlog.py --input data/events.csv
```

This can provide allocator-level detail, but it changes the granularity and overhead of the capture. Use it when the extra visibility answers a specific question, not as the default for every run.

## 5. Generate the main reports

Run the reporter commands against the capture:

```bash
uv run memray flamegraph out.bin
uv run memray table out.bin
uv run memray summary out.bin
uv run memray stats out.bin
```

By default, the flame graph, table, and summary are oriented around allocations contributing to the process's heap high-water mark (peak). They do **not** summarize every allocation event over the entire run in the same way. Check `--help` for reporter-specific output options and filenames in your installed version. Reports are generated from the capture; they do not rerun the target application.

For the allocations that remain allocated when tracking ends, compare the default peak view with a leak-oriented view:

```bash
uv run memray flamegraph --leaks out.bin
uv run memray table --leaks out.bin
```

The `--leaks` option selects allocations made after tracking began that had not been deallocated when tracking stopped. That is an **end-of-capture allocation view**, not proof that the application has a semantic leak: caches and intentionally long-lived objects can remain allocated. With Python's normal allocator, freed Python objects may leave memory retained in allocator pools and can appear in leak-oriented output. For targeted investigations, the Memray documentation recommends considering `PYTHONMALLOC=malloc` alongside `--leaks`; this changes allocator behavior and is not a universal production setting or a substitute for interpreting the results.

### 5.1 Flame graph

```bash
uv run memray flamegraph out.bin
```

A flame graph organizes allocation call stacks. The width of a frame represents the amount of memory attributed to that frame under the selected report's accounting, not elapsed time and not the order in which events happened. A wide frame is a useful place to investigate because it accounts for a large portion of the reported allocation metric. A caller may be wide because its callees allocated the memory; distinguish inclusive/total attribution from memory directly allocated by the function itself.

Read the graph from the broader call paths down to the specific allocation site:

1. Find the widest relevant paths.
2. Follow a path toward the function or library call that creates the objects.
3. Determine whether the bytes represent a large one-off object, repeated temporary allocations, or a structure that remains alive.
4. Compare with the workload stages and correctness requirements.
5. Re-run after a targeted change using the same input and capture settings.

Do not read the horizontal axis as a timeline. Flame graphs aggregate call stacks; they do not show that one frame happened “before” another in time.

### 5.2 Table

```bash
uv run memray table out.bin
```

The default table is an HTML view of source locations whose allocations contributed to the process's peak memory usage. It reports the amount of memory attributed to those allocations, the allocator, and allocation count; it is not automatically a whole-run total-allocation ledger. Inspect whether the peak contribution is driven by many small allocations or a few large ones. If a report presents own and total/inclusive columns, do not confuse them: own allocation is attributed directly to a function, while inclusive totals can include callees. The table's exact columns and options depend on the installed Memray version; use its labels and CLI help.

### 5.3 Summary

```bash
uv run memray summary out.bin
```

The summary is a terminal report of allocation activity at the heap high-water mark. It distinguishes memory directly allocated by a function (“own memory”) from memory allocated by that function and its callees (“total memory”), and reports counts for allocations that were not yet freed at that point. Use it to identify prominent paths and decide where to drill down; it is not a whole-run total-allocation ledger or final root-cause explanation.

### 5.4 Stats

```bash
uv run memray stats out.bin
```

Statistics describe the capture's allocation activity and, in current Memray releases, include high-water/peak information as well as allocation statistics. Exact fields depend on the installed version and capture format; for example, an aggregated capture does not retain the per-allocation details required by every reporter, including `stats`. Use the installed command's help and report labels to establish exactly which metric is shown. Do not infer “leaked bytes” merely from a high total-allocation count.

### Illustrative report-reading example

The following is **illustrative only**. These values are not measurements and are not promised to match a Memray version's exact formatting.

```text
Function / call path              Total allocation bytes     Allocation count
parse_csv_rows                    420 MiB                    1,200,000
build_intermediate_records        310 MiB                      600,000
aggregate_by_category              18 MiB                       12,000
```

A reasonable investigation would ask whether `parse_csv_rows` constructs every row as a dictionary, whether `build_intermediate_records` duplicates fields or materializes all rows, and whether those allocations overlap in lifetime. The table does not prove which function dominates peak memory: allocation totals across the run and simultaneous live memory are different questions. Capture temporal/peak evidence or examine the report's peak-oriented views to identify overlapping lifetimes.

## 6. Four metrics that must not be confused

### 6.1 Total allocated memory

Total allocated memory sums allocation events over the capture according to the report's metric. An object allocated, freed, and later replaced contributes to allocation activity even if it is not live at the end. A high total can indicate churn and allocator overhead, but not necessarily high retained memory.

### 6.2 Allocation count

The number of allocation events or blocks recorded. A large number of small allocations can create CPU overhead and allocator pressure even if each object is small. A low allocation count can still accompany a large peak if one or two buffers are enormous.

### 6.3 Peak memory

Peak memory is the maximum amount of memory considered live/allocated at a point in the captured workload according to the profiler's accounting. It is sensitive to **overlap in lifetimes**. If a 500 MiB input buffer and a 500 MiB intermediate representation coexist, the peak can be much larger than either stage's eventual retained footprint.

Memray's reports and capture modes may expose different allocation views; inspect the reporter's description and labels. Do not assume every column means process RSS or that total allocations are interchangeable with peak live memory.

### 6.4 Live allocations and “leaks”

An allocation still live at the end of a capture is not automatically a leak. It may be an intentional cache, a global index, or an object that should live for the process lifetime. A leak-oriented report is a heuristic about allocations that were not freed by the observed end/criteria of the capture; it cannot decide application intent.

Use this reasoning sequence:

- Is the object supposed to survive this phase?
- Does its count or size grow across equivalent repeated workloads?
- Is there a deliberate upper bound or release point?
- Can you identify the owning reference or native subsystem?
- Does the post-fix workload preserve outputs while reducing the problematic peak or unbounded growth?

**Pitfall 1 — treating total allocation as retained memory.** Detect it when the report shows large allocation totals but the process's memory reaches a stable plateau. Correct it by examining live/peak-oriented evidence and repeating the workload.

**Pitfall 2 — treating live-at-end as a leak.** A capture ends at an arbitrary lifecycle boundary. Capture a representative steady-state phase, repeat the workload, and determine which objects are expected to remain alive. Use `memray flamegraph --leaks capture.bin` or `memray table --leaks capture.bin` when the question is specifically what remained allocated at capture end; compare it with the default peak view and account for Python allocator retention.

## 7. Build a controlled `slowlog`-style workload

The following standalone script models a CSV log-analysis stage. It intentionally includes two strategies:

- `materialize`: reads and retains all rows as dictionaries, then constructs a second list of normalized records.
- `stream`: reads one row at a time and aggregates only the fields needed.

Both modes return the same logical summary. The example uses only the standard library so that it can run before adding pandas or a columnar library. It is a teaching workload, not a claim about the exact implementation of a repository-specific `slowlog.py`. Adapt the same experiment to your project's existing script rather than replacing it.

Save as `slowlog_mem.py`:

```python
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any


def generate_csv(path: Path, rows: int) -> None:
    categories = ("auth", "billing", "search", "ingest", "other")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("event_id", "category", "status", "payload"))
        for i in range(rows):
            writer.writerow((
                i,
                categories[i % len(categories)],
                "error" if i % 17 == 0 else "ok",
                f"message-{i}-" + ("x" * 80),
            ))


def summarize_materialized(path: Path) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    # Deliberately materialize a second representation of the input.
    normalized = [
        {
            "event_id": int(row["event_id"]),
            "category": row["category"].strip().lower(),
            "is_error": row["status"] == "error",
            "payload": row["payload"],
        }
        for row in rows
    ]

    counts: Counter[str] = Counter()
    errors = 0
    for row in normalized:
        counts[row["category"]] += 1
        errors += row["is_error"]

    return {"rows": len(normalized), "errors": errors, "by_category": dict(sorted(counts.items()))}


def summarize_streaming(path: Path) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    rows_seen = 0
    errors = 0

    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            # Keep only the values required for the aggregate.
            category = row["category"].strip().lower()
            counts[category] += 1
            errors += row["status"] == "error"
            rows_seen += 1

    return {"rows": rows_seen, "errors": errors, "by_category": dict(sorted(counts.items()))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("events.csv"))
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--mode", choices=("generate", "materialize", "stream"), default="generate")
    args = parser.parse_args()

    if args.mode == "generate":
        generate_csv(args.input, args.rows)
        print(f"generated {args.rows} rows at {args.input}")
    elif args.mode == "materialize":
        print(summarize_materialized(args.input))
    else:
        print(summarize_streaming(args.input))


if __name__ == "__main__":
    main()
```

Generate a small dataset first:

```bash
python slowlog_mem.py --mode generate --rows 100000 --input events.csv
```

Capture the materializing version:

```bash
uv run memray run -o materialize.bin slowlog_mem.py --mode materialize --input events.csv
uv run memray flamegraph materialize.bin
uv run memray table materialize.bin
uv run memray stats materialize.bin
```

Capture the streaming version:

```bash
uv run memray run -o stream.bin slowlog_mem.py --mode stream --input events.csv
uv run memray flamegraph stream.bin
uv run memray table stream.bin
uv run memray stats stream.bin
```

**Important comparison control:** use the same generated input file, Python build, dependency versions, capture options, and machine. Run the two modes in separate processes. Avoid comparing a warm-up run of one mode with a cold run of the other. Do not run both simultaneously, because they would compete for CPU and memory.

### 7.1 Validate correctness before comparing memory

The summaries should be equal for the same input:

```bash
python slowlog_mem.py --mode materialize --input events.csv
python slowlog_mem.py --mode stream --input events.csv
```

For a repeatable test, add:

```python
from pathlib import Path

def test_materialized_and_streaming_summaries_match(tmp_path: Path) -> None:
    path = tmp_path / "events.csv"
    generate_csv(path, rows=250)
    assert summarize_materialized(path) == summarize_streaming(path)
```

The test assumes the functions are imported from the module under test. It checks output equivalence, not memory improvement. Keep both kinds of evidence.

### 7.2 What to look for

The materializing implementation creates a list of dictionaries for all input rows and then creates a second list of normalized dictionaries while the first list remains live. That overlapping lifetime is a plausible peak-memory driver. The streaming implementation only holds the current row and the category counter, so its memory should depend much less on the number of input rows—although CSV parser buffers, strings, the counter, runtime overhead, and input characteristics still matter.

This is a **hypothesis to verify**, not a measured result. Inspect the captures to establish whether the expected allocations dominate your environment. If a real `slowlog` pipeline is dominated by a pandas DataFrame, a native buffer, or a global registry, this standard-library demonstration will not substitute for measuring that implementation.

## 8. Intermediate: native tracing and process models

### 8.1 `--native`

```bash
uv run memray run --native -o native.bin slowlog.py --input data/events.csv
uv run memray flamegraph native.bin
```

Native tracing adds C/C++ frames to allocation stacks, which is valuable for NumPy, pandas, compression libraries, parsers, and other extensions. It has extra overhead because native stack information must be collected/resolved. Reports containing native frames may need to be generated on the same machine as the capture for reliable symbol resolution.

Use it when a Python frame says “call native library” but does not reveal which native path allocated the memory. It is not a universal way to profile every GPU or external-library memory pool.

### 8.2 `--follow-fork`

```bash
uv run memray run --follow-fork -o workers.bin worker_app.py
```

Use this when the tracked program creates child processes through a fork-based model and you need to include their allocations. Memray writes a separate capture for each forked child, with the child PID appended to the output filename. The option requires an output file and is incompatible with `--live` and `--live-remote`. Confirm support and expected behavior for your Memray release and platform. Multiprocessing start methods differ by operating system and Python version; a child created with `spawn` does not have the same relationship to the parent as a forked child. Do not assume this option automatically follows every subprocess or provides a complete aggregate for a distributed pipeline.

When workers each load their own input or model, total deployment memory can be approximately the sum of concurrent worker footprints plus parent/overhead, but copy-on-write sharing and shared-memory designs complicate the calculation. Measure actual per-worker and container memory.

### 8.3 `--trace-python-allocators`

```bash
uv run memray run --trace-python-allocators -o pymalloc.bin slowlog.py --input data/events.csv
```

This enables recording allocations made by Python's `pymalloc` allocator. It can add detail for small Python allocations and change the overhead and volume of the trace. Use it when ordinary attribution is too coarse for a question about Python allocator activity. It does not mean “track every byte in the process,” and it does not eliminate the need to distinguish allocator-level events from process RSS.

### 8.4 Live mode

```bash
uv run memray run --live slowlog.py --input data/events.csv
```

Live mode launches the workload and displays allocation activity in a terminal UI while it runs. It is useful for long-running scripts or when the peak appears only during a particular stage. Depending on the version, live mode has sorting and thread navigation controls; use the displayed UI and current docs as the guide.

Live output is for interactive diagnosis. For durable comparisons, keep a capture and generate reports using repeatable commands.

### 8.5 Attaching to an existing process

Memray releases that support attachment provide an `attach` workflow. Start with `uv run memray attach --help`; the general form is `memray attach [options] <pid>`. Attachment observes allocations made **after** it attaches; it cannot reconstruct allocations that occurred earlier. It requires a Python process with Memray importable in that process's environment and permission to attach a debugger. On Python 3.14+, current Memray uses `sys.remote_exec()` by default when the target has the same Python major/minor version; otherwise a supported debugger such as `gdb` or `lldb` may be required. OS security settings, container capabilities, process state, and tool version affect support.

Attachment injects code into a live process and can, in edge cases, crash or deadlock it. Treat it as an operationally sensitive action: obtain authorization, minimize duration, understand permissions such as `CAP_SYS_PTRACE`, and avoid enabling broad tracing privileges without a security review. Never assume attach works in every container or on every platform. If unsupported or too risky, reproduce the process under `memray run`, use live mode at startup, or collect other process-level metrics while planning a safe capture window.

## 9. Targeted optimization patterns

The correct optimization depends on the allocation evidence. Do not apply all of these patterns indiscriminately.

### 9.1 Full-file reads and duplicate representations

**Symptom:** allocation reports show large lists of rows, strings, dictionaries, or normalized records.

**Candidate fix:** iterate over the input or process bounded chunks; avoid retaining both raw and normalized representations simultaneously. If the complete dataset is required for downstream logic, document that requirement and budget for it instead of pretending streaming is possible without a semantic change.

### 9.2 Unnecessary copies

Copies may be introduced by conversions such as `list(iterator)`, `list(existing_list)`, `DataFrame.copy()`, serialization round trips, or dtype conversions. A copy can be necessary for ownership, mutability, or contiguous layout. Remove it only after checking aliasing and correctness requirements.

For every proposed copy removal, ask:
- Does the downstream consumer mutate the object?
- Does it require ownership or a contiguous buffer?
- Will removing the copy extend the lifetime of a larger base object?
- Does the new implementation preserve ordering, null handling, and error behavior?

### 9.3 Intermediate DataFrames

For pandas/columnar pipelines, a transformation can temporarily hold input, output, and intermediate arrays simultaneously. Allocation reports with `--native` can reveal native allocation paths, but interpret library-level calls in context. Consider dropping references to no-longer-needed intermediates, reducing unnecessary conversions, selecting only required columns, or chunking the input.

Do not assume a DataFrame's Python object size represents its complete buffer footprint. Native arrays and shared buffers may dominate. Also do not assume a DataFrame operation is in-place merely because the syntax looks like mutation; inspect library semantics and measure.

### 9.4 Oversized dtypes

If a column contains small bounded integers or low-cardinality categories, a smaller dtype or categorical representation may reduce memory. Check value range, missing values, overflow behavior, downstream arithmetic, serialization compatibility, and whether the conversion itself temporarily duplicates the data. Benchmark and test on representative data, not just a tiny sample.

### 9.5 Views retaining base buffers

A small array or table view may keep a large base buffer alive. The visible object can look small while the referenced storage remains large. A copy may allow the large base to be released if no other references exist, but the copy temporarily raises peak memory. Compare both peak and lifetime; the right decision depends on whether the view outlives the processing stage and whether the base is needed elsewhere.

## 10. Advanced: churn, GC pressure, caches, and temporal peaks

### 10.1 Allocation churn

A pipeline can allocate and free millions of small temporary objects. Total allocation and count can be large even when retained memory is stable. Churn can increase CPU time, allocator work, cache pressure, and GC activity for GC-tracked objects. Memray helps attribute allocation call paths; it is not a substitute for CPU profiling or the dedicated GC lesson.

Ask:
- Is the allocation count very high relative to records processed?
- Are the objects short-lived or retained?
- Are they Python objects, native buffers, or both?
- Does the workload spend time creating objects that are immediately discarded?
- Would batching or a different representation reduce per-record object creation without changing behavior?

### 10.2 Cache effects

Caches can reduce repeated computation but retain values and their object graphs. A bounded entry count is not necessarily a byte bound. Compare cold and warm runs when cache behavior is relevant, and do not mix a cache-cold baseline with a cache-warm candidate.

### 10.3 Time-dependent peak memory

A final RSS sample can miss a transient peak. For a pipeline with stages A, B, and C, the critical question is which objects coexist. Capture a representative full run and, where possible, measure around stage boundaries. A stage that allocates less total memory can still cause the peak if it overlaps with retained buffers from an earlier stage.

A useful timeline table for an investigation:

| Stage | Input live? | Intermediate live? | Output live? | Measurement to record |
|---|---|---|---|---|
| Read/parse | Possibly | Parsed rows | No | Peak during parsing |
| Normalize | Possibly | Raw + normalized | No | Overlap between representations |
| Aggregate | Maybe | Aggregation state | Maybe | Cardinality and retained state |
| Serialize/write | Maybe | Output buffer | Output file | Buffer size and flush behavior |

The table is a reasoning aid, not measured evidence. Fill it with the actual pipeline's ownership/lifetime behavior.

### 10.4 Python allocator, native allocator, and RSS

Memray reports allocation events and call stacks; it does not make RSS synonymous with the sum of every report column. Python's object allocator may keep arenas for reuse after objects are freed. Native libraries may maintain pools. Memory fragmentation can prevent pages from being returned to the OS, and memory-mapped files contribute to process accounting differently across platforms.

If Memray shows a stable allocation picture while RSS continues to grow, check the metric definition, workload changes, native libraries, mapped files, and allocator behavior. Use the appropriate native/system diagnostic tool if the capture does not explain the symptom. Do not label the unexplained difference as a proven leak.

### 10.5 Arrays and GPU allocators — awareness

NumPy/pandas and other native libraries can allocate large buffers outside ordinary Python object storage. GPU frameworks often maintain caching allocators: memory reserved by a framework may remain reserved for reuse after a tensor is released. Whether Memray can see these allocations depends on how the allocator obtains memory and what the capture hooks can intercept. GPU device memory is not the same metric as process RSS. Use framework-specific memory statistics and profilers for device allocations; treat Memray as one piece of evidence.

## 11. Container limits, worker multiplication, and memory budgets

A pipeline's peak must fit within its operational environment, not merely on a developer laptop.

Budget for:
- Python interpreter and imported libraries;
- input buffers and simultaneously live intermediate data;
- native-library workspaces and allocator pools;
- per-worker data, model state, queues, and caches;
- concurrency spikes, retries, and temporary serialization buffers;
- monitoring/profiling overhead and safety headroom.

If each worker materializes the same input, memory may scale with worker count. If workers share copy-on-write pages, the relationship can be different and may change as pages are modified. Measure the actual container or cgroup usage and understand whether the configured limit applies to one process, a pod, or a larger group.

A practical budget is a documented upper bound with headroom, based on representative workload distributions and concurrency—not a value chosen because the latest run happened to fit. Keep the memory limit below the point where the OS or orchestrator must terminate the job, and have a backpressure or graceful failure strategy.

## 12. Memory regression testing with pytest-memray

Install the plugin in the development environment:

```bash
uv add --dev pytest pytest-memray
uv run pytest --help
```

The plugin is enabled with `--memray`:

```bash
uv run pytest --memray tests/
```

It reports allocation information for tests and supports markers to enforce memory behavior. Marker support is version-sensitive; consult the installed `pytest-memray` documentation and check your Python version.

### 12.1 `limit_memory`

Current stable documentation describes:

```python
import pytest

@pytest.mark.limit_memory("24 MB")
def test_processing_stays_within_memory_budget() -> None:
    result = process_representative_fixture()
    assert result.row_count == EXPECTED_ROWS
```

The example is a template: `process_representative_fixture()` and `EXPECTED_ROWS` must be replaced with project-specific code. The marker checks peak/high-water allocation during the test according to the plugin's instrumentation; it is not an assertion about RSS. Choose the limit from measured behavior in a controlled environment with appropriate headroom. The interpreter allocator may not immediately return freed memory to the OS.

### 12.2 `limit_leaks`

Current stable documentation also describes a `limit_leaks` marker that groups allocations remaining at the end of the test by call stack and fails if a location exceeds the specified threshold. It is useful for repeated workloads, but internal caches and incidental interpreter allocations can cause noise. The plugin recommends running the API/workload in a loop to distinguish genuine leaks from incidental allocations.

Example template:

```python
import pytest

@pytest.mark.limit_leaks("1 MB")
def test_repeated_batches_do_not_accumulate_large_allocations() -> None:
    for _ in range(20):
        process_representative_batch()
```

This threshold is illustrative, not a universal safe default. Use a representative batch and justify the threshold experimentally. A single call may not expose accumulation; a loop often makes the retention trend easier to observe.

### 12.3 `limit_leaked_objects` and version caveats

Recent `pytest-memray` documentation describes `pytest.mark.limit_leaked_objects()` for Python 3.13.3 and newer. It fails when Python objects created during the test remain alive at the end, subject to the plugin's filtering and support. Do not use it unconditionally on older Python versions; check the installed plugin documentation and guard or skip the test where necessary.

### 12.4 Save captures for deeper analysis

The plugin documentation describes `--memray-bin-path` for saving binary captures, and options may vary by plugin release. Verify exact options with:

```bash
uv run pytest --help
```

If a test exceeds a memory limit, use the saved capture with the Memray reporters to identify the allocation path. A failing threshold is a signal to investigate, not automatic proof of a leak. Keep correctness assertions in the same test or a companion test.

**Pitfall 3 — setting a memory threshold from one unrepeatable run.** Establish a baseline on a pinned runner, record versions and fixture size, run multiple times, and leave margin for legitimate runtime variation. Avoid exact byte thresholds across different OSes and Python builds.

## 13. Choosing the right tool

Use each tool for the question it answers.

| Tool | Best question | Important limitation |
|---|---|---|
| **Memray** | Which Python/native allocation call paths account for allocation activity and peaks in this run? | Instrumentation overhead; capture and report metrics must be interpreted carefully |
| **`tracemalloc`** | Which traced Python allocations are live, and how did source-line statistics change between snapshots? | Does not fully account for native allocations or all process RSS |
| **Scalene** | Where is sampled Python/native CPU and memory behavior attributed at line level? | Sampling and metric semantics differ from allocation-event tracing |
| **Pympler** | What is the estimated deep size of a Python object graph? | Estimate depends on graph traversal/type support; not a direct RSS-release prediction |
| **objgraph** | Which Python object types are growing, and what references may keep an object alive? | Object-graph view is not a complete process heap or native-memory census |
| **Fil** | Where did the high-water memory peak originate in a Python workload? | Different instrumentation/reporting model; verify support and compatibility for your environment |

Do not use every tool on every incident. Start with the symptom and choose the smallest tool that can answer the next question. For example, if a `tracemalloc` snapshot already shows an unbounded global list, use reference inspection and a regression test; native tracing may add little. If RSS grows while traced Python memory is stable and a NumPy/native path is involved, Memray with `--native` or a library-specific profiler may be the better next step.

## 14. Troubleshooting

| Symptom | Possible cause | Next action |
|---|---|---|
| `memray` command not found | Wrong environment or tool not installed there | Run `uv run memray --help`; verify the active interpreter/environment |
| Capture exists but report generation fails | Version mismatch, corrupt/incomplete capture, wrong command/filename | Use `memray --help`, inspect the capture path, rerun capture cleanly |
| Flame graph shows a broad Python wrapper | Inclusive allocation attributed through callees | Drill into children; use native mode if the underlying work is in C/C++ |
| Large total allocations but modest peak | High allocation churn with short lifetimes | Inspect allocation count and hot paths; consider reducing temporary object creation |
| High peak but low final retained memory | Large intermediate objects overlap in lifetime | Measure stage boundaries and shorten overlap or stream/chunk |
| Native frames absent | Capture was not made with `--native`, symbols unavailable, or allocation path not intercepted | Capture with native tracing; check platform and symbolization requirements |
| Child process memory absent | Process model not followed by current capture/options | Verify `--follow-fork` support and actual start method; measure workers separately if needed |
| RSS grows but Memray/tracemalloc do not explain it | Native allocator/pool, mapping, workload change, or metric mismatch | Check cgroup/RSS semantics and library-specific memory tools |
| `pytest-memray` marker appears ineffective | Plugin not enabled or version mismatch | Run tests with `--memray`; inspect plugin version and help |
| Memory test flakes in CI | Threshold too tight, variable fixture, shared runner, cache warm-up differences | Pin environment, stabilize input, repeat, widen justified margin, separate performance runner |
| Native tracing is much slower | Native stack capture/symbolization overhead | Shorten capture, use ordinary mode first, enable native tracing only for targeted runs |

## 15. Common mistakes

1. Treating total allocated bytes as peak memory or retained memory.
2. Reading flame-graph width as elapsed time or chronological order.
3. Assuming allocations live at capture end are necessarily leaks.
4. Capturing a toy input that does not exercise the production data shape.
5. Comparing captures from different Python builds, inputs, process counts, or instrumentation settings.
6. Enabling native tracing everywhere without considering its overhead.
7. Assuming `--follow-fork` follows every subprocess model or distributed worker.
8. Treating `--trace-python-allocators` as complete process-memory tracking.
9. Optimizing a wide frame without checking whether it is the cause of the observed peak.
10. Removing a copy without checking aliasing, mutation, or buffer lifetime.
11. Claiming a measured reduction from illustrative output or one noisy run.
12. Using a `pytest-memray` threshold without verifying the plugin version and marker semantics.
13. Ignoring the memory cost of multiple workers, queue depth, and simultaneous intermediates.
14. Treating a flat `tracemalloc` result as proof that native memory is healthy.
15. Forgetting correctness tests while optimizing memory.

## 16. Exercises

### Exercise 1 — report literacy
Capture a representative script with Memray. Generate flame graph, table, summary, and stats reports. Write down what each report helps answer and which metrics it does not establish.

### Exercise 2 — churn or peak?
Create a workload that repeatedly allocates and frees medium-sized lists, then a workload that holds two large lists simultaneously. Compare total allocations, count, and peak-oriented evidence. Explain why neither total bytes nor allocation count alone ranks peak memory reliably.

### Exercise 3 — native allocation
If NumPy or pandas is available, profile a transformation that creates a large array or intermediate frame. Compare ordinary and `--native` captures. Explain what new call-stack evidence appears and how tracing overhead affects the comparison.

### Exercise 4 — chunked processing
Adapt the `slowlog` workload to process a large CSV in chunks. Preserve row counts, error counts, category totals, ordering, and null/error semantics. Measure baseline and candidate using the same input and report commands. Do not assert a speed or memory reduction until the captures support it.

### Exercise 5 — multiprocessing
Run a small worker-based workload. Check the multiprocessing start method and determine whether the capture covers child allocations. Compare parent-only, worker-level, and deployment-level memory without assuming they are additive in the presence of copy-on-write/shared buffers.

### Exercise 6 — memory regression test
Add `pytest-memray` with `--memray`, a justified `limit_memory` threshold, and a repeated-workload `limit_leaks` test where appropriate. Run the tests more than once and document any noise or version restrictions.

### Exercise 7 — memory budget
For a batch pipeline, estimate the memory budget for the parent, N workers, queue backlog, intermediate buffers, and headroom. Validate the estimate against observed container metrics. Explain what happens if input size or worker count doubles.

## 17. Self-check questions

1. What is Memray designed to attribute?
2. Why are total allocation bytes and peak memory different?
3. What does a wide frame in an allocation flame graph mean?
4. Why is an allocation that remains live at capture end not necessarily a leak?
5. When should `--native` be enabled?
6. What question does `--follow-fork` answer, and what does it not guarantee?
7. What extra visibility does `--trace-python-allocators` seek to provide?
8. How do live mode and saved-capture reports differ in purpose?
9. How can a full-file read and a second normalized list create a high peak?
10. Why can a view keep a large base buffer alive?
11. Why can RSS remain high when live allocations decline?
12. What does `pytest.mark.limit_memory()` measure, and why is it not an RSS assertion?
13. Why should a leak test repeat a workload?
14. How can multiple workers exceed a memory limit even when each worker appears safe alone?
15. Which evidence would make you choose Memray over `tracemalloc`, or vice versa?

## 18. Hands-on task — allocation analysis of `slowlog`

Use the shared Module 1.17 `slowlog` project. The roadmap's mini-project calls for finding a memory problem, avoiding unnecessary copies, capturing allocation evidence, and writing a report. Keep the work focused; do not redo the full CPU-profiling or GC lesson.

### Required procedure

1. **Record the baseline.** Save the Git revision, Python version/build, OS/architecture, Memray version, dependencies, input rows/bytes/distribution, worker count, and container memory limit.
2. **Verify correctness.** Record expected output counts, category totals, errors, ordering, and relevant edge cases before changing code.
3. **Capture.** Run the baseline with `memray run -o baseline.bin ...`. Use the ordinary mode first; use `--native` or `--follow-fork` only if the workload calls for them.
4. **Read reports.** Generate `flamegraph`, `table`, `summary`, and `stats`. Record which metric each observation represents. Identify whether the likely issue is a peak, churn, or retained allocation.
5. **Form a hypothesis.** Name the allocation path and explain how it affects simultaneous live memory or allocation volume.
6. **Change one thing.** Examples: stream CSV rows, process bounded chunks, remove a duplicate representation, select fewer columns, use a safe smaller dtype, or shorten the lifetime of an intermediate.
7. **Validate correctness.** Run the same tests and compare the outputs from baseline and candidate.
8. **Capture again.** Use the same input, environment, command options, and capture boundaries. Repeat if the workload is noisy or has one-time warm-up effects.
9. **Compare.** Report the measured peak/total/count metrics actually shown by your version's reports, and state the metric definition. Include RSS or container metrics separately when relevant.
10. **Discuss trade-offs.** Did the change increase CPU time, I/O, or complexity? Does it change ordering, mutability, error behavior, or peak overlap? What remains unexplained?
11. **Add a regression guard.** Use a targeted `pytest-memray` marker or a stable workload-level trend test. Avoid exact cross-platform RSS assertions.
12. **Write the report.** Use the template below and keep the capture artifacts or report files with the exact command/environment metadata.

### Acceptance criteria

- The baseline and candidate process equivalent input.
- Correctness is preserved or any intentional semantic change is documented.
- The report identifies the allocation path and explains why it drives the selected metric.
- The intervention targets the measured cause.
- The result is based on actual captures; no invented 50% reduction or speed claim.
- A regression guard exists and its environment/version limitations are documented.
- The final report distinguishes peak, total allocation, count, live/retained evidence, RSS, and uncertainty as applicable.

The roadmap's CSV-to-Parquet mini-project target is to reduce peak memory by **at least 50%** and document how; treat this as a target to attempt and evaluate experimentally, not a promised outcome. If the shared `slowlog` implementation or environment uses the equivalent CSV-to-summary workload instead of a Parquet conversion, state that scope explicitly and apply the same measured peak-memory methodology. If the measured result does not reach the target, report that honestly and explain what you tried, what improved, and what remains.

## 19. Reproducible allocation-investigation report template

Copy into `PERF_REPORT.md` and complete it with measured evidence.

```markdown
# Memory Allocation Investigation — [slowlog / workload]

## 1. Executive summary
- Symptom and impact:
- Hypothesis:
- Root cause (confirmed / likely / unresolved):
- Intervention:
- Result:
- Trade-offs and remaining risks:

## 2. Environment
- Git revision:
- Python version, implementation, build flags:
- OS, architecture, container/runtime:
- Memray version and installed options:
- Dependencies and native libraries:
- Worker count and multiprocessing start method:
- Container/cgroup memory limit:

## 3. Workload and correctness
- Input path/format, bytes, rows, distribution:
- Batch/chunk size:
- Expected output counts, totals, ordering, errors:
- Warm-up and cache policy:
- Reproduction command:

## 4. Capture methodology
- Exact `memray run` command:
- `--native`, `--follow-fork`, `--trace-python-allocators`, `--leaks`, and `PYTHONMALLOC` settings:
- Report commands and output files (separate peak and end-of-capture/leak views):
- Repetitions and capture boundaries:
- Instrumentation overhead/limitations:
- RSS/container metrics and units:

## 5. Baseline findings
- Peak metric and value (include report definition):
- Total allocated bytes (if reported):
- Allocation count (if reported):
- Live/retained evidence:
- Top call paths and source locations:
- Stage where the peak occurs:
- Correctness output:
- Illustrative versus measured values clearly labelled:

## 6. Diagnosis
- Which allocations overlap in lifetime?
- Is the issue peak, churn, retention, or unresolved native/process memory?
- Evidence for the hypothesis:
- Alternative explanations considered:
- Why the chosen metric represents the problem:

## 7. Intervention
- Code/configuration change:
- Why it addresses the allocation cause:
- Ownership/lifetime or algorithm changes:
- Correctness and compatibility risks:
- Trade-offs (CPU, I/O, latency, complexity):

## 8. Verification
- Exact candidate command:
- Output equivalence and tests:
- Candidate peak/total/count metrics:
- RSS/container metrics:
- Repetitions and variability:
- Regression guard and threshold rationale:
- Results that were not measured or remain uncertain:

## 9. Conclusion
- What the evidence proves:
- What it does not prove:
- Did the acceptance criterion pass?
- Follow-up monitoring:
- Decision: resolved / mitigated / further investigation
```

## 20. Completion checklist

- [ ] I can install Memray and verify CLI support in my environment.
- [ ] I can capture a workload and generate flame graph, table, summary, and stats reports.
- [ ] I can distinguish peak memory, total allocation, allocation count, and live/retained evidence, including the default peak view versus `--leaks`.
- [ ] I can enable native tracing or fork-following only when the investigation requires it.
- [ ] I can interpret allocation churn separately from large buffers that overlap in lifetime.
- [ ] I can preserve correctness while switching from materialization to streaming/chunking.
- [ ] I can use `pytest-memray` markers supported by my installed version.
- [ ] I can explain the difference between profiler metrics, allocator behavior, and RSS.
- [ ] I can account for worker multiplication, queue depth, container limits, and headroom.
- [ ] I completed the `slowlog` allocation investigation and wrote `PERF_REPORT.md`.

**Next lesson:** `06-garbage-collector-and-reference-cycles.md` — focus on object lifetime, reference cycles, GC behavior, and measured GC tuning rather than repeating allocation attribution.

---

## Documentation notes

The command and marker examples in this lesson are grounded in the current Memray and pytest-memray documentation consulted during preparation. Tool interfaces can change; verify `--help` and the documentation for the exact installed release before applying commands to production.

- Memray CLI: https://bloomberg.github.io/memray/run.html
- Memray project/native mode: https://github.com/bloomberg/memray
- pytest-memray usage: https://pytest-memray.readthedocs.io/en/stable/usage.html
