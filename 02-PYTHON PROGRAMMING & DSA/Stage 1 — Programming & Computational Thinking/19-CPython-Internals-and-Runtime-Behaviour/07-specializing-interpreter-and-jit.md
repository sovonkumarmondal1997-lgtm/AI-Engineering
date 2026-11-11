# Specializing Interpreter and JIT

> **Scope:** CPython 3.12–3.14, with explicit notes where behaviour differs by version or build. This lesson describes CPython internals, not guarantees of the Python language. Bytecode names, specialization choices, counters, JIT flags, and performance are implementation details and can change between patch releases and builds.

## Learning outcomes

By the end of this lesson, you should be able to:

1. Explain why CPython specializes frequently executed bytecode instead of treating every operation generically forever.
2. Describe adaptive instructions, warm-up, inline caches, guards, specialization, and de-specialization.
3. Inspect warmed-up code with `dis.dis(..., adaptive=True, show_caches=True)` when supported.
4. Recognize how stable types and object layouts can help a hot call site—and why dynamic Python code must remain correct when assumptions change.
5. Distinguish the specializing interpreter from a just-in-time (JIT) compiler and identify when the experimental CPython JIT is available and enabled.
6. Design fair benchmarks across Python versions and JIT configurations, interpret noisy results, and avoid overgeneralizing from microbenchmarks.
7. Make evidence-based performance decisions while prioritizing algorithms, data layout, vectorization, and native implementations where they matter more.

## Prerequisites

You should know basic Python functions, classes, attributes, loops, and numeric operations. Be comfortable running a script from a terminal and understand that CPython compiles source to bytecode, then executes that bytecode in an evaluation loop. Earlier lessons in this module cover `dis`, frames, and the evaluation loop; Module 1.17 covers profiling and benchmarking.

Useful concepts:

- **Bytecode:** instructions executed by CPython's virtual machine.
- **Hot code:** code executed often enough that optimization may repay its cost.
- **Type stability:** an operation repeatedly receives values of compatible runtime types.
- **Guard:** a quick runtime check that a speculative optimization's assumptions still hold.
- **De-specialization:** abandoning or backing off from an optimization when assumptions repeatedly fail.
- **JIT:** just-in-time compilation, translating selected runtime code into native machine code while the program runs.

## Mental model

Think of modern CPython as a layered execution system:

```text
Python source
    ↓ compile
ordinary bytecode
    ↓ execute and observe hot operations
adaptive/specialized bytecode + inline caches      (CPython 3.11+)
    ↓ on JIT-capable builds, sufficiently hot paths may enter Tier 2
Tier 2 intermediate representation / micro-ops
    ↓ if the experimental JIT is built and enabled
native machine-code templates stitched at runtime
```

The middle step is important: **specialization is not itself a JIT**. CPython's specializing interpreter can replace generic bytecode operations with faster specialized interpreter instructions without generating machine code. A JIT is an additional, optional layer. Most CPython installations do not necessarily have an enabled JIT, and free-threaded builds do not support the CPython JIT in the 3.14 release described here.

The objective is not to make Python statically typed. CPython observes what actually happens, makes local assumptions, checks those assumptions, and falls back when they no longer hold. Python's language-level behaviour must remain correct.

---

## 1. Why the specializing interpreter exists

### What it is and why it matters

A generic bytecode instruction often has to support many possible runtime cases. For example, `a + b` may add integers, concatenate strings, invoke user-defined `__add__`, or raise an exception for unsupported operands. Supporting all those cases requires dispatch and checks.

In a hot loop where `a` and `b` are repeatedly exact integers, much of that generality is unnecessary for that particular execution. CPython can specialize the operation for the observed case and retain checks that make the optimization safe.

The **Faster CPython** project delivered major improvements in Python 3.11 and continued improving the runtime in later releases. A commonly quoted headline is roughly a 25% average speed-up from 3.10 to 3.11 on the benchmark suite used at the time. That is a historical aggregate, not a promise that every application—or every later version—will be 25% faster. Workload, dependencies, build options, hardware, and benchmark suite all matter.

### How it works at a high level

1. The compiler emits ordinary bytecode for the program's semantics.
2. At runtime, selected instructions are quickened into adaptive forms.
3. Adaptive instructions collect enough observations to decide whether a specialized form is likely to help.
4. A specialized instruction uses a fast path plus guards for assumptions such as operand types, dictionary keys, or function identity/version.
5. If a guard fails, CPython executes a correct fallback path. Repeated misses can cause the instruction to back off or de-specialize.

The exact thresholds, counter encodings, and opcode names are internal details. Do not write application logic that depends on a specific instruction name appearing after exactly N calls.

### Where it helps in real applications

A web service repeatedly reading fields from objects, calling the same function, or performing arithmetic on integers may benefit from optimized attribute loads, calls, global lookups, and binary operations. A function that runs only once may not become hot enough for specialization to matter. Time spent waiting on a database or network may dominate any interpreter-level savings.

### Limitations and trade-offs

Specialization has runtime and memory costs. Dynamic code that frequently changes types, class layouts, globals, or call targets can reduce the benefit. Instrumentation such as tracing and profiling can change execution behaviour and may inhibit or distort optimizations. Specialization does not remove algorithmic complexity or make Python-level numeric loops equivalent to vectorized native code.

---

## 2. Adaptive instructions, warm-up, caches, guards, and de-specialization

### 2.1 Warm-up and counters

An instruction is not necessarily specialized the first time it runs. CPython needs evidence that a path is hot and that a specialization is likely to pay off. Adaptive instructions use internal counters to schedule specialization attempts; specialized instructions also track whether their assumptions keep holding.

A benchmark's first few iterations can therefore measure a different execution state from later iterations. Warm-up is not just CPU cache warming: it can include interpreter specialization and, when available, JIT compilation. It can also include unrelated effects such as imports, allocator activity, and operating-system scheduling.

### 2.2 Inline caches

An **inline cache** stores small pieces of information close to an instruction so that the fast path can avoid repeating expensive lookups. Depending on the instruction family and version, cached information may relate to dictionary key layouts, type versions, or call targets. `dis` can display cache entries with `show_caches=True`.

Cache contents are not a public application interface. Their layout and meaning may change across CPython releases. Read them to understand an experiment, not to build production logic.

### 2.3 Guards

A specialization is a hypothesis, not a permanent truth. A specialized attribute lookup might assume a particular object/type layout or dictionary version. A call specialization may depend on a stable call shape or target. A guard checks relevant assumptions before using the fast path.

If an assumption is false, the interpreter must preserve normal Python semantics: it takes a fallback path, retries generic behaviour, or eventually changes the specialization. Guard failure is not automatically a bug; it is a normal consequence of dynamic behaviour.

### 2.4 De-specialization

Consider a function that adds integers most of the time but occasionally receives a string. The integer fast path cannot blindly treat the string as an integer. It must detect the mismatch and fall back to the appropriate semantics. Repeated mismatches can cause the site to become less specialized or use a different specialization.

A few mismatches do not prove that an opcode will visibly revert in a specific way. CPython uses adaptive counters and specialization policies that are implementation details. Inspect the actual build and describe what you observed, not what you expected to see.

---

## 3. Experiment 1 — inspect specialization with `dis`

**Question:** What changes in a function's adaptive disassembly after it repeatedly receives integer arguments, and what happens when its input types change?

**Setup:** Run with CPython 3.12, 3.13, or 3.14. The `adaptive` and `show_caches` options are available in these versions. The exact opcode names and displayed cache contents can vary.

Save as `inspect_specialization.py`:

```python
import dis
import sys


def add(a, b):
    return a + b


def inspect(label):
    print(f"\n--- {label} ---")
    print("Python:", sys.version.split()[0])
    # adaptive=True shows the runtime-adapted instruction stream.
    # show_caches=True displays implementation-specific inline-cache entries.
    dis.dis(add, adaptive=True, show_caches=True)


# First inspect the function before deliberately warming it up.
inspect("before warm-up")

for _ in range(2_000):
    add(10, 20)

inspect("after integer warm-up")

# Exercise a different valid operand combination. This must preserve Python
# semantics even if it misses a specialized integer fast path.
for _ in range(2_000):
    add("runtime ", "specialization")

inspect("after string calls")

# Confirm the actual result rather than inferring correctness from bytecode.
print("integer result:", add(10, 20))
print("string result:", add("runtime ", "specialization"))
```

Run it:

```bash
python inspect_specialization.py
```

### Procedure

1. Record the Python version and build you used (`python -VV` is also useful).
2. Compare the initial disassembly with the integer-warmed disassembly.
3. Look for a specialized arithmetic instruction such as `BINARY_OP_ADD_INT`, if the runtime chooses it. Cache entries may also be displayed.
4. Compare again after the string calls. Note whether the displayed instruction changes, remains specialized, or shows adaptive/generic behaviour.
5. Run the script on another CPython version and compare cautiously.

### Expected observations

On a typical GIL-enabled CPython 3.12–3.14 build, repeated integer addition is a plausible specialization candidate. You may see `BINARY_OP_ADD_INT` after warm-up. The exact output is **representative, not guaranteed**: opcode names, cache formatting, warm-up thresholds, and specialization policies can change. String addition is valid Python, and the final results should be `30` and `runtime specialization`.

### Interpretation

The runtime can optimize a hot operation for the cases it observes while retaining correct behaviour for other types. The disassembly is evidence of the current runtime's adaptive state, not proof that the function is faster in an end-to-end workload.

### What this does not prove

- It does not establish a stable bytecode API or a fixed warm-up threshold.
- It does not prove a measurable speed-up; timing is a separate experiment.
- It does not prove every changed-type call causes immediate de-specialization.
- It does not generalize to every Python implementation or CPython build.

### Troubleshooting

- If the `dis.dis` call rejects an option, check the active interpreter and its version; do not assume the shell's `python` is the version you installed.
- If a named specialization does not appear, record that fact. The code may not have specialized on that build, or the observation may be affected by instrumentation or different runtime policy.
- Do not assert exact opcode names in normal application tests. They are suitable for version-pinned experiments, not portable correctness tests.

---

## 4. Type stability, object shape, and maintainable code

### What helps

A hot call site is easier to optimize when it repeatedly sees compatible types and layouts. For example, a loop that consistently adds integers is a better candidate for integer-add specialization than a loop that mixes integers, strings, decimals, and custom numeric objects.

Object **shape** here means the relevant runtime layout and attribute organization, not the visual shape of a value. Repeated access to an instance attribute can be optimized when CPython can rely on stable type and attribute-layout metadata. Creating instances consistently—for example, assigning the same attributes in `__init__`—can help dictionary key-sharing and layout regularity. This is not a promise that a particular source style will always yield a particular opcode.

Readable local variables and built-ins can also reduce avoidable dynamic work in some cases. But the fastest source form depends on the operation and CPython version; verify with a profiler and benchmark.

### What can reduce the benefit

- **Polymorphic call sites:** the same instruction sees several unrelated types or targets.
- **Megamorphic call sites:** a site sees many distinct shapes or targets and no single fast path dominates.
- **Frequent runtime mutation:** classes, descriptors, global namespaces, or object layouts change in ways that invalidate assumptions.
- **Tracing/profiling:** instrumentation adds overhead and can alter optimization behaviour.
- **Dynamic execution:** `exec`-heavy or highly dynamic code may offer fewer stable assumptions, though the effect is workload-specific.

Do not interpret these as rules to ban polymorphism or dynamic Python. Those features often provide good design value. Specialization is one optimization input, not the architecture's primary requirement.

### Real-world example

A data-ingestion service may represent every validated event with the same `Event` class and consistently initialize `event_id`, `timestamp`, and `kind`. A hot normalization function repeatedly reads those fields. Stable layouts may help attribute access. If events instead come from many unrelated classes, descriptors, proxies, and dynamic attributes, the same lookup site may be harder to optimize. The correct design decision still depends on maintainability, correctness, and measured throughput.

### Other CPython improvements are not all specialization

Python 3.11+ also brought other performance changes, and later releases added more. Examples include cheaper Python function calls/frames, exception-handling changes, and—in Python 3.12—PEP 709's inlining of list, set, and dict comprehensions. Superinstructions can combine common instruction sequences. These improvements have different mechanisms; do not attribute every speed-up to specialization or the JIT.

### Common mistake

Do not contort a public API, introduce needless casts, or avoid useful abstractions solely to chase a speculative specialization. Keep code semantically clear. Profile a real workload, find a hot path, and test a small change against a stable baseline.

---

## 5. Interpreter specialization versus a JIT

| Property | Specializing adaptive interpreter | JIT compiler |
|---|---|---|
| Main action | Replaces generic bytecode operations with specialized interpreter instructions and caches | Compiles selected hot code/IR into native machine code |
| Native code required? | No | Yes |
| Can optimize hot paths? | Yes, mainly at instruction-level granularity | Potentially across larger regions with additional optimization opportunities |
| Warm-up cost | Usually relatively small, but not zero | Can include tracing/IR optimization and machine-code generation costs |
| Availability in CPython | Standard CPython since 3.11, subject to implementation details | Experimental optional build/runtime feature in CPython 3.13+; availability differs by build/version/platform |
| Production assumption | A normal part of contemporary CPython execution, but exact internals are not stable APIs | Do not assume it exists or is production-ready; explicitly check and test the build |

### Why a JIT is harder

Python supports dynamic types, reflection, descriptors, custom operators, exceptions, generators, and extension modules. Native compilation must preserve observable Python semantics while managing assumptions and de-optimization. The implementation also needs to coexist with debuggers, profilers, the C API, and platform-specific machine-code details.

### CPython's experimental JIT in 3.13 and 3.14

The experimental JIT was added to CPython in 3.13 behind a build-time option. The 3.14 release notes describe official macOS and Windows binaries that include an experimental JIT; it is still not recommended as a production default. Availability in a particular Linux distribution or custom build is not guaranteed. Always inspect the executable actually running your workload.

The architecture is broadly:

1. Tier 1 specialized bytecode gathers useful runtime information.
2. Hot code may be translated into Tier 2 intermediate representation, often described as micro-ops or uops.
3. Optimization passes operate on that representation.
4. With the JIT enabled, optimized IR can be translated to machine code using a copy-and-patch approach: build-time-generated, architecture-specific machine-code stencils are patched with runtime information and stitched into executable code. LLVM is used to generate these stencils in the documented CPython 3.13–3.14 build process; it is a build-time dependency, not a runtime dependency of the resulting executable. A Tier 2 interpreter configuration is also available in relevant builds without enabling native JIT compilation.

Do not infer that a build has a working native JIT merely because it has Tier 2-related code or a runtime variable named `PYTHON_JIT`. The build must support the feature, and the runtime configuration must enable it.

The 3.14 release notes report that JIT performance can range from slower to faster depending on workload (the documented typical impact spans approximately 10% slower to 20% faster in the release notes). Treat that as release-time guidance, not a guarantee for every patch release or workload. Free-threaded builds do not support the CPython JIT in 3.14.

### Other compilation approaches: not the same thing

- **PyPy:** a different Python implementation with its own tracing JIT and compatibility/performance trade-offs.
- **Numba:** compiles supported numerical code paths using type-specialized techniques; it is not a general compiler for every Python feature.
- **Cython:** can compile annotated or compatible Python-like code ahead of time into extension modules.
- **Native extensions / vectorized libraries:** move work into native code, often with less per-element Python overhead.

These tools solve overlapping but different problems. Benchmark on the actual supported workload and dependency stack. Other emerging or specialized approaches—including `mypyc`, Codon, Mojo, Cinder, and Pyston—make different trade-offs in typing, compilation, runtime compatibility, and deployment. Treat them as options to investigate for a concrete bottleneck, not as interchangeable drop-in JIT switches. Subinterpreters and free-threaded CPython address concurrency/isolation concerns and are not synonyms for a JIT; in CPython 3.14 the experimental JIT is not supported by free-threaded builds.

---

## 6. Inspect whether the experimental JIT is available and enabled

The public documentation describes `sys._jit` as an **experimental CPython implementation detail**, added in Python 3.14. It is not guaranteed to exist in older versions, other implementations, or builds without JIT support.

```python
import os
import platform
import sys

print("implementation:", platform.python_implementation())
print("version:", sys.version.split()[0])
print("PYTHON_JIT:", os.environ.get("PYTHON_JIT", "<unset>"))

jit = getattr(sys, "_jit", None)
if jit is None:
    print("sys._jit API unavailable in this interpreter")
else:
    print("JIT available:", jit.is_available())
    print("JIT enabled:", jit.is_enabled())
```

### How to interpret it

- `is_available()` indicates that this executable supports JIT compilation.
- `is_enabled()` indicates that JIT compilation is enabled for the current process; it implies availability.
- If `sys._jit` is absent, the interpreter may be older than 3.14, may be built without the feature, or may be another implementation. Absence alone does not identify which cause applies.
- CPython 3.14 also documents `sys._jit.is_active()`, which reports whether the topmost Python frame is currently executing JIT code. It is intended for JIT testing/debugging, not application decisions: tracing JIT behaviour can make repeated checks surprising, especially if code branches on the result.
- `PYTHON_JIT` is a runtime setting only meaningful when the build supports the relevant JIT pipeline. It cannot add JIT support to a binary that was built without it.

The API is deliberately underscored and experimental. Use feature detection rather than importing it unconditionally. Avoid using `sys._jit` to drive business logic.

### Build and runtime flags

On supported source builds, CPython 3.13+ uses a configure option in the family of:

```bash
./configure --enable-experimental-jit
```

The documented configure values include `no`, `yes`, `yes-off`, and `interpreter`. `yes` enables the JIT and can be disabled at runtime with `PYTHON_JIT=0`; `yes-off` builds it but disables it by default, allowing runtime opt-in with `PYTHON_JIT=1`. `interpreter` enables the Tier 2 interpreter configuration without the JIT. Exact support depends on the release and platform; Windows has corresponding build-script options. Read the `Tools/jit/README.md` and the release notes for the source version being built.

### Other build-level performance factors: PGO, LTO, and the tail-calling interpreter

A JIT is not the only build option that can change performance. **Profile-guided optimization (PGO)** uses representative training runs to guide native compiler optimization, and **link-time optimization (LTO)** lets the compiler/linker optimize across translation-unit boundaries. Their availability and benefit depend on the toolchain, build recipe, and workload. Distribution builds can differ materially from a local debug build even when both report the same Python version. For example, `uv`'s managed CPython distributions are sourced from Astral's `python-build-standalone` project, whose published variants include build profiles such as `pgo+lto`, `pgo`, `lto`, and `noopt`; the exact profile varies by release and platform. Record build provenance before attributing a result to a runtime feature.

CPython 3.14 also has an opt-in **tail-calling interpreter**, enabled in source builds with `--with-tail-call-interp`. It requires a compiler with suitable tail-call support; the documented supported configuration is Clang 19 or newer on x86-64 and AArch64, and enabling PGO (`--enable-optimizations`) is highly recommended. Preliminary release benchmarks reported a 3–5% geometric-mean improvement on `pyperformance` for the tested configurations; that is not a per-workload promise. This changes interpreter dispatch, not Python-function tail-call semantics, and it is not the JIT. Check the exact 3.14 build documentation and build options rather than assuming a binary uses it.

For a controlled run, set the environment only for that process:

```bash
# POSIX shell: opt in only if this build supports the JIT.
PYTHON_JIT=1 python benchmark.py

# Compare with JIT disabled on the same JIT-capable binary.
PYTHON_JIT=0 python benchmark.py
```

On PowerShell, use `$env:PYTHON_JIT = "1"` before launching the process, and restore/unset it after the run. These commands do not install a JIT or change the build. A standard binary without JIT support may ignore or be unable to use the setting.

### Perf and native observability

On supported platforms, CPython 3.12+ can expose Python calls to Linux `perf` with `-X perf` or `PYTHONPERFSUPPORT=1`; support still depends on the interpreter build and platform. CPython 3.13 adds the separate `-X perf_jit` / `PYTHON_PERF_JIT_SUPPORT` mode for reporting Python calls using DWARF information. These options concern Python-frame profiling support and do **not** guarantee that native tools can unwind through frames generated by CPython's experimental JIT. In the 3.14 JIT implementation, the release notes explicitly identify native debugger/profiler unwinding through JIT frames as a limitation. Check the exact version's `using/cmdline` and `howto/perf_profiling` documentation before relying on these options. `py-spy --native` can help include native frames when its platform and permissions permit, but it does not guarantee complete JIT-frame visibility.

---

## 7. Benchmarking: measure the workload, not a story

### A reliable method

1. **Define the question.** Are you measuring steady-state function throughput, startup latency, end-to-end request latency, memory, or CPU consumption? These are different outcomes.
2. **Control the environment.** Record CPU, OS, power mode, Python build, compiler/build flags, dependencies, and relevant environment variables. Avoid competing workloads. Pinning cores can help in controlled Linux experiments, but it is not always representative of production scheduling.
3. **Separate startup from steady state.** Import time, JIT compilation, caches, and warm-up may matter to short-lived commands but not long-running workers. Measure both when both matter.
4. **Repeat.** Use multiple processes and repeated runs. Report medians and dispersion or confidence intervals, not a single lucky number. Investigate outliers instead of silently discarding them.
5. **Use an appropriate tool.** `pyperf` is preferable for careful Python microbenchmarks and supports repeated worker processes and calibration. `pyperformance` is useful for a suite of representative benchmarks. For production, instrument representative request/job workloads and compare throughput, latency percentiles, CPU, memory, and error rates.
6. **Change one factor at a time.** Do not compare a debug build with PGO/LTO release build and attribute all differences to the JIT.
7. **Validate correctness.** Compare outputs and error behaviour before comparing timing.
8. **Use the result's scope honestly.** One microbenchmark says something about that operation, interpreter, build, and machine—not every Python program.

### Why `timeit` can mislead

`timeit` is useful for quick experiments, but a tiny loop may exaggerate or hide the effect of specialization. Repeating a function inside one process can measure warm steady-state performance, while invoking a script repeatedly can include startup and compilation effects. Neither is automatically wrong; choose the measurement that matches the production question.

### Prefer `pyperf` for repeatable comparisons

Install `pyperf` in each environment, then use its documented runner and comparison commands. A minimal benchmark function can be placed in a script:

```python
# bench_add.py

def work(n=200_000):
    total = 0
    for i in range(n):
        total += i
    return total


def bench():
    return work()

if __name__ == "__main__":
    print(bench())  # optional correctness check; pyperf will run the benchmark too
```

For a pyperf-managed benchmark, use the documented `pyperf.Runner` pattern instead of timing `bench()` manually:

```python
# bench_pyperf.py
import pyperf


def work(n=200_000):
    total = 0
    for i in range(n):
        total += i
    return total


runner = pyperf.Runner()
runner.bench_func("integer_sum_loop", work)
```

Run in each Python environment, using the same source and dependency versions:

```bash
python -m pip install pyperf
python bench_pyperf.py --rigorous -o py312.json
python -m pyperf stats py312.json
```

Use a different output filename for each interpreter/build, then compare files with the `pyperf compare_to` command documented by your installed pyperf version. The exact command-line options are tool-version-sensitive; check `python -m pyperf --help` and `python -m pyperf compare_to --help`. Do not overwrite the first result when collecting a second configuration.

The function above is intentionally a simple CPU-bound Python loop. It is a demonstration workload, not a universal benchmark and not a substitute for the project's real workload. For a broader suite, use `pyperformance` with its documented runner and preserve the suite version and selected benchmarks in your report. Do not mix suite results from different versions without explaining that the benchmark set or harness may have changed.

---

## 8. Experiment 2 — compare versions and JIT-on/off configurations

**Question:** Does the interpreter version or experimental JIT change the performance of a CPU-bound pure-Python loop on your machine?

### Setup

- Ideally use separate CPython 3.10, 3.12, and 3.14 installations to show both the historical baseline and newer runtime behaviour.
- If available, use a JIT-capable CPython 3.13/3.14 binary and compare `PYTHON_JIT=0` with `PYTHON_JIT=1` **on the same executable**.
- If a free-threaded build is available, measure it as a separate configuration and label it clearly. CPython 3.14 free-threaded builds do not support the experimental JIT, so do not present that result as a JIT-on/off comparison or attribute every difference to one factor.
- Use identical benchmark source, dependencies, power settings, and machine conditions. When comparing build variants, note that build options such as PGO/LTO and the interpreter implementation may also differ.
- Record whether each executable is a release/debug build, its build flags if known, and JIT availability/enabled status.

### Procedure

1. Run the benchmark's correctness check in every environment.
2. Collect several pyperf runs per version/configuration. Do not compare one run from one build with a large sample from another.
3. Measure a real project workload as a second benchmark. Include startup time if your production process is short-lived.
4. Record the tool's reported central estimate and variation, throughput or elapsed time, memory, CPU model, OS, Python version/build, build profile where known, and JIT state. Report a confidence interval when the measurement method supports one; otherwise report the available dispersion and state the limitation.
5. If a result looks surprising, repeat it and investigate background load, thermal throttling, build differences, dependency differences, and warm-up effects.
6. Write a three-paragraph conclusion: (a) setup and controls, (b) observed data and uncertainty, (c) what you would and would not change based on the evidence.

Use a table like this so that build differences do not disappear inside a single timing number:

| Configuration | CPython build / GIL mode | JIT available / enabled | PGO/LTO or other build notes | CPU / OS | Central estimate and uncertainty | Correctness check |
|---|---|---|---|---|---|---|
| 3.12 baseline | Record exact build | N/A or unavailable | Record if known | Record | Record tool output and dispersion/CI | Pass/fail |
| 3.14 JIT off | Record exact build | Record both | Record if known | Record | Record tool output and dispersion/CI | Pass/fail |
| 3.14 JIT on | Same executable as JIT-off row | Record both | Same build as preceding row | Same machine | Record tool output and dispersion/CI | Pass/fail |
| Free-threaded build (optional) | State that this is a separate build/configuration | JIT unsupported in CPython 3.14 | Record build profile | Record | Record tool output and dispersion/CI | Pass/fail |

Do not fill unknown values with guesses. If the tool does not provide a confidence interval, report the statistic and dispersion it does provide and explicitly say that a confidence interval was not calculated.

### Expected observations

A newer CPython may improve this loop, but the size of the change depends on release, build, CPU, and measurement. Enabling an experimental JIT may make a benchmark faster, slower, or effectively unchanged. Short runs can be dominated by startup or JIT overhead; long runs can show a different steady-state result. No numeric result should be predicted in advance.

### Interpretation

The benchmark establishes how those exact configurations performed on that machine under those conditions. If the JIT helps one arithmetic loop but does not improve the service's end-to-end latency, it may not be worth enabling. Conversely, a repeatable improvement in a dominant workload is a reason to evaluate the configuration more deeply.

### What this does not prove

- It does not prove that one Python version is faster for every workload.
- It does not establish that JIT-on is production-ready.
- It does not prove that a microbenchmark's speed-up will translate proportionally to application latency.
- It does not isolate the JIT effect unless the compared binaries and conditions are otherwise controlled.

---

## 9. Where bigger performance wins often come from

Interpreter optimizations are valuable, but they are only one layer of performance engineering.

### 9.1 Algorithm and complexity

Changing an algorithm from repeated linear searches to indexed lookups can dwarf a modest interpreter speed-up. If the program performs unnecessary work, optimizing each operation may preserve the wrong amount of work.

### 9.2 Data layout

Millions of Python objects carry object headers, references, and allocation overhead. Compact arrays, typed buffers, columnar data, or a better database/query layout can reduce memory traffic and improve cache locality. The right representation depends on access patterns and conversion costs.

### 9.3 Vectorization and native libraries

A Python loop over individual numeric values incurs per-iteration interpreter overhead. NumPy and other native libraries can process whole arrays in compiled loops; some operations also release the GIL. Vectorization is not free—allocation, conversion, temporary arrays, and small input sizes can erase gains—but it is often more consequential than a bytecode specialization.

### 9.4 Native extensions or compilation

A native extension, Cython, Numba, or another suitable tool may accelerate a measured hot path. Trade-offs include packaging, ABI/platform support, debugging, build complexity, type constraints, and maintenance cost. Prefer a clear boundary and evidence that the native implementation is worth the added complexity.

### 9.5 A practical priority order

1. Confirm correctness and measure the real bottleneck.
2. Remove unnecessary work and improve algorithmic complexity.
3. Improve data layout and batching; use vectorized/native operations where appropriate.
4. Optimize the hot Python path with a small, readable change.
5. Evaluate interpreter upgrades and build options under controlled conditions.
6. Consider JIT or other compilation options only after measuring benefits and operational risks.

These are heuristics, not a rigid rule. A Python-version upgrade can be an inexpensive win, but it still needs compatibility testing.

---

## 10. Production rollout and operational safeguards

An experimental JIT changes the runtime configuration and potentially the shape of performance and debugging data. Treat it like any other performance-sensitive rollout.

### Recommended rollout

1. **Inventory the baseline.** Capture Python version/build, flags, dependency versions, hardware, startup time, throughput, p50/p95/p99 latency, CPU, RSS, error rate, and relevant profiler data.
2. **Reproduce offline.** Use a representative workload and repeatable benchmark. Check correctness and exception behaviour.
3. **Use a canary.** Enable the candidate build/configuration for a small portion of traffic or a limited worker pool, with a clear rollback path.
4. **Compare service-level metrics.** Look for changes in tail latency, CPU saturation, memory, startup, timeouts, and error rates—not only average benchmark time.
5. **Keep a fallback.** Preserve a known-good interpreter/build and a documented way to disable the JIT where the target build supports it. A runtime flag cannot replace a binary that does not support the feature.
6. **Check observability.** Verify that tracing, crash reports, profilers, native debuggers, and operational tooling behave acceptably with the selected configuration.
7. **Document the result.** Record tested workload, environment, confidence, known limitations, and rollback procedure.

### Safe operational practices

- Do not set `PYTHON_JIT=1` globally on a fleet and assume every interpreter understands it.
- Avoid comparing different dependency or build configurations and claiming the JIT caused the result.
- Do not gate correctness or business behaviour on `sys._jit` or a particular specialized opcode.
- Keep performance tests separate from correctness tests; timing assertions are usually flaky.
- Re-run measurements after CPython patch upgrades, operating-system changes, or major dependency changes.
- If a canary regresses, roll back first and preserve evidence; do not keep an experimental configuration enabled solely because a microbenchmark improved.

---

## 11. Common misconceptions and failure modes

### “Fewer bytecode instructions always means faster code.”
False. Opcode count ignores instruction cost, cache behaviour, native calls, memory allocation, branch prediction, and the workload's dominant cost. Measure elapsed time and resource usage.

### “Every CPython build has a JIT.”
False. The JIT is experimental and build/platform-dependent. Python 3.14's official macOS and Windows binaries include it, but many other builds may not. Use feature detection and inspect release documentation.

### “Specialization makes Python statically typed.”
False. CPython observes runtime behaviour and uses guarded assumptions. Dynamic semantics remain intact.

### “A JIT makes numerical Python as fast as C.”
Unsupported. A JIT may improve selected hot paths, but object-heavy dynamic operations and numeric loops can still incur substantial overhead. Native vectorized code can do more work per call.

### “A benchmark result from one loop predicts my service.”
False. End-to-end latency includes I/O, serialization, database time, queueing, contention, startup, and other work that a microbenchmark may not represent.

### “If the opcode changed, I proved the speed-up.”
False. Disassembly shows runtime state; timing and representative workloads are needed to establish performance.

### “I should write code for the JIT before profiling.”
False. Maintainable code and good algorithms are primary. Use profiling to identify a hot path, then test changes.

---

## 12. Diagnostic workflow when performance changes

When a new Python release or JIT configuration appears slower or faster than expected, use a disciplined sequence:

1. **Verify the executable:** `python -VV`, `python -c "import sys; print(sys.executable)"`, `python -m pip --version`.
2. **Record the configuration:** platform, CPU, build type, environment variables, `sys.flags`, dependencies, JIT availability/enabled state when `sys._jit` exists.
3. **Separate startup and steady state:** run both a cold-start measurement and a warmed benchmark if both represent production.
4. **Check correctness first:** compare results and errors across configurations.
5. **Inspect bytecode as evidence:** use `dis.dis(func, adaptive=True, show_caches=True)` on supported versions, but do not treat an opcode listing as a performance metric.
6. **Profile the real workload:** determine whether time is in Python frames, native code, allocation, serialization, I/O, or waiting.
7. **Repeat and quantify uncertainty:** use pyperf or production samples; report distribution, not only the best run.
8. **Change one variable:** interpreter version, JIT flag, or code change—not all at once.
9. **Canary and roll back:** compare service-level metrics and preserve a known-good configuration.

---

## 13. Concept map

```text
Hot Python operation
        │
        ▼
Adaptive instruction gathers observations
        │
        ▼
Specialization candidate selected
        │
        ├── guard succeeds ──► fast specialized interpreter path
        │
        └── guard fails ─────► correct fallback / miss accounting
                                      │
                                      ▼
                          possible re-specialization or backoff

For a JIT-capable build, sufficiently hot code may also follow:
Tier 1 specialized bytecode → Tier 2 IR/uops → optimization → native code

Across all paths: Python-visible semantics and correct results must be preserved.
```

---

## 14. Summary

- CPython's specializing adaptive interpreter, introduced in 3.11, optimizes hot bytecode operations using runtime observations, inline caches, and guards.
- Specialization is not JIT compilation: it can speed execution while still interpreting specialized bytecode.
- Guards and fallback paths preserve Python semantics when types or layouts change; repeated misses can lead to de-specialization or a different strategy.
- `dis.dis(..., adaptive=True, show_caches=True)` is useful for experiments on supported versions, but bytecode and cache details are not stable APIs.
- The CPython JIT is an experimental, optional feature in 3.13+ and varies by version, platform, and build. Python 3.14 adds `sys._jit` introspection in builds that support it; feature-detect it.
- Benchmark warm-up, startup, repeated runs, build differences, noise, and real-workload impact separately. Never invent a speed-up before measuring.
- Prefer algorithmic improvements, suitable data structures, vectorization, and native code when those address the actual bottleneck. Keep code readable and roll out experimental runtime options with canaries and fallbacks.

## 15. Self-check questions with answers

### 1. What does “specializing” mean, and what is a guard?

**Answer:** Specializing means replacing or adapting a generic bytecode operation to a faster implementation for runtime cases observed at a hot instruction. A guard is a runtime check that verifies the assumptions required by that fast path. If a guard fails, CPython must take a correct fallback path and may later adjust or abandon the specialization. This is an implementation strategy, not static typing.

### 2. Show instruction specialization with `dis(..., adaptive=True)` and provoke de-specialization by changing argument types.

**Answer:** Use the `add(a, b)` experiment in Section 3. Warm the function with repeated integer inputs, inspect adaptive disassembly, then repeatedly call it with strings and inspect again. A common result is an integer-add specialization such as `BINARY_OP_ADD_INT` after integer warm-up. The later display is version- and workload-dependent: a changed type may trigger a fallback without immediately changing the displayed opcode. Report what your interpreter actually shows and verify both arithmetic and string concatenation results.

### 3. Benchmark one CPU-bound pure-Python workload across two Python versions and, if possible, JIT on/off, then write a three-paragraph conclusion.

**Answer:** Use Section 8 and the `pyperf` runner. Keep the source and dependencies fixed, record exact interpreter/build/JIT state and hardware, collect repeated runs, and measure a real workload as well as the synthetic loop. The first paragraph should describe setup and controls; the second should report measured results and variation; the third should explain what the evidence supports and what remains unproven. There is no universally correct numeric answer: results depend on the actual machines, builds, workload, and measurement.

## References and further reading

Prefer documentation for the exact CPython version being measured. The sources below explain the core mechanisms and version-specific constraints.

1. [PEP 659 — Specializing Adaptive Interpreter](https://peps.python.org/pep-0659/) — rationale, quickening, adaptive instructions, inline caches, and specialization/de-specialization.
2. [PEP 744 — JIT Compilation](https://peps.python.org/pep-0744/) — background on CPython's experimental copy-and-patch JIT; read its status and scope notes as well as the release documentation.
3. [What’s New in Python 3.11](https://docs.python.org/3.11/whatsnew/3.11.html) — specialization and performance changes in 3.11.
4. [What’s New in Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html) — including PEP 709 comprehension inlining and other runtime improvements.
5. [What’s New in Python 3.13](https://docs.python.org/3.13/whatsnew/3.13.html) — experimental JIT build options and the Tier 2 pipeline.
6. [What’s New in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html) — JIT availability in official macOS/Windows binaries, experimental status, performance caveats, and introspection.
7. [The `dis` module documentation](https://docs.python.org/3.14/library/dis.html) — `adaptive` and `show_caches` options and bytecode inspection.
8. [The `sys` module documentation](https://docs.python.org/3.14/library/sys.html#sys._jit) — experimental `sys._jit` API, where available.
9. [CPython source: `Python/bytecodes.c`](https://github.com/python/cpython/blob/main/Python/bytecodes.c) and [specialization implementation](https://github.com/python/cpython/blob/main/Python/specialize.c) — implementation details; use the matching release tag when studying a specific version.
10. [CPython JIT developer notes: `Tools/jit/README.md`](https://github.com/python/cpython/blob/main/Tools/jit/README.md) — build requirements and JIT implementation notes.
11. [CPython configure options](https://docs.python.org/3.14/using/configure.html) — including `--enable-experimental-jit` and `--with-tail-call-interp`.
12. [Python support for Linux `perf` profiling](https://docs.python.org/3.14/howto/perf_profiling.html) — version/build-specific Python-frame visibility.
13. [uv managed Python distributions](https://docs.astral.sh/uv/concepts/python-versions/) and [python-build-standalone build profiles](https://github.com/astral-sh/python-build-standalone/blob/main/docs/running.rst) — examples of why distribution build provenance matters.
14. [pyperf documentation](https://pyperf.readthedocs.io/) — repeatable Python benchmarking.
15. [pyperformance](https://github.com/python/pyperformance) — a suite of benchmarks for comparing Python implementations and releases.
16. [Faster CPython project](https://github.com/faster-cpython) — background and ongoing performance work.

> **Version discipline:** The source links to CPython `main` describe the development branch and can move. For an implementation claim about Python 3.12, 3.13, or 3.14, select the corresponding tag or read that release's documentation. Never assume a current development-branch opcode or flag existed in an older release.
