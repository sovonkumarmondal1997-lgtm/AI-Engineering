# Roadmap — Module 1.17: Profiling, Memory and Runtime Performance

This is the learning roadmap for the seventeenth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about measuring and improving Python performance, **in what order**,
**how** to practise each topic, and **how to prove to yourself** that you
have learned it.

Module 1.10 (lesson 06) taught the discipline: **measure before you
optimise**. This module gives you the tools and the mental model to do it —
CPU profilers, flame graphs, sampling profilers for production,
microbenchmarks, memory tracing, the garbage collector, CPython performance
idioms, and how to call native code when Python itself is the bottleneck.

Algorithmic complexity (Big-O) was covered in Module 1.4 and Stage 3; large-scale
data tooling (NumPy vectorisation, Numba/Cython, Dask, Ray, Polars) is covered in
Stage 2, modules 02, 04 and 21. This module **does not repeat them**; it gives
you the Python-level profiling and memory skills those stages depend on.

> Target: **Python 3.12+**. Notes for 3.13/3.14 (JIT, free-threading, new profilers) are flagged inline.

---

## 1. Module outcome

By the end of this module you will be able to:

- Profile CPU time with `cProfile`/`pstats`, read cumulative vs total time, call graphs, and flame graphs.
- Attach a **sampling profiler** (`py-spy`, `scalene`, the built-in sampling profiler arriving in newer releases (`profiling.sampling`, PEP 799)) to a running process with low overhead.
- Write correct microbenchmarks with `timeit`/`pyperf`/`pytest-benchmark` and avoid common measurement traps.
- Find memory leaks and big allocators with `tracemalloc`, `memray`, `gc` and `objgraph`.
- Explain reference counting, the cyclic garbage collector and tune it where justified.
- Apply CPython performance idioms (local variables, builtins, comprehensions, `str.join`, `__slots__`, caching) and know which are myths.
- Call native code with `ctypes`/`cffi` and describe when C/C++/Rust extensions (PyO3, pybind11, Cython) are worth it.
- Produce a written performance investigation: hypothesis → measurement → change → verification.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Big-O, choosing data structures | Module 1.4 (03, 04) | Most speed-ups are algorithmic |
| Profiling mindset | Module 1.10 (06) | This module is the toolbox |
| Python object model & garbage collection | Module 1.9 (10) | Memory behaviour |
| Generators and memory trade-offs | Module 1.9 (01, 04) | Streaming vs materialising |
| `__slots__`, descriptors | Module 1.11 (06, 07) | Memory layout |
| `weakref`, `contextvars` | Module 1.13 (10) | Leaks and caches |
| Bytes / `memoryview` / `mmap` | Module 1.14 | Zero-copy techniques |
| Testing and CI | Modules 1.7, 1.16 | Performance regression tests |
| How computers work (CPU, cache, RAM) | Stage 0 — Module 0.1 | Explains *why* things are slow |

**Tools:** `uv add --dev py-spy memray scalene pyperf pytest-benchmark snakeviz objgraph line_profiler`.
On Linux/WSL2 `py-spy` may require `sudo` or `ptrace` permissions
(`kernel.yama.ptrace_scope`).

---

## 3. How the module is organised

```text
Phase A — Where Does the Time Go?               (Basics → Intermediate)
  01 cProfile, pstats and flame graphs
  02 sampling profilers with py-spy (and friends)
  03 timeit and microbenchmark pitfalls
Phase B — Where Does the Memory Go?             (Intermediate → Advanced)
  04 tracemalloc and leak hunting
  05 memray and allocation analysis
  06 garbage collector tuning and reference cycles
Phase C — Making It Faster                      (Advanced)
  07 CPython performance idioms
  08 ctypes and cffi for native code
  09 C and Rust extensions awareness
```

Pace: about 3 weeks part-time. Use one shared, deliberately inefficient
sample app (a log-analysis/ETL script with a leak and a hot loop) for all lessons.

---

## Lesson 01 — `01-cprofile-pstats-and-flame-graphs.md`

**Why it matters.** Intuition about "what is slow" is wrong surprisingly
often. A deterministic profiler tells you which functions consume time and
how often they are called, so you fix the real bottleneck.

### Basic — what to learn

- Run: `python -m cProfile -o out.prof script.py`; `python -m cProfile -s cumtime script.py`.
- Columns: `ncalls`, `tottime` (time in the function itself), `cumtime`
  (including callees), `percall`.
- Read the **top 10 by cumulative time** first, then by `tottime`.
- Profile with context manager (3.8+): `with cProfile.Profile() as pr: ...; pr.print_stats("cumtime")`.

```python
import cProfile, pstats
with cProfile.Profile() as pr:
    main()
pstats.Stats(pr).sort_stats("cumulative").print_stats(15)
```

### Intermediate — what to learn

- `pstats.Stats`: `strip_dirs`, `sort_stats`, `print_callers`, `print_callees`, filtering by regex.
- Visualising: **snakeviz** (icicle/sunburst), `gprof2dot` → Graphviz call graph, flame graphs
  via `flameprof`/`py-spy`; how to read width = time.
- Profiling overhead: deterministic profilers slow code (especially many tiny calls) and distort ratios;
  don't compare absolute numbers with unprofiled runs.
- Profiling tests and scripts selectively: `pytest --profile` (`pytest-profiling`) or decorating a hot entry point.
- Line-level detail: `line_profiler` (`@profile`, `kernprof -lv`) for a function you've already narrowed down.
- Profile **representative** workloads (realistic data size and shape), not toy inputs; warm caches; run several times.

```bash
python -m cProfile -o etl.prof etl.py data/big.csv
uv run snakeviz etl.prof
```

### Advanced — what to learn

- Profiling threads, async code and multiprocessing: `cProfile` only sees the thread it started in;
  per-process profiles and merging; async profilers show await time as cumulative in the event loop.
- Interpreting results: recursion inflating `cumtime`; C functions appearing as built-ins;
  generator frames; attribution of lambda/comprehension frames.
- **Amdahl's law**: speed-up limited by the fraction improved; decide whether a 30 % function is worth optimising.
- Differential profiling: compare two profiles (before/after) to confirm improvement and spot regressions.
- Profiling in CI for regressions (store `.prof` artifacts; budgets on call counts rather than flaky seconds).
- Python 3.12+ `sys.monitoring` and the newer low-overhead profiling APIs (awareness; Module 1.19 lesson 10).
- Common findings: repeated parsing/compiling (regex, datetime formats), N+1 queries, repeated string concatenation,
  accidental O(n²) `in list`, logging overhead, JSON encoding/decoding costs, pandas row-wise `apply`.
- Writing the investigation report: baseline, profile, hypothesis, change, result, risks.

### Common mistakes

- Optimising based on a toy dataset.
- Reading `tottime` of the wrong function (look at callers/callees).
- Trusting profiled wall time as real performance.

### Self-check

1. Difference between `tottime` and `cumtime`?
2. Why can deterministic profiling mislead for code with millions of tiny calls?
3. Profile the sample ETL script, find the top bottleneck, fix it, and prove the improvement with a second profile.

---

## Lesson 02 — `02-sampling-profilers-with-py-spy.md`

**Why it matters.** In production you can't restart a service with a
deterministic profiler, and overhead distorts results. Sampling profilers
periodically capture stack traces from an existing process with minimal
overhead — essential for "why is this job stuck/slow *right now*?".

### Basic — what to learn

- How sampling works: N samples/second of call stacks; the most frequent
  stacks are where time goes; statistically accurate with enough samples.
- `py-spy top --pid <PID>` (live), `py-spy record -o profile.svg -- python app.py`
  (flame graph), `py-spy dump --pid <PID>` (current stacks of all threads — great for hangs).
- Reading a flame graph: x-axis = proportion of samples (not time order), y-axis = stack depth.

```bash
py-spy record -o flame.svg --rate 100 -- python etl.py data/big.csv
py-spy dump --pid 12345          # where is it stuck right now?
```

### Intermediate — what to learn

- Options: `--native` (C frames), `--gil` (only GIL holders), `--idle`, `--subprocesses`, `--format speedscope|flamegraph|raw`;
  loading `speedscope` JSON in the browser.
- Attaching permissions: `ptrace`, containers (`--cap-add SYS_PTRACE`), Kubernetes ephemeral containers; macOS/Windows differences.
- CPU-bound vs I/O-bound vs lock-bound: use `--idle` and wall-clock vs CPU views to separate waiting from computing.
- **Scalene**: CPU + memory + GPU line-level sampling profiler with Python-vs-native split; **pyinstrument** (statistical wall-clock, good for web requests).
- Profiling a web request/handler with pyinstrument middleware; profiling notebooks.
- Safe use in production: low overhead (typically < 1–5 %), but still announce, limit duration, avoid exposing flame graphs containing sensitive paths/data.

### Advanced — what to learn

- Always-on continuous profiling (Pyroscope, Grafana Phlare, Datadog/Sentry profiling): low-frequency sampling shipped to a backend, diffing releases.
- Diagnosing: GIL contention (many threads, low CPU use), blocked event loop (sync call inside `async def`), slow imports (`python -X importtime`),
  startup latency, lock convoys, thread pools starved, runaway regex, serialisation hotspots.
- Correlating with system metrics: `top`, `pidstat`, `perf` (Linux), `strace -c`, `lsof` (Stage 0 tools).
- Newer Python releases: the built-in sampling profiler (`profiling.sampling`, PEP 799; check which release ships it) and `python -m pdb -p PID` attach (3.14, PEP 768) — compare with `py-spy`.
- Interpreting native frames from NumPy/pandas/PyTorch/C extensions; combining with `perf`/`py-spy --native`.
- Debugging a hung production job from `py-spy dump` output: find the blocking call, deadlock cycle, or missing timeout.
- Sampling bias and limits: short functions between samples, inlined C code, sleeping stacks.
- Runbook entry: "Job is slow/hung" → exact commands, expected outputs, escalation.

### Common mistakes

- Using too low a sampling rate for short runs.
- Reading flame graph width as time order.
- Forgetting permissions inside containers.

### Self-check

1. Why does sampling have lower overhead than deterministic profiling?
2. A service shows 10 % CPU but requests are slow: which `py-spy` view helps and what might you find?
3. Write the runbook steps for investigating a hung batch job with `py-spy dump`.

---

## Lesson 03 — `03-timeit-and-microbenchmark-pitfalls.md`

**Why it matters.** Microbenchmarks answer "is A faster than B?" for small
code. They are also the easiest place to fool yourself: warm-up, caching,
dead-code elimination, noisy machines, wrong inputs, and measuring the wrong thing.

### Basic — what to learn

- `timeit.timeit(stmt, setup, number)`, `repeat`, `Timer.autorange`; command line `python -m timeit -s "setup" "stmt"`.
- Use `min()` of repeats as the best estimate of the code's intrinsic speed (noise is additive).
- `time.perf_counter()` for ad-hoc timings (monotonic, high resolution); never `time.time()` for durations.

```python
import timeit
t = timeit.repeat("sum(x*x for x in data)", setup="data=list(range(10_000))",
                  repeat=5, number=200)
print(min(t) / 200)
```

### Intermediate — what to learn

- Fair comparisons: same input size/shape, include conversions, avoid global-lookup artefacts, don't benchmark `print`.
- Realistic inputs: sizes at several scales (n = 10, 10³, 10⁶) to see complexity curves; plot results.
- Tools: **`pyperf`** (multiple processes, calibrates, statistics, system tuning), **`pytest-benchmark`**
  (benchmarks in the test suite, saved baselines, comparison `--benchmark-compare`), `asv` for long-term tracking.
- Pitfalls: CPU frequency scaling, noisy neighbours, background processes, thermal throttling; laptop vs CI machine;
  Python version/build flags (PGO/LTO), debug builds; first-run effects (import, cache, JIT warm-up).
- Memory-allocation effects: GC pauses during timing (`timeit` disables GC by default — `gc.enable()` in setup if relevant).
- Reporting: median/min, spread, number of runs, environment details (Python version, CPU, OS).

```python
def test_sort_benchmark(benchmark):
    data = list(range(100_000, 0, -1))
    result = benchmark(sorted, data)
    assert result[0] == 1
```

### Advanced — what to learn

- Statistics for benchmarks: confidence intervals, effect size, avoiding p-hacking; when two means overlap, don't claim a win.
- Benchmark design traps: constant folding by the peephole optimiser, dead-code removal, caching in `lru_cache`/dict memo,
  copy-on-write, memoised regexes, memory locality, branch prediction and data-dependent speed (sorted vs random input).
- Microbenchmarks vs macrobenchmarks: a 2× faster function inside a 1 % hot path is irrelevant; validate with end-to-end timing.
- Benchmarking I/O, network and database code: separate warm vs cold, use realistic latency, avoid local-loopback illusions.
- CPython versions & builds: 3.11+ specialising interpreter, 3.13 JIT flag (`PYTHON_JIT=1`), free-threaded penalty in single-thread
  code (measure instead of assuming).
- Performance regression gating in CI: store baselines, tolerate noise with relative thresholds and repeated runs, run on dedicated runners.
- Writing a "benchmark claims" checklist: hypothesis, setup, controls, results, caveats, reproducible script.
- Myth-busting exercises (see lesson 07): test commonly repeated performance folklore yourself.

### Common mistakes

- Benchmarking with tiny inputs or inputs that differ between variants.
- Reporting the mean of noisy runs.
- Drawing conclusions from one machine or one run.

### Self-check

1. Why use `min()` of `repeat()` for microbenchmarks?
2. Benchmark `list` vs `set` membership for n = 10 … 10⁶ and explain the curve.
3. Design a CI check that fails only when a benchmark regresses by > 20 % across three runs.

---

## Lesson 04 — `04-tracemalloc-and-memory-leak-hunting.md`

**Why it matters.** Long-running Python services and batch jobs grow in
memory: caches without limits, global registries, reference cycles with
`__del__`, accumulating lists, closures holding large objects. OOM kills
production jobs at 3 a.m.

### Basic — what to learn

- Where Python memory goes: objects, containers, buffers; `sys.getsizeof` (shallow!) vs deep size.
- `tracemalloc.start()`, `take_snapshot()`, `snapshot.statistics("lineno")`, `get_traced_memory()`.
- Compare snapshots: `snap2.compare_to(snap1, "lineno")` shows which lines allocated more.

```python
import tracemalloc
tracemalloc.start(10)               # keep 10 frames per allocation
before = tracemalloc.take_snapshot()
run_workload()
after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:10]:
    print(stat)
```

### Intermediate — what to learn

- Leak patterns: unbounded caches/dicts/lists, global registries, listeners never removed, `lru_cache` on methods,
  exceptions keeping tracebacks (frames) alive, thread/task leaks, closures, `contextvars` values, logging handlers accumulating.
- Process-level vs Python-level memory: RSS vs `tracemalloc` (allocator fragmentation, native/C allocations, arenas not returned to the OS).
- `psutil.Process().memory_info().rss`; `resource.getrusage`; container memory limits (cgroups) and OOM killer (Stage 0 OS content).
- `gc.get_objects()`, `gc.get_referrers()`, **`objgraph`** (`show_growth`, `show_backrefs`) to find *why* objects survive.
- Strategy: reproduce growth with a loop, snapshot at steady state, diff, trace back-references, fix, re-measure.
- Memory-efficient patterns: generators, chunking, `__slots__`, `array`/NumPy, interning, `weakref` caches, bounded caches (`cachetools.TTLCache`).

```python
import objgraph
objgraph.show_growth(limit=10)       # before
run_workload()
objgraph.show_growth(limit=10)       # after: which types increased?
```

### Advanced — what to learn

- Deep size measurement (`pympler.asizeof`), per-object overheads (object header, dict, int/str caches, small-object allocator pymalloc).
- Fragmentation and arenas: why RSS stays high after freeing; `malloc_trim`, `MALLOC_ARENA_MAX`, using `jemalloc`/`mimalloc`; process recycling
  (`maxtasksperchild`, Gunicorn `max_requests`) as pragmatic mitigation.
- Native memory leaks from C extensions, NumPy/pandas views keeping big buffers alive (a small slice holds the whole array).
- Copy-on-write and `fork`: Python refcounts dirty pages, so forked workers lose sharing (3.12+ immortal objects and `gc.freeze()` help).
- Memory-bound pipelines: backpressure, bounded queues, streaming parsers, memory budgets and early failure.
- Production monitoring: RSS and GC metrics, alerts on growth slope; heap dumps (`memray` live, `tracemalloc` on demand endpoints with safeguards).
- Case studies: debug a leak in the sample app caused by (a) a global dict, (b) `lru_cache` on a method, (c) a lingering traceback; write the fix and a regression test (assert object counts after `gc.collect()`).
- Testing for leaks: loop N times and assert memory growth under a threshold; `weakref` probes.

### Common mistakes

- Using `sys.getsizeof` on containers and believing it is total size.
- Confusing "Python freed it" with "process RSS dropped".
- Fixing symptoms (restart) without root cause.

### Self-check

1. Why does `lru_cache` on an instance method cause a leak, and how do you fix it?
2. How would you tell a Python-level leak from a native-extension leak?
3. Reproduce and fix a leak in the sample app with `tracemalloc` + `objgraph`, adding a regression test.

---

## Lesson 05 — `05-memray-and-allocation-analysis.md`

**Why it matters.** `tracemalloc` only sees Python allocations and slows
code. **Memray** (a production-grade memory profiler) traces Python *and*
native allocations with flame graphs, live view and leak reports — the
go-to tool when "what is using 8 GB?" is the question.

### Basic — what to learn

- Install and run: `memray run -o out.bin script.py`; reports: `memray flamegraph out.bin`, `memray table`,
  `memray summary`, `memray stats`.
- Reading the flame graph: width = bytes allocated at peak (or total allocated); drill into functions.
- Peak memory vs total allocations vs leaked memory — three different questions.

```bash
uv run memray run -o etl.bin etl.py data/big.csv
uv run memray flamegraph etl.bin       # open etl-flamegraph.html
uv run memray stats etl.bin
```

### Intermediate — what to learn

- `--native` for C/C++ frames (NumPy/pandas internals), `--follow-fork` for multiprocessing,
  `--trace-python-allocators` for pymalloc visibility.
- Modes: `memray run --live` (TUI), `memray attach <pid>` to a running process, `pytest --memray`
  (`pytest-memray`) with `@pytest.mark.limit_memory("50 MB")` markers for regression tests.
- Leak report: `--leaks` option shows allocations never freed at the end/at the peak.
- Typical wins: avoid materialising `read()` of huge files; use iterators; reduce dtype sizes; drop intermediate DataFrames;
  stop copying (`.copy()`, slices that allocate); string interning/categoricals (Stage 2).
- Compare pandas/Polars/Arrow memory behaviour on the same job (links to Stage 2 module 04).
- Reporting: peak MB before/after, allocations count, top allocators.

```python
import pytest
@pytest.mark.limit_memory("80 MB")
def test_streaming_job_stays_bounded():
    process_file("fixtures/large.csv")
```

### Advanced — what to learn

- Allocation patterns: many small short-lived objects (churn) vs few huge buffers; allocation rate and its effect on GC and cache misses.
- Understanding native allocator interplay: pymalloc arenas, `malloc`, mmap-backed large allocations; why `memray` and RSS differ.
- Temporal analysis: memory over time, high-water mark spikes during stages (read → transform → join); restructure pipeline to lower peak.
- GPU/array frameworks: PyTorch/NumPy allocator behaviour, pinned memory, caching allocators (awareness; ML stage for GPU memory).
- Memory budgets in containers: set limits, measure headroom, choose `maxtasksperchild`, tune worker counts so `workers × peak < limit`.
- Reproducible memory benchmarks in CI; thresholds per test; trend dashboards.
- Using `memray` with free-threaded builds and async code; limitations.
- Writing an investigation report: peak reduced from X to Y with specific changes; trade-offs (CPU vs memory, readability).
- Compare tools decision table: `tracemalloc` (built-in, Python-only), `memray` (full, low overhead), `scalene` (line-level + CPU), `pympler`/`objgraph` (object-level), `fil` (peak-focused).

### Common mistakes

- Profiling the wrong dataset size (memory scales with data).
- Optimising total allocations when peak memory is the problem.
- Ignoring worker multiplication in multi-process jobs.

### Self-check

1. Difference between peak memory, total allocated and leaked memory?
2. Use `memray` to reduce the peak memory of a CSV-to-Parquet script by at least 50 % and document how.
3. Write a `pytest-memray` test that enforces a memory ceiling on a streaming function.

---

## Lesson 06 — `06-garbage-collector-tuning-and-reference-cycles.md`

**Why it matters.** CPython frees most objects instantly through reference
counting; the cyclic garbage collector handles cycles. GC pauses, memory
growth from uncollectable cycles and copy-on-write breakage in forked
workers are real production concerns. Tuning is rarely needed — but you must
know when and how.

### Basic — what to learn

- Reference counting: `sys.getrefcount`, increments/decrements, immediate destruction at count 0.
- Reference cycles (`a.b = b; b.a = a`) are not freed by refcounting alone; the **cyclic GC** finds them.
- `gc` module: `gc.collect()`, `gc.get_count()`, `gc.get_threshold()`, `gc.disable()/enable()`, `gc.garbage`.

```python
import gc, weakref
class Node: pass
a, b = Node(), Node(); a.other, b.other = b, a
ref = weakref.ref(a); del a, b
print(ref() is not None)       # True — alive due to the cycle
gc.collect()
print(ref() is None)           # True — cyclic GC freed it
```

### Intermediate — what to learn

- Generational GC: three generations (young → old), thresholds `(700, 10, 10)` by default (GC internals have changed across recent releases, including incremental-GC work — read the `gc` docs for your exact version), what triggers a collection.
- Finalisers: `__del__` and cycles (since PEP 442 objects with `__del__` in cycles are collectable); `weakref.finalize`.
- Why avoid `__del__`; context managers for resources (Module 1.9 lesson 03).
- Breaking cycles deliberately: `weakref`, parent pointers as weak refs, explicit `close()`; detecting cycles with `gc.get_referrers`, `gc.set_debug(gc.DEBUG_SAVEALL)` and inspecting `gc.garbage`.
- Exceptions & tracebacks creating cycles (`except Exception as e` stores frames; Python deletes `e` at the end of the block to prevent it).
- Measuring GC cost: `gc.callbacks`, `gc.get_stats()`, timing collections.

### Advanced — what to learn

- **When to tune**: latency spikes from gen-2 collections in large heaps; many long-lived container objects (millions of dicts/lists); batch jobs that allocate many objects but create no cycles.
  Options: `gc.disable()` for short batch scripts (with caution), raise thresholds (`gc.set_threshold`), `gc.freeze()` after startup (Instagram-style: freeze long-lived objects before `fork` to reduce copy-on-write), manual `gc.collect()` at safe points.
- Always measure before/after (latency percentiles, RSS, throughput); document the rationale and revisit on Python upgrades.
- Immortal objects (3.12+) and their effect on refcount writes and copy-on-write; per-interpreter GC; free-threaded builds use a different, deferred reference-counting scheme (Module 1.19).
- Data structures that avoid GC pressure: tuples of atoms are untracked after first GC; `array`, NumPy arrays, `struct`-packed bytes, columnar layouts hold no per-element objects.
- Detecting uncollectable objects in C extensions; debugging with `gc.DEBUG_LEAK`.
- GC and `multiprocessing`/`fork`: refcount writes dirty shared pages; `spawn` vs `fork`; pre-fork `gc.freeze()` recipe.
- GC pauses in async servers & real-time paths; moving heavy collections off the request path.
- Observability: export `gc.get_stats()` and gen-2 collection counts/durations as metrics.

### Common mistakes

- Disabling GC globally "for speed" in a long-running service with cycles → leak.
- Relying on `__del__` for cleanup order.
- Tuning without measurements.

### Self-check

1. Why doesn't reference counting free `a ↔ b` and who does?
2. When would you call `gc.freeze()` and why before `fork`?
3. Reproduce a latency spike due to gen-2 collections with a large object graph and fix it with measured tuning.

---

## Lesson 07 — `07-cpython-performance-idioms.md`

**Why it matters.** After you've profiled and fixed algorithms, pure-Python
micro-optimisations can still give 1.2–3× on hot loops — but many folklore
tips are obsolete in 3.11+. This lesson separates the real from the myth.

### Basic — what to learn

- Rules of thumb that still hold: choose the right data structure; use built-ins (`sum`, `min`, `sorted`, `str.join`, `any`, `map` with C functions);
  avoid repeated work inside loops; prefer comprehensions/generators to manual append loops (usually faster and clearer).
- String building: `"".join(parts)` instead of `+=` in loops (CPython sometimes optimises `+=`, don't rely on it).
- `in` on `set`/`dict` vs `list`; `dict.get`/`setdefault`/`defaultdict`; `collections.deque` for queues.
- Local variable access is faster than global/attribute lookup in tight loops.

```python
# slower: global + attribute lookups in the loop
out = []
for x in data:
    out.append(math.sqrt(x))

# faster & clearer
sqrt = math.sqrt
out = [sqrt(x) for x in data]
```

### Intermediate — what to learn

- The **specialising adaptive interpreter** (3.11+): hot bytecode is specialised for observed types; therefore *type-stable* code is faster;
  avoid changing the types in hot variables, avoid megamorphic call sites.
- Function call overhead (much lower since 3.11 but non-zero): inline tiny helpers in hot loops only when profiling demands.
- Exceptions are cheap on the no-exception path (zero-cost `try`), expensive when raised: EAFP vs LBYL depends on failure rate.
- `functools.lru_cache`/`cache` for pure expensive functions (watch unbounded growth); `__slots__` for memory; `array`/NumPy for numeric arrays.
- Avoid unnecessary copies (slicing big lists, `list(...)`, string slicing in loops); use `itertools`, views, `memoryview`.
- `sorted` with `key=` (keys computed once) vs `cmp_to_key`; `heapq.nsmallest/nlargest` vs sort; `bisect` for sorted lookups.
- Regex compilation, `str` methods vs regex, `str.translate`, `bytes` operations for ASCII-heavy data.
- I/O: buffered reads, larger chunks, `readinto`, binary mode, avoid per-line Python overhead when bulk processing (e.g. `csv` with C parser, `pyarrow`).

### Advanced — what to learn

- **Myth-busting experiments** with `pyperf`: `+=` vs `join`; list comprehension vs `map`; `dict()` vs `{}`; `try/except` vs `if`; f-strings vs `format`;
  attribute access vs local alias; `__slots__` speed; generator vs list for iteration; record results per Python version.
- Reading bytecode (`dis`) to see why something is faster (links to Module 1.19).
- Vectorise instead of looping: NumPy/pandas/Polars expressions, `numexpr`; moving Python loops into native code (Stage 2 module 02).
- Parallelism for CPU-bound work: processes, `concurrent.futures.ProcessPoolExecutor`, shared memory (`multiprocessing.shared_memory`),
  chunk sizing and serialisation overhead; free-threaded Python for CPU-bound threads (benchmark first).
- JIT & PGO: the experimental copy-and-patch JIT (3.13+; `PYTHON_JIT`), PGO/LTO builds, `python-build-standalone`/`uv` builds are optimised; alternative runtimes (PyPy, GraalPy) — when they fit and their compatibility limits.
- Caching at multiple levels: in-process, `functools`, disk (`joblib.Memory`, `diskcache`), external (Redis); cache invalidation and stampede.
- Avoiding premature optimisation: a decision framework — correctness → clarity → algorithm → data layout → vectorisation/native → micro-tuning; document deviations.
- Performance code review checklist; leaving comments with benchmark evidence for non-obvious optimisations.
- Performance budgets and SLOs: latency percentiles and throughput targets as acceptance tests.

### Common mistakes

- Replacing readable code with unmeasured micro-optimisations.
- Optimising code that is not on the hot path.
- Assuming old Python-version folklore applies to 3.12+.

### Self-check

1. Which three classic tips are still valid and which two are outdated on 3.12+? Prove with benchmarks.
2. Why can type-unstable code be slower on the specialising interpreter?
3. Take a slow pure-Python function from the sample app and move it through the decision framework, documenting each step's gain.

---

## Lesson 08 — `08-ctypes-and-cffi-for-native-code.md`

**Why it matters.** Sometimes the fastest or only way is existing native
code: a C library for compression, a system API, a vendor SDK, a hand-tuned
kernel. `ctypes` (stdlib) and `cffi` let Python call it without writing a
full extension module.

### Basic — what to learn

- Loading libraries: `ctypes.CDLL("libc.so.6")`, `ctypes.util.find_library`, platform differences (`.so`, `.dylib`, `.dll`).
- Calling functions: set `argtypes` and `restype` **always**; pass `c_int`, `c_double`, `c_char_p`, `POINTER(...)`.
- Strings and bytes: `c_char_p` expects `bytes`; lifetimes of buffers.

```python
import ctypes, ctypes.util
libc = ctypes.CDLL(ctypes.util.find_library("c"))
libc.strlen.argtypes = [ctypes.c_char_p]
libc.strlen.restype = ctypes.c_size_t
print(libc.strlen(b"hello"))          # 5
```

### Intermediate — what to learn

- Structures and unions: `class Point(ctypes.Structure): _fields_ = [("x", c_double), ("y", c_double)]`;
  nested structs, arrays (`c_int * 10`), passing by reference (`byref`), out-parameters.
- Callbacks: `CFUNCTYPE` to pass Python callables to C (keep a reference alive!); thread/GIL considerations.
- Buffers and zero-copy: `from_buffer`, `memoryview`, NumPy `ctypeslib`; allocating output buffers (`create_string_buffer`).
- Error handling: `errno` (`use_errno=True`), `ctypes.get_errno()`, return-code conventions; NULL pointers.
- **cffi**: ABI mode (`ffi.dlopen`) vs API mode (compile with a C compiler for speed/safety); `ffi.cdef("""...""")`, `ffi.new`, `ffi.buffer`.
- Packaging a small C helper compiled at build time vs loading a system library at runtime.

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("double sqrt(double x);")
libm = ffi.dlopen("m")
print(libm.sqrt(2.0))
```

### Advanced — what to learn

- Safety: wrong `argtypes` → crashes/undefined behaviour; no bounds checking; use-after-free; string encoding and NUL termination;
  validate every pointer/length from untrusted input; fuzz native wrappers (Module 1.16 lesson 09).
- Performance: call overhead (~100s of ns), batch calls, pass arrays not scalars; releasing the GIL (ctypes releases it for calls; cffi API mode can too) — enabling parallel threads.
- ABI stability & portability: struct layout/alignment (`_pack_`), calling conventions, `size_t`/`long` differences between Windows and Unix, endianness.
- Wheels with bundled native libs: `auditwheel`/`delocate`, `manylinux`, rpath; licensing (LGPL) considerations (links to Module 1.18).
- Comparing options: `ctypes` (stdlib, simple), `cffi` (nicer, faster), Cython (typed Python→C), `pybind11`/`nanobind` (C++), `PyO3` (Rust), SWIG, `Python C API` (lesson 09).
- Observability & debugging: `faulthandler`, `gdb` with Python helpers, core dumps, `valgrind`/ASan builds.
- Real exercise: wrap a small C function (e.g. a CRC or text-scan routine), write both `ctypes` and `cffi` wrappers, benchmark against pure Python and NumPy, add tests for edge cases (empty input, large input, invalid pointers).
- Security review checklist for FFI: untrusted library paths, `LD_LIBRARY_PATH`, DLL hijacking.

### Common mistakes

- Omitting `argtypes`/`restype` (defaults to `int`, truncating pointers on 64-bit).
- Letting a callback or buffer be garbage collected while C still uses it.
- Calling native functions per element in a hot loop.

### Self-check

1. Why is omitting `restype` dangerous on 64-bit platforms?
2. How do you keep a `CFUNCTYPE` callback alive?
3. Wrap a C function that fills a buffer and verify there is no buffer overflow with tests.

---

## Lesson 09 — `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`

**Why it matters.** The fastest Python libraries (NumPy, pandas internals,
Polars, `pydantic-core`, `orjson`, `cryptography`, `tokenizers`, `ruff`/`uv`
tooling) are native code with Python bindings. As an AI/data engineer you
rarely write them first — but you must know when it is justified, how they
fit, and how they affect packaging, debugging and security.

### Basic — what to learn

- Why native extensions: raw loops, SIMD, releasing the GIL, memory control, reusing existing C/C++/Rust libraries.
- The landscape: **C API** (hand-written), **Cython**, **pybind11 / nanobind** (C++), **PyO3 + maturin** (Rust), `cffi`, Numba (JIT, Stage 2), Mojo (awareness).
- When *not*: before profiling, algorithmic fixes, vectorisation with existing libraries; maintenance burden and wheel distribution cost.

### Intermediate — what to learn

- Minimal PyO3 module (read, then run a template):

```rust
use pyo3::prelude::*;

#[pyfunction]
fn sum_squares(xs: Vec<f64>) -> f64 {
    xs.iter().map(|x| x * x).sum()
}

#[pymodule]
fn fastmath(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_squares, m)?)
}
```
  Build: `maturin develop --release`; call from Python; benchmark vs pure Python and NumPy.
- Minimal pybind11 module (C++) and `scikit-build-core`/CMake build; Cython `.pyx` with typed memoryviews.
- Data exchange cost: copying lists vs sharing buffers (`numpy` arrays via buffer protocol/`PyBuffer`, Arrow C Data Interface); avoiding Python-object conversion in hot paths.
- GIL: how extensions release it (`Python::allow_threads`, `py::gil_scoped_release`) for parallel threads.
- Exceptions across the boundary (Rust `Result` → Python exceptions); panics and aborts.
- Reading the build config in `pyproject.toml` (`build-backend = "maturin"`).

### Advanced — what to learn

- Distribution: building wheels for many platforms (`cibuildwheel`, `maturin` GitHub Action, `manylinux`, `musllinux`, macOS universal2, Windows), `abi3` stable-ABI wheels, free-threaded wheels (`cp313t`), PyPI size limits (links to Module 1.18 lessons 02, 05).
- Memory safety and security: Rust's guarantees vs C/C++; unsafe blocks; supply-chain risks of native dependencies; reproducible builds; SBOMs (Module 1.18 lesson 10).
- Debugging native crashes: `faulthandler`, `gdb`/`lldb`, `py-spy --native`, `perf`; address/undefined sanitizers.
- Performance realism: call-boundary overhead, GIL contention, async + native threads, benchmarking with `pyperf`; speed-ups usually come from algorithmic and data-layout control, not "Rust is fast" alone.
- Evolution: Python C API changes (3.12 per-interpreter state, 3.13 free-threading support requirements, immortal objects), `Py_GIL_DISABLED`, extension-module thread-safety obligations.
- Case studies: how `Polars` (Rust + Arrow), `pydantic-core`, `tokenizers`, `orjson`, `ruff`/`uv` deliver speed-ups; what API shapes they expose to Python.
- Decision record: write an ADR "Native extension vs vectorisation vs Numba vs service" for a concrete hot spot — options, benchmarks, maintenance cost, packaging impact, team skills.
- Hybrid architectures: keep Python orchestration, push hot kernels to native, or move heavy steps to a separate service/worker in another language.

### Common mistakes

- Writing an extension to avoid learning to profile or vectorise.
- Converting large Python containers on every call.
- Underestimating cross-platform wheel and CI cost.

### Self-check

1. List three signals that a native extension is justified, and three that it is not.
2. Why does passing a Python list to a Rust function often erase the speed-up, and what is the alternative?
3. Write an ADR choosing between NumPy vectorisation, Numba, PyO3 and "do nothing" for a given hot loop, using benchmark evidence.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Read `pstats` output and name the bottleneck; read a flame graph; design a fair microbenchmark; interpret `py-spy dump` |
| B | Interpret `tracemalloc` diffs; pick the right memory tool; predict GC behaviour for cycles; decide whether to tune GC |
| C | Evaluate performance claims; choose between `ctypes`/`cffi`/extension; fix a wrong `argtypes` crash |

Include 6 **"what is wrong with this benchmark?"** items and 6 **"what would you measure first?"** incident scenarios.

---

## 5. Module mini-project

**Performance investigation of `slowlog`**, a deliberately inefficient log/CSV analytics script (provided by you or generated):

1. Generate realistic data (1–5 GB or scaled to your machine) and write a baseline benchmark script.
2. Profile with `cProfile` + `snakeviz`; sample with `py-spy`; capture memory with `memray`.
3. Find and fix at least: one algorithmic hot spot, one memory leak/unbounded cache, one avoidable copy, one I/O inefficiency.
4. Add a `pytest-benchmark` regression test and a `pytest-memray` memory ceiling.
5. Try `multiprocessing` or vectorisation for the CPU-bound stage and measure (include the serialisation cost).
6. Optional: replace one kernel with a `ctypes`/`cffi` or PyO3 implementation and decide with data whether to keep it.
7. Write `PERF_REPORT.md`: baseline, method, findings, changes, before/after numbers (time, peak memory), risks, and what you chose **not** to optimise and why.

Acceptance: ≥ 3× speed-up **or** ≥ 50 % memory reduction on the final scenario with correctness tests unchanged; reproducible benchmark commands; all claims backed by saved profiles/benchmarks.

---

## 6. Completion checklist

- [ ] I can profile with `cProfile`, read `pstats`, and produce a flame graph.
- [ ] I can attach `py-spy` to a live process and diagnose slow or hung jobs.
- [ ] I can write fair microbenchmarks and avoid their pitfalls.
- [ ] I can find memory growth with `tracemalloc`, `objgraph` and `memray`.
- [ ] I can explain reference counting, cycles, generations and decide when to tune GC.
- [ ] I know which CPython micro-optimisations are real and can prove it with benchmarks.
- [ ] I can call native code via `ctypes`/`cffi` safely.
- [ ] I can reason about native extensions (PyO3, pybind11, Cython) and their packaging costs.
- [ ] I can write a clear, evidence-based performance report.
- [ ] I completed the `slowlog` mini-project.

**Next:** Module 1.18 — Packaging, Distribution and Publishing.
