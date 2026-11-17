# Sampling Profilers with `py-spy`

> **Stage 1 — Programming & Computational Thinking · Module 17: Profiling, Memory and Runtime Performance**  
> **Lesson 02 · Target runtime: Python 3.12+**  
> **Purpose:** Investigate a slow or apparently hung Python process using sampled stack evidence, without confusing samples with exact timings.

---

## 1. Where this lesson fits

Module 17 follows the rule introduced in Module 1.10, lesson 06: **measure before you optimise**. Lesson 01 introduced deterministic profiling with `cProfile`, `pstats`, and profile visualisations. This lesson adds sampling profilers, which are especially useful when a process is already running, a workload is long-lived, or deterministic instrumentation would perturb a high-call-count workload.

The shared practice application is a deliberately inefficient log/CSV analytics job. It is a learning workload, not a claim that every production ETL job has the same bottleneck.

This lesson stays at the Python profiling and production-investigation layer. It does not replace the later lessons on microbenchmark design, memory tracing, garbage collection, or CPython optimisation idioms.

## 2. Prerequisites

You should be comfortable with:

- Python functions, loops, exceptions, modules, and reading stack traces.
- Running a script from a terminal and using a virtual environment.
- CSV/text-file processing and basic collections such as `list`, `set`, and `dict`.
- The idea of CPU time versus wall-clock time.
- The measurement-first mindset and basic deterministic profile terminology from Lesson 01.

If the words *process*, *thread*, *blocking*, *I/O*, or *call stack* are unfamiliar, review the relevant Stage 0 operating-system lessons and Module 09 concurrency vocabulary before interpreting production evidence.

## 3. Learning objectives

By the end, you should be able to:

1. Explain sampling, sampling frequency, sample counts, and uncertainty.
2. Choose between `py-spy`, deterministic profiling, Scalene, and pyinstrument for a specific question.
3. Capture live stack snapshots, live top views, and recorded profiles with `py-spy`.
4. Read flame graphs and Speedscope profiles without treating them as timelines or exact function timers.
5. Diagnose permission failures and account for platform/container constraints.
6. Distinguish active CPU work from waiting, lock contention, and I/O delays using profiles plus system evidence.
7. Investigate native code, concurrency symptoms, startup delays, serialization, and other production bottlenecks.
8. Write a safe, reproducible runbook and evidence-based performance investigation.

---

## 4. What a sampling profiler does

### 4.1 The central idea

A sampling profiler periodically asks, in effect, **“What stack is this process executing right now?”** It records a stack snapshot, waits for the next sampling interval, and repeats. If the process spends a large fraction of its time in one execution path, that path tends to appear in many samples.

A stack is a chain of active calls, for example:

```text
main
└── process_file
    └── parse_row
        └── datetime.strptime
```

The profiler does not need to instrument every Python function call. It samples the running process from outside (subject to platform and permission support) and reconstructs Python/native stacks where possible. That is why `py-spy` can often attach to an existing Python process without requiring a code change or restart.

**Important:** a sample is an observation at one instant, not a stopwatch measurement for every function. Sample counts estimate where execution time was spent over the recording window. They do not prove that each individual call took a particular duration.

### 4.2 Sampling frequency and uncertainty

If a profiler samples at \(f\) samples per second for \(T\) seconds, the nominal sample count is approximately:

\[
N \approx fT
\]

At 100 samples/second over 30 seconds, the recording might contain roughly 3,000 sampling opportunities. Actual recorded samples can be fewer because of process state, scheduling, permissions, profiler behavior, and format-specific filtering.

A path observed in 1,500 of 3,000 samples accounts for approximately 50% of those samples. This is an estimate, not an exact statement that a function consumed precisely half the wall-clock time.

For an idealized independent Bernoulli sample proportion \(\hat p\), a rough standard error is:

\[
SE(\hat p) \approx \sqrt{\frac{\hat p(1-\hat p)}{N}}
\]

This formula is a useful intuition, not a full confidence interval for real profiler data. Stack samples can be correlated, execution phases change over time, and samples are not always independent or uniformly distributed. More samples generally improve the stability of estimates, but do not remove systematic bias.

**Practical implications**

- Very short recordings may miss intermittent work entirely.
- A low sample rate may miss short-lived functions or brief spikes.
- A longer recording captures more phases, but may mix unrelated workload states.
- Use a representative time window and repeat captures when the result is ambiguous.
- Do not increase sampling rate blindly: higher rates can add overhead and produce more data.

### 4.3 Sampling versus deterministic instrumentation

| Property | Sampling (`py-spy`) | Deterministic instrumentation (`cProfile`) |
|---|---|---|
| Observation | Periodic stack snapshots | Records function-call/return events |
| Best question | “Where is this running process spending time?” | “How many calls happened and what are their measured timings?” |
| Existing process | Often attachable with permissions | Usually needs instrumentation at startup or an application integration |
| Tiny-function detail | May miss short functions between samples | Can count calls, but event overhead can distort high-call-count code |
| Timing precision | Statistical estimate from samples | Per-function event-based timing, still affected by profiler overhead |
| Native execution | Depends on native-stack support and symbols | C calls may appear as built-in functions, with limited internal detail |
| Best use | Production triage, broad hotspots, long-running services | Controlled scripts, call counts, detailed Python call relationships |

These tools answer different questions. Use them together when useful; do not expect their reported percentages to match exactly.

---

## 5. Install and inspect the tool

Use the project’s environment and lockfile where possible. With `uv`, the roadmap’s development-tool setup includes:

```bash
uv add --dev py-spy scalene pyinstrument
uv run py-spy --help
uv run py-spy record --help
uv run py-spy top --help
uv run py-spy dump --help
```

The exact options and output formats vary by installed `py-spy` version and platform. **Treat the local `--help` output as authoritative.** Do not copy an option from an article written for another version and assume it exists in your environment.

If you are not using `uv`, install the package in the environment that owns your tooling, then run `py-spy --version` and inspect `py-spy --help`.

A common production pattern is to keep the profiler binary in a controlled diagnostic environment rather than adding it to the application’s runtime dependencies.

**Version compatibility:** the upstream `py-spy` README consulted for this lesson lists CPython support through Python 3.14. Do not infer Python 3.15 support from the lesson’s general Python 3.12+ target; check the installed `py-spy` release notes and support matrix before profiling a newer interpreter. A profiler and target that are incompatible may fail to attach or produce incomplete data.

---

## 6. The three core `py-spy` workflows

### 6.1 Live view: `py-spy top`

Use `top` to see which functions dominate samples while the process runs:

```bash
py-spy top --pid 12345
```

Replace `12345` with the actual PID. Do not run this command against a PID copied from an example.

The live display updates as samples arrive. Depending on the installed version, it may show functions, percentages, and thread information. Interpret the percentages as sample-derived estimates for the observation window, not exact wall-clock timers.

**When to use it**

- A batch job is slow right now and you can safely observe it.
- A service has high CPU and you need an initial hotspot.
- You need to know whether the process is repeatedly in parsing, serialization, application code, or native library calls.

**Limitations**

- A short-lived hotspot may disappear between updates.
- A process that is blocked or idle may not show a CPU-heavy stack.
- Permissions, Python build details, and platform support affect what can be observed.
- `top` alone rarely proves a root cause; correlate with logs, metrics, and a recording.

### 6.2 Record a profile

Record a flame graph while launching a command:

```bash
py-spy record --output profile.svg -- python etl.py data/events.csv
```

To choose a sampling rate explicitly, if supported by the installed version:

```bash
py-spy record --rate 100 --output profile.svg -- python etl.py data/events.csv
```

The `--` separates profiler arguments from the command being profiled. Check `py-spy record --help` for the valid rate range and available formats for your version.

To attach to a process already running:

```bash
py-spy record --pid 12345 --output attached-profile.svg
```

For a bounded capture, use the duration option supported by the installed version (commonly `--duration 30`) and verify its spelling with `py-spy record --help` before an incident. For example:

```bash
py-spy record --duration 30 --output attached-profile.svg --pid 12345
```

If the installed build does not expose that option, stop the recording deliberately after the agreed observation window.

**Safe practice:** record only long enough to answer the question. A flame graph can reveal source paths, function names, package structure, and potentially sensitive operational details. Store it with restricted access and an appropriate retention period.

### 6.3 Snapshot stacks: `py-spy dump`

```bash
py-spy dump --pid 12345
```

This asks for a snapshot of the target process’s current stacks, commonly across its threads when supported. It is particularly useful for a hung job because it shows where threads appear to be at the observation instant.

Example of **illustrative output** (not measured from a real process):

```text
Process 12345: python etl.py
Python v3.12.x
Thread 0x... (active): "MainThread"
    run_pipeline
    process_batch
    fetch_reference_data
    requests.get
    socket.recv_into
```

Interpretation:

1. The main thread is inside a network receive path.
2. That is consistent with waiting on I/O, but a single snapshot does not prove whether the remote service, network, timeout configuration, or local socket handling is the root cause.
3. Capture a second snapshot after a short interval. If the stack remains unchanged, investigate timeouts, request deadlines, network metrics, and upstream health.
4. Check logs and thread stacks before declaring a deadlock.

Another illustrative pattern:

```text
Thread "worker-1": ...
    process_record
    normalize_payload
    json.dumps

Thread "worker-2": ...
    process_record
    normalize_payload
    json.dumps
```

Multiple threads in the same serialization path may indicate repeated serialization work. It does not, by itself, show whether the workload is CPU-bound, GIL-limited, or waiting elsewhere.

---

## 7. Read flame graphs correctly

A flame graph arranges sampled stacks into nested rectangles.

- **Width** represents the number/proportion of samples attributed to a stack frame or aggregated stack path in that visualization.
- **Vertical position/depth** represents stack depth and call ancestry.
- **Horizontal position is not chronological execution order.** The graph is arranged to aggregate stacks, not to show a left-to-right timeline.
- A wide frame is a high-priority investigation candidate, not automatic proof that the function should be rewritten.

For example, if `parse_timestamp` occupies a wide rectangle under `parse_row`, many samples observed execution there or beneath it. Possible causes include expensive parsing, a high call count, or both. Confirm with representative input, another profile, and targeted measurements before changing code.

### Inclusive and self/leaf interpretation

A parent frame can be wide because its descendants consume time. If `process_file` contains `parse_row`, which contains `parse_timestamp`, the parent’s inclusive width may reflect samples in its whole subtree. Do not add parent and child widths as if they were independent costs; that double-counts nested execution.

A frame that is wide at the bottom of many stacks is often more directly actionable than a broad orchestration function whose descendants do the work. But the “leaf” may be a built-in or native function, and the application-level fix may belong to its caller.

### Flame graph versus timeline

Use a flame graph to answer **“which stack paths were common?”** Use timestamped logs, traces, metrics, or a timeline-capable viewer to answer **“when did the stall begin, and what happened before it?”**

---

## 8. Useful options and output formats

Options are version- and platform-dependent. Confirm all flags against the installed binary before using them.

### `--native`

Where supported, request native stack frames as well as Python frames:

```bash
py-spy record --native --output native-profile.svg -- python etl.py data/events.csv
```

This can help reveal time in C/C++ libraries, such as NumPy, pandas, PyTorch, compression libraries, or database drivers. Native-frame support is limited to supported platform/architecture combinations; native symbol availability, debug symbols, and permissions determine how useful the result is. Check the upstream support matrix for the target OS and architecture before relying on this mode. A native frame may be unresolved or incomplete; absence of a readable frame is not proof that native code is uninvolved.

### `--gil`

Where supported, limit samples to threads holding the Global Interpreter Lock (GIL):

```bash
py-spy record --gil --output gil-profile.svg --pid 12345
```

This is a diagnostic lens, not a general-purpose replacement for a normal profile. It can help examine which threads hold the GIL, but it does not alone establish the complete cause of poor throughput. Interpret it alongside CPU utilization, thread states, and the application’s concurrency model. On free-threaded Python builds, GIL-related interpretations differ.

### `--idle`

Where supported, include idle/waiting stack observations:

```bash
py-spy record --idle --output wall-profile.svg --pid 12345
```

This can make waiting behavior more visible, depending on version and platform. Idle samples must not be interpreted as CPU consumption. Compare with process CPU, wall time, I/O, and scheduler metrics.

### `--subprocesses`

Where supported, follow child processes launched by the target:

```bash
py-spy record --subprocesses --output tree-profile.svg -- python parent_job.py
```

Check the installed version’s documentation for how child-process output is represented and whether the chosen output format supports it. Multiprocessing may create independent workers, and the parent’s profile alone may omit the work that dominates total job duration. Followed child profiles can increase artifact volume and sensitivity.

### Output formats and Speedscope

Check supported formats:

```bash
py-spy record --help
```

Common upstream `py-spy` formats include the default interactive SVG flame graph, Speedscope JSON, and raw stack data. Confirm the exact choices for the installed release and platform before using a format in a runbook:

```bash
# Default flame graph (SVG)
py-spy record --output profile.svg -- python etl.py data/events.csv

# Speedscope-compatible JSON
py-spy record --format speedscope --output profile.speedscope.json -- python etl.py data/events.csv

# Raw stack output for text-based processing
py-spy record --format raw --output profile.raw -- python etl.py data/events.csv
```

Use the exact format name shown by your installed version. Open Speedscope JSON in the viewer at `https://www.speedscope.app/` according to your organization’s data-handling policy. For confidential profiles, prefer an approved local or internal viewer rather than uploading artifacts to a public service. Raw output is useful for scripting and downstream processing but is less convenient for visual exploration.

Speedscope supports different visual perspectives. A “sandwich” or inverted view can help locate the callers responsible for a hot function; a chronological/time-order view, when available for the profile format, answers a different question from an aggregated flame graph. The viewer cannot recover timing detail the profiler never collected.

### Platform and permissions at a glance

| Environment | Typical constraint | Practical response |
|---|---|---|
| Linux | Process inspection can be restricted by UID, capabilities, ptrace policy, Yama `ptrace_scope`, or container isolation | Run with appropriate identity and least privilege; check OS policy and audit requirements |
| WSL2 | Linux kernel and process-inspection restrictions still apply; behavior depends on WSL configuration | Test against a process in the same environment; inspect `py-spy` errors and local permissions |
| Docker | Container PID namespaces and capability restrictions may prevent attachment | Prefer profiling from the same container where possible; grant only approved diagnostic capabilities |
| Kubernetes | Pod security, namespaces, ephemeral-container policy, and cluster RBAC may block inspection | Follow the platform runbook; obtain approval for an ephemeral debug container or node-level inspection |
| macOS | System security and process permissions may restrict attaching to other processes | Use an authorized account and consult current tool support |
| Windows | Process access and native stack support differ from Linux; some options may be unavailable | Check current `py-spy` platform documentation and local `--help`; test on a non-production process first |

On Linux, `sudo` may be required, but do not treat it as the default solution. Prefer the least-privileged supported path. Do not weaken host security policy globally just to run a profiler. In Kubernetes, avoid adding broad privileges to a production workload as a convenience.

---

## 9. Distinguish CPU work from waiting

A slow request or batch job is not necessarily CPU-bound. Sampling is most informative when interpreted with other evidence.

| Evidence pattern | Plausible explanation | Next checks |
|---|---|---|
| High process CPU and repeated samples in parsing/transformation | CPU-bound Python or native work | Record a longer profile; inspect hot stack paths and input shape |
| Low CPU, stable stack in `socket.recv`, database client, or file read | I/O wait or upstream delay | Check timeouts, latency histograms, network/database/file-system metrics |
| Many threads at a lock acquire/wait path | Lock contention or convoy | Inspect lock ownership and critical-section duration; compare thread stacks over time |
| Slow async requests, event-loop thread in synchronous I/O or CPU-heavy function | Event loop blocked | Inspect async task/loop lag metrics; move blocking work to an appropriate executor or use async I/O |
| Workers idle while queue grows | Starved pool, blocked workers, or downstream bottleneck | Check queue depth, worker utilization, task duration, downstream limits |
| Parent process quiet but children busy | Work concentrated in child processes | Inspect child PIDs or use supported subprocess tracing |
| High wall time but low process CPU | Waiting, throttling, locks, or child-process work | Correlate wall/CPU time with cgroup throttling, I/O, and child process metrics |

A stack containing `time.sleep` may be intentional backoff. A stack in a database driver may be waiting for a response or executing native code. Stack evidence narrows hypotheses; it does not uniquely identify root cause.

### CPU-bound

A CPU-bound workload spends most of its time executing instructions. A high CPU utilization signal plus repeated hot computation stacks is consistent with this. Identify the hot path, then check algorithmic complexity, repeated work, data structures, and whether native/vectorized execution is appropriate in later lessons.

### I/O-bound

I/O-bound work spends significant time waiting for external resources. The profile may show a network read, database call, file operation, or event wait. Determine whether the wait is expected, whether deadlines/timeouts exist, and whether requests are serialized unnecessarily.

### Lock-bound and pool starvation

If threads repeatedly wait on the same lock, inspect who owns it and how long the critical section runs. A lock convoy occurs when many workers queue behind a serialized resource. Pool starvation can occur when all worker slots are occupied by tasks waiting for work that itself needs the same pool. A snapshot is a clue; repeated snapshots and application-level metrics provide stronger evidence.

---

## 10. Complementary tools: Scalene and pyinstrument

### Scalene

Scalene is a profiler designed to provide CPU and memory-oriented insights, including distinctions between Python and native execution in supported environments; some releases and environments also expose GPU-related measurements. Its capabilities, overhead, and options vary by release and platform.

Typical invocation patterns include:

```bash
scalene --help
scalene run etl.py data/events.csv
```

Use the exact invocation supported by the installed version. Scalene is useful when you need line-oriented context or want to investigate whether time is spent in Python versus native code, and when CPU and memory behavior may be related. It is not interchangeable with `py-spy`: the instrumentation, reports, supported environments, and overhead characteristics differ.

### pyinstrument

pyinstrument is a statistical profiler that emphasizes call-stack views and wall-clock time. It can be useful for request handlers, web applications, and workloads where waiting time matters.

Inspect the installed version’s help and integration documentation. A simple script workflow may resemble:

```bash
pyinstrument etl.py data/events.csv
```

For a web handler, use a documented framework integration or a narrowly scoped profiling context in a controlled environment. Avoid enabling detailed profiling for every production request by default. Prefer sampling a small, approved fraction of requests or reproducing the issue in staging. For notebooks, use the documented IPython/Jupyter integration supported by the installed pyinstrument version, and keep profiling scoped to the cell or operation under investigation.

### Choosing a tool

- **`py-spy`:** attach to a running process, inspect threads, record a sampled profile.
- **Scalene:** investigate Python/native CPU contribution and line-level CPU/memory questions.
- **pyinstrument:** inspect a call tree with wall-clock-oriented statistical evidence, useful for request paths.
- **`cProfile`:** controlled deterministic call counts and function-level timings, often for a reproducible script.

Use the tool that answers the question. Do not compare their raw percentages as though all profilers measure the same thing.

---

## 11. Production safety and sensitive artifacts

Profiles can expose:

- Internal module and file paths, repository names, function names, and service architecture.
- Request handlers, tenant-specific code paths, or names embedded in stack frames.
- Command-line arguments, environment details, or other process metadata, depending on tooling.
- Native library versions and deployment details.

Before capturing:

1. State the question and the expected duration.
2. Obtain the required operational approval.
3. Prefer a bounded capture and a low-impact sampling configuration.
4. Avoid including secrets in command-line arguments; command lines may be visible to other processes and may be captured by diagnostics.
5. Store artifacts in approved restricted storage, encrypt where required, and set retention/deletion expectations.
6. Redact paths or metadata before sharing externally, while preserving enough context for interpretation.
7. Do not upload sensitive profiles to public viewers or paste them into public issue trackers.

Sampling overhead is workload- and configuration-dependent. It can be small for some workloads and material for others, especially at higher sampling rates or with native stack collection. Measure impact on a representative non-production workload when possible. In production, monitor latency and resource metrics during the capture and stop if safety thresholds are breached. Do not promise a universal overhead percentage.

`py-spy` reads the target process from outside the application, but do not translate that into a guarantee of zero impact: platform and mode affect how stacks are read, and some collection paths briefly pause the target. Its `--nonblocking` option (where supported) avoids pausing the target but can produce sampling errors or partial stacks because memory reads are not atomic. Check `py-spy record --help` and the upstream documentation before choosing that trade-off.

---

## 12. A shared `slowlog` investigation

The aim is to practice the complete sequence:

**symptom → profile → hypothesis → controlled change → correctness check → new evidence → report**

The example below intentionally performs repeated parsing and inefficient membership checks. It uses only the Python standard library. The generated data is synthetic; it is not a benchmark result.

### 12.1 Create the workload

Save this as `slowlog.py`:

```python
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def generate_csv(path: Path, rows: int = 50_000) -> None:
    """Create reproducible synthetic log events for local profiling."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "level", "service", "message"])
        for index in range(rows):
            writer.writerow(
                [
                    f"2026-01-{(index % 28) + 1:02d} 12:{(index % 60):02d}:00",
                    ("ERROR" if index % 17 == 0 else "INFO"),
                    ("payments" if index % 3 == 0 else "catalog"),
                    f"event-{index % 500} request processed",
                ]
            )


def analyze_slow(path: Path, watched_services: list[str]) -> dict[str, int]:
    """Deliberately inefficient version used as a profiling exercise."""
    error_count = 0
    watched_count = 0
    parsed_timestamps = 0

    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            # Deliberate repeated parsing: the parsed datetime is not used.
            datetime.strptime(row["timestamp"], TIMESTAMP_FORMAT)
            parsed_timestamps += 1

            if row["level"] == "ERROR":
                error_count += 1

            # Deliberate linear membership test on every row.
            if row["service"] in watched_services:
                watched_count += 1

    return {
        "rows": parsed_timestamps,
        "errors": error_count,
        "watched": watched_count,
    }


def analyze_optimized(path: Path, watched_services: list[str]) -> dict[str, int]:
    """Optimization candidate: remove unused parsing and use set membership."""
    watched = set(watched_services)
    error_count = 0
    watched_count = 0
    row_count = 0

    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            row_count += 1

            if row["level"] == "ERROR":
                error_count += 1

            if row["service"] in watched:
                watched_count += 1

    return {
        "rows": row_count,
        "errors": error_count,
        "watched": watched_count,
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python slowlog.py generate|slow|fast PATH"
        )

    mode, raw_path = sys.argv[1], sys.argv[2]
    path = Path(raw_path)

    if mode == "generate":
        generate_csv(path)
        print(f"Generated {path}")
        return

    watched = ["payments", "catalog"]
    if mode == "slow":
        result = analyze_slow(path, watched)
    elif mode == "fast":
        result = analyze_optimized(path, watched)
    else:
        raise SystemExit(f"Unknown mode: {mode}")

    print(result)


if __name__ == "__main__":
    main()
```

This script is intentionally educational. The `slow` version parses each timestamp but discards the result; removing unused work is valid only if parsing has no required validation or side effect. In a real ETL pipeline, parsing might be part of input validation or normalization, so you must preserve the contract before removing it.

### 12.2 Generate data and verify the baseline

```bash
python slowlog.py generate events.csv
python slowlog.py slow events.csv
```

The output should resemble this shape (the exact row count follows the configured generator; these are expected logical counts, not measured timings):

```text
Generated events.csv
{'rows': 50000, 'errors': 2942, 'watched': 50000}
```

All generated rows use one of the two watched services, so the watched count equals the row count. The error count depends on the generator's `index % 17 == 0` rule.

### 12.3 Capture a profile

Profile the script as a command:

```bash
py-spy record --output slowlog-before.svg -- python slowlog.py slow events.csv
```

If you need a Speedscope artifact and your version supports it:

```bash
py-spy record --format speedscope --output slowlog-before.json -- python slowlog.py slow events.csv
```

Open the flame graph or Speedscope file using an approved viewer. Record:

- Tool and version.
- Python version and operating system.
- Dataset size and how it was generated.
- Recording duration and sample rate.
- The widest repeated stack paths and their approximate sample share.
- Whether CPU was saturated or the process appeared to wait.

**Do not copy made-up percentages into the report.** Your actual profile may show timestamp parsing, CSV handling, interpreter overhead, or another path as dominant depending on machine, Python version, dataset, and sampling configuration.

### 12.4 Form a hypothesis from evidence

Suppose your profile shows a large share of samples in `datetime.strptime` reached through `analyze_slow`. The hypothesis is:

> The workload spends material CPU time parsing timestamps whose values are never used; removing this unnecessary work should reduce CPU work without changing the returned summary.

This is a hypothesis, not a conclusion. If parsing is a required validation step in your real application, removing it would be a correctness regression. The second example is valid only because the exercise defines timestamp parsing as unused.

If instead the profile is dominated by file I/O, do not assume the parser is the bottleneck. Check storage throughput, row count, and whether the job is CPU- or I/O-bound before selecting a change.

### 12.5 Check correctness before performance

Run both implementations on the same input:

```bash
python slowlog.py slow events.csv
python slowlog.py fast events.csv
```

The dictionaries should match. For a repeatable test, add `test_slowlog.py`:

```python
from pathlib import Path

from slowlog import analyze_optimized, analyze_slow, generate_csv


def test_optimized_matches_reference(tmp_path: Path) -> None:
    path = tmp_path / "events.csv"
    generate_csv(path, rows=1_000)

    expected = analyze_slow(path, ["payments", "catalog"])
    actual = analyze_optimized(path, ["payments", "catalog"])

    assert actual == expected
```

Run:

```bash
python -m pip install pytest
python -m pytest -q
```

This test checks result equivalence for a generated fixture. It does not prove performance, validate malformed CSV behavior, or establish all production requirements. Add tests for malformed rows and required validation if those are part of the real contract.

### 12.6 Capture the second profile

```bash
py-spy record --output slowlog-after.svg -- python slowlog.py fast events.csv
```

Compare the same evidence dimensions:

- Same machine, Python build, data, and profiler configuration.
- Similar recording windows and enough samples for stable interpretation.
- Whether the hypothesized stack shrank or disappeared.
- Whether a different stack became dominant.
- Whether correctness tests still pass.
- Unprofiled end-to-end runtime measured separately using a controlled benchmark method (covered in Lesson 03).

Do not infer a numerical speed-up from a visual flame graph alone. A flame graph shows sample proportions, and total sample counts can differ between recordings. If the profile shifts from timestamp parsing to CSV parsing, that may be expected after removing work; it does not mean CSV parsing became slower in absolute terms.

**Important:** `py-spy`'s profile is evidence about sampled execution. It is not a replacement for controlled unprofiled timing, and it does not guarantee that production latency improves by the same proportion.

---

## 13. Advanced diagnosis patterns

### 13.1 GIL contention

Symptoms can include poor throughput scaling as CPU-bound Python threads are added, with the GIL limiting simultaneous execution of Python bytecode on a conventional GIL-enabled build. A `--gil` profile can help show sampled stacks from threads holding the GIL, but it is only one view. Check CPU utilization per core, thread states, blocking calls, native extensions that release the GIL, and whether the workload is actually CPU-bound. Low total CPU alone is not evidence of GIL contention; it can indicate waiting, throttling, or underutilization. On free-threaded builds, do not apply conventional GIL assumptions without checking the runtime build and profiler support.

Do not diagnose GIL contention solely because the application uses threads. I/O-bound threads may be effective, and native extensions may release the GIL.

### 13.2 Blocked event loop

An `async def` function can still call blocking synchronous code. If that call runs on the event-loop thread, unrelated tasks may stall. Use sampled stacks to look for synchronous network/file calls, CPU-heavy parsing, or long-running serialization on the loop thread. Correlate with event-loop lag and request latency metrics. Use async libraries or an executor where appropriate, and test cancellation and timeout behavior.

### 13.3 Lock convoys and starved thread pools

Capture multiple stack snapshots at intervals. If many workers wait on the same lock, inspect the critical section and lock owner. If a thread pool is fully occupied by tasks waiting for work scheduled on that same pool, investigate dependency cycles and pool sizing. A single stack dump cannot establish the lock owner or prove a deadlock cycle; use lock instrumentation, thread dumps, logs, and controlled reproduction.

### 13.4 Slow imports and startup latency

For startup investigations, use Python’s import timing output:

```bash
python -X importtime -c "import your_package"
```

This is a separate diagnostic from `py-spy`. Import timing can reveal expensive import trees; sampled profiling of a short-lived startup process may not collect enough samples to be useful. Distinguish import time from initialization, network calls during startup, and application warm-up.

### 13.5 Runaway regular expressions

A pathological regex can consume CPU disproportionately for certain inputs. A profile may show regex engine frames or the Python call that invokes a regex. Reproduce with representative and adversarial input sizes, inspect regex complexity, and add input limits/timeouts where the engine supports them. Avoid sending untrusted pathological input into an expensive regex path. Do not rely on a short profile to rule out rare catastrophic cases.

### 13.6 Serialization bottlenecks

JSON encoding/decoding, compression, pickling, and DataFrame serialization may dominate a profile. Determine whether the time is in Python wrappers or native code. Then test payload size, schema complexity, repeated serialization, copying, and whether serialization is happening more often than necessary. Preserve wire compatibility and validate output equivalence before changing formats or batching.

### 13.7 Native frames in NumPy, pandas, PyTorch, and extensions

With supported native-stack collection, a profile may include frames from C/C++ or other extension code. Read these alongside Python callers and the library’s own profiling tools. A Python frame that calls `DataFrame.apply` may be a clue that work is repeated row by row; a native frame can show that computation moved into a library. Neither automatically proves which API change is correct.

Native stack quality depends on symbols, compiler/build options, operating system, and tool support. When frames are unresolved, combine sampling with application-level timing, library diagnostics, and OS profilers such as Linux `perf` where permitted.

---

## 14. Correlate profiles with system evidence

Profiles explain stack activity; operating-system and service metrics explain resource conditions. Capture evidence for the same time window whenever possible.

```bash
# Linux examples; availability and permissions vary.
top -H -p 12345
pidstat -p 12345 1
lsof -p 12345
strace -c -p 12345
```

`strace -c` summarizes system calls observed during its trace window, but tracing can add overhead and may require elevated permissions. Use it carefully and only where authorized. `lsof` can help inspect open files/sockets but is not a CPU profiler. `pidstat` can help correlate CPU, I/O, and scheduling behavior. Linux `perf` can provide lower-level CPU/hardware evidence but has kernel, permissions, and symbolization constraints.

For containers, correlate with cgroup CPU throttling, memory limits, I/O limits, queue depth, worker utilization, database latency, and upstream request metrics. A process may appear slow because it is throttled or starved even if its Python stack looks ordinary.

Maintain a shared timeline containing:

- Profile start/end time and sample rate.
- Process ID, container/pod, deployment/release, and workload identifier.
- CPU usage, throttling, RSS, I/O, queue depth, and relevant service latency.
- Incident events, retries, timeouts, and upstream status.
- Any change in traffic, input size, or worker count.

Avoid logging secrets or customer payloads into the investigation report.

---

## 15. Continuous profiling and release comparisons

Continuous profiling systems such as Grafana Pyroscope (the project historically called Grafana Phlare), Datadog profiling, or Sentry profiling collect sampled execution data over time and associate it with services, versions, and environments. Product capabilities and names can change; verify the current supported deployment, agent compatibility, data residency, and retention model before adopting a system.

A useful release comparison asks:

- Did the share of samples in a particular stack change between releases?
- Did the total request/job volume or workload mix change?
- Is the comparison normalized per request, task, or unit of input?
- Did a new dependency, deployment configuration, or Python version change?
- Are the same sampling configuration and comparable environments used?

A relative increase in sample share is not necessarily an absolute slowdown: another stack may have become cheaper, or traffic mix may have changed. Compare with latency/throughput metrics and representative workload data. For regressions, keep profiles as controlled artifacts, restrict access, and use stable call-count or functional assertions where appropriate rather than brittle wall-clock thresholds in shared CI runners.

---

## 16. Newer Python profiling and attach capabilities

The roadmap calls for awareness of the built-in sampling profiler (`profiling.sampling`, PEP 799) and process-attachment debugging (`python -m pdb -p PID`, PEP 768). These are release-specific features, not generic capabilities of every Python 3.12+ interpreter. The Python 3.15 documentation lists `profiling.sampling` as added in 3.15; `pdb -p` was added in Python 3.14. The `py-spy` support matrix consulted here lists support through CPython 3.14, so verify its current release support before using it with Python 3.15.

Start by checking the target interpreter and its documented feature set:

```bash
python --version
python -m profiling.sampling --help
python -m pdb -h
```

On Python 3.15 or later, if the module is present and supported, the built-in sampler can launch a workload or attach to an existing PID:

```bash
python -m profiling.sampling run -d 30 --flamegraph -o slowlog-profile.html slowlog.py slow events.csv
python -m profiling.sampling attach 12345
python -m profiling.sampling dump 12345
```

Use the exact commands/options in the documentation for the installed minor release. The built-in sampler has its own runtime/platform requirements and should not be assumed interchangeable with `py-spy`; in particular, verify profiler/target version compatibility and permissions. `pdb` is a debugger, not a sampling profiler. Attach with `python -m pdb -p PID` only when interactive debugging is warranted and approved; it can perturb or pause the target, and attaching to a process blocked in a system call or waiting for I/O may not take effect until it executes another bytecode instruction or receives a signal.

Do not change production runtime versions during an incident merely to gain a diagnostic feature without a change plan.

---

## 17. Troubleshooting

### “Permission denied” or attach fails

1. Confirm the PID is correct and still exists.
2. Confirm the profiler runs as an identity permitted to inspect that process.
3. On Linux, check ptrace/Yama policy and container namespace/capability constraints.
4. Confirm the process and profiler are in compatible host/container environments.
5. Check OS and `py-spy` version support.
6. Request approved elevated access if necessary; do not globally weaken security controls.

### Profile is empty or contains too few samples

- The process may have exited before enough samples were collected.
- The workload may be too short; run a representative longer workload or attach during the active phase.
- The selected process may be a wrapper or idle parent rather than the worker.
- Permissions or unsupported runtime details may limit observation.
- Verify that the profile file was created and is readable.

### Flame graph appears dominated by an unexpected function

- Check whether the function is a parent with expensive descendants.
- Inspect native frames and Python callers.
- Confirm the workload was representative and the observation window was not mostly startup or waiting.
- Repeat the capture and correlate with metrics before changing code.

### Results differ between runs

- Compare workload size and distribution, release/build, sample rate, duration, CPU throttling, and concurrency.
- Separate startup, warm-up, steady-state, and drain phases.
- Consider sampling variance and intermittent waits.
- Use repeated captures and a controlled benchmark for latency claims.

### Native frames are missing

- Check `--native` availability and platform support.
- Check native symbol availability and debug-symbol policy.
- Recognize that stack unwinding may be incomplete.
- Combine with application metrics or an approved OS-level profiler.

### `--subprocesses` or an output format is rejected

The installed version may not support that option, or the current platform/output format may restrict it. Read the installed `py-spy record --help`; choose a supported output format and profile child processes explicitly if necessary.

---

## 18. Common mistakes

1. Treating sample percentages as exact function timings.
2. Reading flame-graph width as time order.
3. Recording too briefly to capture a representative workload.
4. Raising the sample rate without considering overhead and artifact size.
5. Assuming `py-spy` can inspect every process on every platform.
6. Forgetting PID namespaces, ptrace restrictions, container security, or Kubernetes policy.
7. Interpreting an idle or blocked stack as CPU consumption.
8. Assuming one stack snapshot proves a deadlock or root cause.
9. Ignoring child processes when the job uses multiprocessing.
10. Treating native frames as complete when symbols or unwinding are missing.
11. Comparing profiles from different workloads/releases without normalizing traffic and workload mix.
12. Uploading a sensitive profile to an unapproved public viewer.
13. Claiming a change improved production latency solely because a flame graph looks different.
14. Changing code before checking the application’s correctness contract.

---

## 19. Exercises

### Exercise A — Sampling intuition

A 20-second capture at 80 samples/second has about 1,600 nominal sample opportunities.

1. What fraction would 320 samples represent?
2. Why is that not an exact claim that the corresponding function consumed precisely 20% of wall time?
3. Name two reasons actual usable samples might be fewer than the nominal count.

### Exercise B — Interpret a stack snapshot

Illustrative stack:

```text
MainThread
  run_job
  write_results
  json.dumps
  JSONEncoder.iterencode
```

Write three plausible hypotheses and identify one additional piece of evidence needed for each. Do not conclude that JSON serialization is definitely the only bottleneck from this one snapshot.

### Exercise C — Compare CPU and wait symptoms

A job’s wall time rises, but process CPU stays low. Describe how you would use `py-spy dump`, a bounded recording, and OS/service metrics to distinguish network wait, lock contention, and worker-pool starvation.

### Exercise D — Tool choice

For each scenario, choose a tool and justify it:

1. A production worker is slow right now and cannot be restarted.
2. A reproducible script has a hot function with suspicious call counts.
3. A web request spends time waiting and you need a call-tree view.
4. A NumPy-heavy workload may be spending time in native code.

### Exercise E — Safe profile handling

Write a short checklist for approving a profile capture in a production Kubernetes namespace. Include permissions, capture duration, impact monitoring, artifact access, and retention.

---

## 20. Self-check questions

1. Why does sampling usually have lower overhead than deterministic function-call instrumentation, and when might that advantage shrink?
2. Why does a low sampling rate make short runs less informative?
3. What does width represent in a flame graph? What does vertical depth represent?
4. Why is horizontal position not a chronological timeline?
5. When would `py-spy dump --pid PID` be more useful than a recorded flame graph?
6. A service has slow requests and 10% CPU utilization. Which evidence would help distinguish I/O wait, event-loop blocking, and lock contention?
7. Why can a parent process’s profile miss the dominant work in a multiprocessing job?
8. What can `--native` add, and why might native frames still be incomplete?
9. How would you use `--gil` without overclaiming that GIL contention is the root cause?
10. What should you verify before using a newer built-in profiling or attach feature?
11. Why must a before/after profile comparison control for workload and release differences?
12. What information belongs in a safe production profiling report?

---

## 21. Final hands-on task: “slow or hung job” investigation

Use the `slowlog.py` workload above or the module’s shared slowlog/ETL project.

Deliver a concise investigation report containing:

1. **Question and symptom:** define the slow or hung behavior, expected behavior, and operational impact.
2. **Environment:** Python/tool versions, OS/container, release, process/worker identity, dataset size and shape.
3. **Capture plan:** tool, command, duration, sample rate, permission path, safety/rollback plan.
4. **Evidence:** flame graph or Speedscope artifact, dominant stack paths, sample counts/percentages as actually observed, and relevant system metrics.
5. **Hypothesis:** one falsifiable explanation tied to a specific stack and workload.
6. **Change:** the smallest change that tests the hypothesis; document any correctness or compatibility risk.
7. **Correctness:** tests that compare outputs and cover the relevant edge cases.
8. **Re-measurement:** repeat the capture with comparable settings and data; separately measure unprofiled end-to-end performance.
9. **Conclusion:** state what the evidence supports, what remains uncertain, and whether further investigation is needed.
10. **Artifact handling:** storage location, access controls, redaction, and retention/deletion plan.
11. **Escalation:** if repeated snapshots and metrics do not distinguish the cause, preserve the evidence and escalate to the service owner/on-call lead. Escalate immediately if the capture breaches latency/resource guardrails, the process is at risk of termination, or access would require unapproved privilege changes. Do not broaden privileges or extend capture duration without approval.

### Report template

```text
Incident / investigation:
Question:
Observed symptom:
Expected behavior:
Python / py-spy versions:
OS / container / deployment:
Workload and input size:
Capture command and settings:
Capture window:
System metrics during capture:
Dominant sampled stacks:
Hypothesis:
Change made:
Correctness checks:
Before/after profile comparison:
Unprofiled timing method and results:
Risks / trade-offs:
Limitations and remaining uncertainty:
Artifact location and access/retention:
Next action:
```

Do not invent percentages, timings, or speed-ups. If the evidence is inconclusive, say so and describe the next experiment.

---

## 22. Completion criteria

You are ready to move on when you can:

- Capture a live view, a bounded recording, and a stack snapshot with `py-spy`.
- Explain sampling uncertainty and the difference between sample-derived estimates and exact function timings.
- Read flame graphs and Speedscope output without treating them as timelines.
- Diagnose common permission and platform issues safely.
- Combine profile evidence with CPU, I/O, queue, and service metrics.
- Form and test a bottleneck hypothesis on the slowlog workload while preserving correctness.
- Produce a reproducible, security-conscious investigation report.

The core production habit is simple: **sample to discover where execution is active, correlate to understand the system state, then test a specific hypothesis and verify the change.**

---

## 23. References and version checks

Use these sources for tool-specific behavior and release compatibility. Recheck them when upgrading the profiler or Python runtime; command-line options can change.

- [`py-spy` upstream README and platform/permission notes](https://github.com/benfred/py-spy) — commands, output formats, subprocesses, native frames, GIL filtering, and attach restrictions.
- [Python 3.15 `profiling.sampling` documentation](https://docs.python.org/3.15/library/profiling.sampling.html) — built-in sampler introduced in Python 3.15; use only with a compatible runtime and supported target.
- [Python 3.14 `pdb` documentation](https://docs.python.org/3.14/library/pdb.html) — `-p/--pid` attachment added in Python 3.14 and its limitations.
- [PEP 799](https://peps.python.org/pep-0799/) — standard-library profiling package organization and Python 3.15 changes.
- [PEP 768](https://peps.python.org/pep-0768/) — safe external debugger interface for CPython, Python 3.14.
- [Scalene documentation](https://github.com/plasma-umass/scalene) — version-specific invocation and supported measurements.
- [pyinstrument documentation](https://pyinstrument.readthedocs.io/) — script, framework, and notebook integration.
- [Speedscope](https://www.speedscope.app/) — profile viewer. Use an approved local/internal viewer for confidential artifacts.
- [Grafana Pyroscope documentation](https://grafana.com/docs/pyroscope/latest/) — continuous profiling deployment, storage, and retention considerations.

The lesson’s roadmap requirements are derived from `roadmap-Profiling-Memory-and-Runtime-Performance.md`; external references above verify tool and runtime behavior and do not replace that curriculum scope.
