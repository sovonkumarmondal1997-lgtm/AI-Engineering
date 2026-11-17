# CPython Internals and Runtime Behaviour — Practice Questions

**Target:** CPython 3.12–3.14. **Audience:** beginner through advanced. **Format:** 36 questions with a reasoned answer key.  
**Primary specification:** `roadmap-CPython-Internals-and-Runtime-Behaviour.md`, especially its four phases, Lessons 01–10, six required “what happens?” traces, and `pyx-inspector` mini-project. The project tree places this file beside Lessons 01–10 in `Stage 1 — Programming & Computational Thinking/19-CPython-Internals-and-Runtime-Behaviour/`.

## How to use this bank

Attempt each question before opening its answer. For code/output questions, use the stated assumptions and distinguish guaranteed language behaviour from CPython implementation details. Bytecode, object sizes, timing, scheduling, allocator behaviour, JIT support, and OS tools can vary. Unless a question explicitly pins a build, use a standard GIL-enabled CPython 3.12–3.14 build; call out when the answer requires checking the exact interpreter, build flags, operating system, or C-extension behaviour.

### Labels

- **Phase A — From Source to Execution:** Lessons 01–03.
- **Phase B — Modules and Memory:** Lessons 04–05.
- **Phase C — Parallelism and Speed:** Lessons 06–07.
- **Phase D — Observing and Debugging:** Lessons 08–10.
- Difficulty: **Beginner**, **Intermediate**, or **Advanced**.
- Type: conceptual, output prediction, code reading, debugging, coding, experiment design, scenario diagnosis, or system design.

---

# Questions

## Phase A — From Source to Execution

### Q01. Compilation pipeline and error classification

- **Difficulty:** Beginner
- **Skill assessed:** Distinguishing compile-time syntax errors from runtime name errors
- **Type:** Conceptual / code reading

For each snippet, state whether the error occurs before execution or during execution, name the exception, and explain the relevant pipeline stage.

```python
# A
source = "if True print('hi')"
compile(source, "<A>", "exec")

# B
source = "print(missing_name)"
code = compile(source, "<B>", "exec")
exec(code)
```

### Q02. Interpret `dis` without relying on exact opcodes

- **Difficulty:** Beginner
- **Skill assessed:** Reading stack-machine intent and version-aware bytecode
- **Type:** Code reading

```python
import dis

def calculate(a, b):
    return a + b * 2

dis.dis(calculate)
```

Describe the logical operations and value-stack effect in evaluation order. Name at least three details you would **not** assert identically across CPython 3.12, 3.13, and 3.14.

### Q03. The local-variable trap

- **Difficulty:** Beginner
- **Skill assessed:** Symbol-table scope analysis
- **Type:** Output prediction

What happens when `f()` runs, and why is this not fixed by the global `x`?

```python
x = 10

def f():
    print(x)
    x = 20

f()
```

### Q04. `.pyc` cache reasoning

- **Difficulty:** Intermediate
- **Skill assessed:** Import caching and bytecode cache invalidation
- **Type:** Conceptual / scenario diagnosis

A service starts with a cold filesystem cache and imports a package repeatedly across process restarts. Explain what a `.pyc` file stores, when it can help, how timestamp-based and hash-based invalidation differ at a high level, and why it does not make an already-running function execute faster. Include one deployment condition in which writing `__pycache__` may be unavailable or undesirable.

### Q05. Frame chain and recursion

- **Difficulty:** Intermediate
- **Skill assessed:** Frames, tracebacks, and recursion limits
- **Type:** Output prediction / conceptual

```python
import sys

def descend(n):
    if n == 0:
        return sys._getframe().f_code.co_name
    return descend(n - 1)

print(descend(2))
print(sys.getrecursionlimit() > 0)
```

State the two printed values in semantic terms. Then explain what changes if `descend` recurses far enough to exceed the configured recursion limit, why Python does not promise tail-call elimination, and why retaining frame/traceback objects can retain locals. Why should an answer not equate Python frame depth with C-stack depth on every CPython version/build?

### Q06. Required trace: generator suspension

- **Difficulty:** Intermediate
- **Skill assessed:** Generator execution state and frame lifetime
- **Type:** Output prediction / trace

```python
def gen():
    x = yield "ready"
    yield x * 2

g = gen()
print(next(g))
print(g.gi_running)
print(g.send(5))
print(g.gi_running)
```

Predict the output, explain when the body starts, what `send(5)` does, and what `gi_running` does and does not tell you. Assume ordinary CPython generator semantics and no concurrent access to `g`.

### Q07. Closure capture and late binding

- **Difficulty:** Intermediate
- **Skill assessed:** Closure cells and lexical scope
- **Type:** Output prediction / debugging

```python
def make_functions():
    funcs = []
    for i in range(3):
        funcs.append(lambda: i)
    return funcs

print([f() for f in make_functions()])
```

Predict the output and explain it using closure cells. Give one minimal change that makes the functions return `0`, `1`, and `2` respectively, and explain why that change works.

### Q08. Disassembly experiment: specialization

- **Difficulty:** Advanced
- **Skill assessed:** Adaptive interpreter evidence and benchmark discipline
- **Type:** Experiment design

Design an experiment for CPython 3.12–3.14 that compares `dis.dis(func)` with `dis.dis(func, adaptive=True)` before and after warm-up. State the setup, commands or code, expected observations, what you would record, and at least three things the experiment cannot prove. Do not require a particular opcode spelling.

### Q09. Tiny pipeline inspector

- **Difficulty:** Advanced
- **Skill assessed:** Integrating tokenization, AST, symbol tables, code objects, and bytecode
- **Type:** Coding / system design

Design a small `pipeline` command for `pyx-inspector` that accepts a Python source file and reports token summary, AST, symbol-table scope names, and bytecode/code-object metadata for a selected function. Give a minimal implementation outline or pseudocode, define how syntax errors are reported, and list at least four safeguards against fragile output or untrusted input assumptions.

---

## Phase B — Modules and Memory

### Q10. Required trace: second import

- **Difficulty:** Beginner
- **Skill assessed:** `sys.modules`, module identity, and import execution
- **Type:** Trace / conceptual

Assume `json` has not been removed from `sys.modules` and no custom import hooks or reloads are involved.

```python
import json
first = json
import json
second = json
print(first is second)
print(json.__name__)
```

Predict the output and explain the high-level steps on the second import. What changes conceptually if the code uses `importlib.reload(json)` instead?

### Q11. Import shadowing diagnosis

- **Difficulty:** Beginner
- **Skill assessed:** Import path diagnosis
- **Type:** Debugging / scenario

A project contains `app.py` and a local file named `json.py`. Running `python app.py` makes `import json; json.loads(...)` fail with an unexpected `AttributeError`. Explain the likely cause, give three commands or checks to confirm it, and propose durable fixes. State why deleting one entry from `sys.modules` is not a robust general fix.

### Q12. Circular import and partial initialization

- **Difficulty:** Intermediate
- **Skill assessed:** Import state and module design
- **Type:** Code reading / debugging

`alpha.py` contains `from beta import make_beta` and then defines `make_alpha`. `beta.py` contains `from alpha import make_alpha` and then defines `make_beta`. Explain why importing `alpha` may fail with a partially initialized module. Provide two structural fixes and one debugging observation that helps confirm the diagnosis.

### Q13. Required trace: closure capture revisited as an object-lifetime question

- **Difficulty:** Intermediate
- **Skill assessed:** Object references and lifetime
- **Type:** Trace / conceptual

```python
def build():
    value = {"items": [1, 2]}
    def read():
        return value["items"]
    return read

reader = build()
print(reader())
```

Explain which reference keeps the dictionary reachable after `build()` returns and why the local name disappearing does not destroy the object. Does this example prove the dictionary is stored in a particular physical layout or that every closure captures a value by copying it? Explain.

### Q14. Per-object memory estimate with assumptions

- **Difficulty:** Intermediate
- **Skill assessed:** Shallow versus transitive memory accounting
- **Type:** Calculation / measurement design

On a **64-bit GIL-enabled CPython 3.12 build**, estimate the memory attributable to `shared = 1000; shared_list = [shared] * 1_000_000` versus `distinct_list = [i + 1000 for i in range(1_000_000)]`. Assume the latter values are distinct integer objects, and use an illustrative pointer width of 8 bytes and an illustrative `sys.getsizeof(1)` value of 28 bytes. State assumptions and avoid presenting the estimate as an exact measurement. Explain what `sys.getsizeof(list_obj)` includes and omits, and how you would measure the actual experiment with `tracemalloc`. Also explain why `is` is not numeric equality, what small-integer caching/string interning mean at a high level, and why CPython implementation details (including immortal objects in 3.12+) do not justify using identity comparisons for ordinary values.

### Q15. Why RSS may not fall after `del`

- **Difficulty:** Intermediate
- **Skill assessed:** Allocator layers and fragmentation
- **Type:** Scenario diagnosis

A batch job creates millions of short-lived dictionaries, deletes them, runs `gc.collect()`, and sees little change in RSS. Explain at least four compatible reasons, including the difference between object reclamation and returning pages to the OS. Explain the roles of pymalloc arenas, pools, and blocks in fragmentation. Propose two mitigations and one experiment that could distinguish a retained-reference leak from allocator retention/fragmentation.

### Q16. Required trace: exception in `__del__`

- **Difficulty:** Intermediate
- **Skill assessed:** Finalization and unraisable exceptions
- **Type:** Output prediction / trace

```python
class Item:
    def __del__(self):
        print("finalizing")
        raise RuntimeError("cleanup failed")

item = Item()
del item
print("after delete")
```

For ordinary CPython execution where deleting the last reference immediately triggers finalization, describe the visible output and exception handling. Why should production code not rely on `__del__` for critical cleanup or on finalization occurring at a portable exact time?

### Q17. Memory representation trade-off

- **Difficulty:** Advanced
- **Skill assessed:** Data layout and measurement design
- **Type:** Experiment design / system design

You must store five million numeric values for analytics. Compare a Python `list` of `float` objects, `array('d')`, and a NumPy array (if NumPy is installed). Specify a fair measurement plan for peak memory and throughput, distinguish payload from wrapper/object overhead, and explain which workload details could change the winner. Do not invent benchmark results.

### Q18. Import instrumentation and plugin isolation

- **Difficulty:** Advanced
- **Skill assessed:** Finders/loaders, plugin boundaries, and import security
- **Type:** System design

Design a mini plugin loader that loads approved Python modules from a configured directory. Include an outline for a `sys.meta_path`-based import observer that records module names/origins and measures actual module execution time without changing finder order or invoking finders twice. Describe how you would handle loaders that lack `exec_module`, plugin failures, common shadowing mistakes, and trust boundaries. Explain why a custom import hook or allow-list is not automatically a security sandbox.

---

## Phase C — Parallelism and Speed

### Q19. GIL and thread prediction

- **Difficulty:** Beginner
- **Skill assessed:** CPU-bound versus I/O-bound concurrency
- **Type:** Conceptual / experiment prediction

On a standard GIL-enabled CPython build, predict whether four Python threads running independent CPU-bound pure-Python loops should be expected to run four times faster than one thread. Contrast this with four threads waiting on blocking I/O. Name at least three variables that prevent a timing result from being universal.

### Q20. Required trace: `sys.exit()` in a thread

- **Difficulty:** Intermediate
- **Skill assessed:** `SystemExit` semantics and thread boundaries
- **Type:** Trace / output prediction

```python
import threading

def worker():
    print("worker before")
    raise SystemExit(7)

thread = threading.Thread(target=worker)
thread.start()
thread.join()
print("main after join")
```

Assuming the thread starts successfully and output writes succeed, explain which messages are expected, what happens to the worker thread, and why the main process is not normally terminated with exit status 7. Distinguish `sys.exit()` from `os._exit()`.

### Q21. Find the race

- **Difficulty:** Intermediate
- **Skill assessed:** Shared-state race reasoning
- **Type:** Debugging / code reading

```python
import threading
counter = 0

def increment_many(n):
    global counter
    for _ in range(n):
        counter += 1

threads = [threading.Thread(target=increment_many, args=(100_000,)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)
```

Why is it incorrect to claim that the GIL makes this program logically race-free? Give two valid repair strategies and describe how you would test the repair. Do not claim that every run must visibly lose increments.

### Q22. Required trace: `fork` after threads

- **Difficulty:** Advanced
- **Skill assessed:** Process creation, inherited locks, and OS assumptions
- **Type:** Trace / scenario diagnosis

A Linux/POSIX service on CPython 3.12–3.14 starts multiple threads, then calls `os.fork()` from one thread. Explain what state the child inherits and why locks held by threads that do not exist in the child can cause deadlock. Include the documented warning behavior and the Python 3.14 multiprocessing start-method default change. State the safest general design alternatives and the assumptions/limitations of any answer. Do not provide a “works everywhere” prediction for arbitrary libraries.

### Q23. Fair concurrency benchmark

- **Difficulty:** Intermediate
- **Skill assessed:** Benchmark methodology
- **Type:** Experiment design

Design a benchmark comparing one thread, four threads, and four processes for (a) CPU-bound pure Python and (b) blocking I/O simulated with `time.sleep`. Include workload size, warm-up, repetitions, timing, process startup costs, correctness checks, machine/build metadata, and how you would report uncertainty. What observations are plausible, and why does one run not establish a general rule?

### Q24. Specialization and de-specialization

- **Difficulty:** Intermediate
- **Skill assessed:** PEP 659 adaptive specialization and guards
- **Type:** Conceptual / experiment design

A function `add(a, b): return a + b` is repeatedly called with integers and then with strings or mixed types. Explain what adaptive specialization may do in CPython 3.12–3.14, what a guard is, and why exact `dis` output must be treated as version/build-sensitive. Outline an experiment using `dis.dis(..., adaptive=True)`.

### Q25. Experimental JIT decision

- **Difficulty:** Advanced
- **Skill assessed:** Runtime/build capability and production performance evaluation
- **Type:** Scenario diagnosis / system design

A team proposes enabling CPython's experimental JIT in production because a microbenchmark ran faster once. Give a go/no-go evaluation plan covering build availability, runtime flags, representative workload, warm-up, repeatability, confidence intervals, memory/startup cost, observability, canary, rollback, and the possibility of no speed-up or regression. State what must be verified for the exact 3.13/3.14 build.

### Q26. Free-threaded build and thread safety

- **Difficulty:** Advanced
- **Skill assessed:** GIL variants and concurrency guarantees
- **Type:** Conceptual / scenario diagnosis

Explain how a free-threaded CPython build changes the concurrency picture and why it does not make compound application invariants automatically safe. Contrast it with subinterpreters: what isolation/data-transfer constraints apply, and what changed in Python 3.14 with `concurrent.interpreters` / `InterpreterPoolExecutor`? Identify what you would check about the exact interpreter build, GIL state, C-extension compatibility and wheels before interpreting a benchmark or deploying either model.

### Q27. Benchmark result critique

- **Difficulty:** Advanced
- **Skill assessed:** Performance reasoning and confounders
- **Type:** Code review / experiment design

A report says: “Version B is 18% faster because it executed fewer bytecode instructions in one `time.time()` run. We ran the benchmark immediately after startup with tracing enabled.” Identify at least five methodological or interpretive defects and propose a better comparison that could support a defensible conclusion.

---

## Phase D — Observing and Debugging

### Q28. Design a safe `doctor` report

- **Difficulty:** Beginner–Intermediate
- **Skill assessed:** Runtime introspection and redaction
- **Type:** Coding / system design

Design a JSON `doctor` report for a production Python service. Include interpreter/build and relevant flags, executable and virtual-environment information, platform, usable CPU hints, selected resource limits, GC/thread summaries, and encoding/locale. Explain why `os.cpu_count()` can differ from CPUs usable under affinity/container quotas and how you would feature-detect `os.process_cpu_count()` (Python 3.13+) and platform-specific affinity/cgroup data. Also diagnose why logs may appear late when stdout is redirected or not attached to a TTY, and give safe fixes. Specify at least six values you would omit or redact, how you would test redaction, and how you would handle unavailable platform-specific data. Do not dump the entire environment or `sys.path` by default.

### Q29. Post-mortem versus live hang

- **Difficulty:** Beginner–Intermediate
- **Skill assessed:** Selecting a diagnostic technique
- **Type:** Scenario diagnosis

A request handler raised a reproducible `KeyError` yesterday; today a worker remains alive but stops making progress and uses almost no CPU. Explain the different first-line approach for the two incidents. Include how to preserve traceback/context for the exception and how to gather evidence for the hang without immediately restarting the process.

### Q30. Required trace: process appears stuck with no CPU

- **Difficulty:** Intermediate
- **Skill assessed:** Thread-stack and wait-state diagnosis
- **Type:** Scenario diagnosis / operational procedure

A Linux service is unresponsive, CPU usage is near zero, and health checks time out. Give an ordered diagnostic plan using safe stack capture (`faulthandler`, `sys._current_frames()` if in-process access is available, or a suitable external tool), OS wait-state evidence, and lock/dependency inspection. Explain why a no-CPU hang differs from a CPU spin and what each observation cannot prove.

### Q31. PEP 768 remote attach safety

- **Difficulty:** Advanced
- **Skill assessed:** Version-aware remote debugging and security
- **Type:** Scenario diagnosis / system design

An operator wants to run `python -m pdb -p PID` against a production worker. Explain the Python-version availability boundary, permission/OS/build considerations, the purpose of the `-X disable_remote_debug` / `PYTHON_DISABLE_REMOTE_DEBUG` controls where supported, and operational risks. Give preconditions, evidence to preserve, and stop conditions. Explain why remote attach is not universally available or risk-free.

### Q32. Required trace: `sys.exit()` and process lifecycle contrast

- **Difficulty:** Intermediate
- **Skill assessed:** Exit semantics across control boundaries
- **Type:** Trace / conceptual

Compare these three actions: (a) `sys.exit(3)` in the main thread, (b) `sys.exit(3)` in a non-main `threading.Thread`, and (c) `os._exit(3)` in any process context where it is callable. For each, describe the intended control-flow effect, cleanup/finalization expectations, and why the same numeric argument does not mean the same lifecycle outcome.

### Q33. Build a mini trace CLI

- **Difficulty:** Advanced
- **Skill assessed:** `sys.monitoring`, event choice, filtering, and cleanup
- **Type:** Coding / system design

Design `pyx trace script.py` for CPython 3.12–3.14. It should report a call tree, call counts/timings, and line-hit counts; support `--only-package`; compare overhead with `sys.settrace`; and release monitoring tool IDs and disable events even if the target script raises. Specify the event model (including the location-specific `sys.monitoring.DISABLE` optimization), reentrancy strategy, exception handling, filtering rules, test strategy, and version-sensitive event names you would verify. Name the relevant implementation sources from the syllabus and state what a source review can and cannot establish across versions.

### Q34. Tracing-hook coexistence and overhead

- **Difficulty:** Advanced
- **Skill assessed:** Legacy tracing, monitoring, and profiler trade-offs
- **Type:** Conceptual / experiment design

Compare `sys.settrace`, `sys.setprofile`, `sys.monitoring`, and `cProfile` for a debugger, line/branch coverage, call profiling, and low-overhead production observation. Explain the `settrace` global-to-local callback protocol, when `frame.f_trace` must be set explicitly for an already-running frame, `frame.f_trace_lines` / `frame.f_trace_opcodes`, current-thread versus future/all-thread installation, tool coexistence, event granularity, overhead, and cleanup. Contrast interpreter-event instrumentation with OpenTelemetry/APM auto-instrumentation that often wraps or monkey-patches libraries: discuss semantic span context, framework/library coverage, double-instrumentation, and blind spots without assuming either is universally superior. Explain how monitoring can instrument/de-optimize bytecode and why JIT/tier-2 behavior must be checked for the exact build and instrumentation state. Propose a fair benchmark protocol; do not claim one API is always fastest for every workload.

### Q35. Audit hooks are not a sandbox

- **Difficulty:** Advanced
- **Skill assessed:** Security observability boundaries
- **Type:** Conceptual / scenario diagnosis

A team installs `sys.addaudithook` and a `sys.monitoring` callback that flags calls to `eval` and `os.system`, then declares arbitrary plugin code sandboxed. Explain the gaps in this claim, what each mechanism can observe, why callbacks themselves require care, and what architectural boundary is needed for genuinely untrusted code.

### Q36. End-to-end incident and roadmap review

- **Difficulty:** Advanced
- **Skill assessed:** Runtime investigation, evidence, and coverage synthesis
- **Type:** System design / postmortem

A Python API service has intermittent latency spikes, rising RSS, and occasional worker hangs after a dependency upgrade. Write a concise investigation plan that separates hypotheses and evidence for: import/startup regression, memory retention/allocator behaviour, GIL/contention or native blocking, adaptive/JIT differences, and a tracing/monitoring observer effect. Include initial metadata, two low-risk experiments, a decision tree for escalation, evidence retention/redaction, rollback criteria, and a regression-test/postmortem deliverable. Include the `pyx-inspector` acceptance checklist: at least 85% coverage on non-experimental code, graceful feature degradation across CPython 3.12–3.14, reproducible measurements, and `INTERNALS.md` notes linking each command to the CPython source file/function inspected. Your plan must identify which roadmap lessons/tools support each hypothesis.

---

# Answer key and reasoning

## Phase A — From Source to Execution

### A01. Compilation pipeline and error classification

- **A:** `compile()` raises `SyntaxError`; the source cannot be parsed into a valid module code object, so execution does not begin.
- **B:** `compile()` succeeds because `missing_name` is syntactically valid. `exec(code)` raises `NameError` when runtime name resolution cannot find the name in locals/globals/builtins.
- **Why:** Syntax validity and runtime name binding are separate stages. The symbol table can classify names, but it does not guarantee a global name exists at runtime.

### A02. Interpret `dis` without relying on exact opcodes

Python evaluates the left operand `a` first, then evaluates the right operand `b * 2`, then performs the addition and returns the result. A stack-machine mental model for the usual unspecialized sequence is: push `a`; push `b`; push constant `2`; multiply the top two values, leaving `a` below the product; add those two values; return the sum. The exact instruction sequence/argument display may vary with specialization, caches, superinstructions, compiler changes, and Python version. Do not assert exact offsets, opcode names/counts, or cache layout across 3.12–3.14. `dis` is a diagnostic view of implementation bytecode, not a stable language contract.

### A03. The local-variable trap

`f()` raises `UnboundLocalError` at `print(x)`. Because `x` is assigned anywhere in `f`, the compiler classifies it as a local name for that function unless declared `global` or `nonlocal`; the local has not yet been bound at the print. The global `x = 10` is therefore not used for this local lookup. A fix is to remove the assignment, use a distinct local name, or deliberately declare `global x` if mutating the module global is intended.

### A04. `.pyc` cache reasoning

A `.pyc` contains a marshalled code object/cache payload and header metadata, not a running process's state. Import can avoid reparsing/recompiling unchanged source when the cache is valid. Timestamp-based caches compare source metadata such as timestamp and size; hash-based caches use a source hash and a policy for checking it (PEP 552). Cache validity policy and command-line/build settings matter. It does not accelerate each execution of a function after import; runtime speed depends on execution and optimization, not re-reading the source cache. Read-only container layers, package installations with unwritable directories, or `PYTHONDONTWRITEBYTECODE` may prevent or intentionally suppress cache writes. A cache miss causes recompilation; it should not change intended program semantics.

### A05. Frame chain and recursion

The first line prints `descend`, because `sys._getframe()` is called inside that function and its code object's `co_name` is `descend`. The second prints `True` for a normal positive recursion limit. If recursion exceeds the configured limit, CPython raises `RecursionError`; the exact depth at which it happens is not a portable constant and should not be inferred from a single run. Python frames and C-stack depth are not identical on all versions/builds: CPython 3.11+ changed Python-to-Python call execution and frame materialization, and C-stack limits/build choices also matter. Python does not promise tail-call elimination; retaining frame or traceback objects can also retain references to locals and extend object lifetimes, so diagnostics should release them when no longer needed.

### A06. Required trace: generator suspension

Output:

```text
ready
False
10
False
```

Calling `gen()` creates a generator object; its body begins when `next(g)` first advances it. It runs to `yield "ready"` and suspends. While the generator is not actively executing, `g.gi_running` is false. `send(5)` resumes at the suspended `yield`, makes that yield expression evaluate to `5`, assigns `x = 5`, and yields `10`. It suspends again, so `gi_running` is false. The property is a transient execution-state indicator, not a complete thread-safety guarantee; concurrent advancement is not made safe by observing it.

### A07. Closure capture and late binding

Output is `[2, 2, 2]`. Each lambda closes over the same cell for the loop variable `i`; the functions read the cell when called, after the loop has left it bound to `2`. One minimal fix is `funcs.append(lambda i=i: i)`. The default argument is evaluated at each loop iteration and stored in that function's defaults, so each lambda gets the then-current value. This is a change in binding time, not a copy of every object in a general closure.

### A08. Disassembly experiment: specialization

Example plan:

```python
import dis

def add(a, b):
    return a + b

print("before:")
dis.dis(add, adaptive=True)
for _ in range(10_000):
    add(1, 2)
print("after integer warm-up:")
dis.dis(add, adaptive=True)
for _ in range(100):
    add("a", "b")
print("after mixed use:")
dis.dis(add, adaptive=True)
```

Run under each exact interpreter executable and record `sys.version`, build/platform details, warm-up count, call distribution, and disassembly. A stable integer call site may show specialized forms after warm-up; mixed types may alter specialization or cause guard misses/de-specialization. Exact names and transitions are version/build-sensitive. This does **not** prove end-to-end speedup, causation for a benchmark result, or identical behaviour under tracing/JIT/free-threaded builds. It also does not establish that another workload will specialize similarly. Use repeated timing separately and report uncertainty.

### A09. Tiny pipeline inspector

A sound outline: read source as text; call `tokenize.generate_tokens` with `io.StringIO(source).readline`; parse with `ast.parse`; build a symbol table using `symtable.symtable(source, filename, "exec")`; compile with `compile(source, filename, "exec")`; recursively inspect code objects in `co_consts` and select by qualified/name metadata; use `dis.get_instructions`/`dis.dis` for display. Catch `SyntaxError` and report filename, line, offset, and message without pretending later stages succeeded. Safeguards: (1) never execute the input merely to inspect it; (2) cap source and output sizes; (3) treat AST/disassembly formatting as version-specific; (4) avoid dumping secrets from source or locals; (5) handle nested functions/multiple same-named functions; (6) separate machine-readable output from human output; (7) test syntax errors and encoding; (8) do not promise bytecode compatibility across versions. Explain that `compile(..., "exec")` accepts a module/suite and returns a code object, while `compile(..., "eval")` accepts a single expression whose code object produces a value; neither mode executes by itself.

## Phase B — Modules and Memory

### B10. Required trace: second import

Output:

```text
True
json
```

The import machinery first checks `sys.modules`; with the module present, the second import normally reuses that module object and binds the local name. It does not execute module top-level code again under the stated assumptions. `importlib.reload(json)` re-executes the module code in the existing module object; it is not a clean process restart and can have side effects or leave external references to old objects/functions.

### B11. Import shadowing diagnosis

Likely cause: the local `json.py` is found earlier on `sys.path` and imported instead of the standard-library package/module. Confirm with `print(json.__file__)` or `json.__spec__.origin` inside `app.py`, `python -v app.py`, and by printing `sys.path` from the same `app.py` invocation. A separate `python -c` can be useful, but its initial `sys.path` entry can differ from script execution. Rename the local file, remove its stale `__pycache__` if applicable, and ensure launch working directory/path are correct; test in a clean process. Deleting `sys.modules['json']` does not fix path precedence, can leave stale references, and can produce inconsistent imports within the same process.

### B12. Circular import and partial initialization

Importing `alpha` creates and registers a module object in `sys.modules` before its code finishes. While `alpha` imports `beta`, `beta` imports `make_alpha` from the still-initializing `alpha`; that name has not yet been defined, so a partially initialized module error may occur. Fixes include moving shared definitions to a third module, or restructuring dependencies so the imports are local/lazy where that is semantically appropriate; importing modules rather than early-binding names can sometimes reduce the issue but does not automatically remove a true cycle. Confirm using the traceback and `alpha.__spec__`/module origin, or temporarily trace import order with `python -v`.

### B13. Required trace: closure capture and object lifetime

`reader()` returns `[1, 2]`. The nested function retains a closure cell referring to `value`; that cell keeps the dictionary reachable after `build()` returns. The local binding in the completed call frame disappears, but the object remains reachable through the function's closure. The example does not establish a universal physical object layout or that closures copy captured values; CPython uses cells for free variables, while language semantics are lexical binding. The unused `weakref` import has no effect and can be removed.

### B14. Per-object memory estimate with assumptions

A list with one million references needs roughly 8 MB for its element-pointer array at an illustrative 8 bytes/reference, plus the list object's own header and spare capacity from over-allocation. If all entries refer to one shared integer object, count that integer once, not one million times. If each entry refers to a distinct integer object, add roughly 28 MB for the integer objects under the question's illustrative assumption, plus list storage: a rough lower-order estimate is about 36 MB before allocator/overallocation/process effects versus about 8 MB plus one integer in the shared-object case. These are decimal MB approximations (1 MB = 1,000,000 bytes), not exact RSS predictions; actual list over-allocation, object sizes, allocator metadata and transient construction memory differ. The expression `i + 1000` avoids relying on cached small-integer identity for the distinct-value example. `sys.getsizeof(list_obj)` reports the shallow size of the list (including its allocated reference array as reported by that build), not the recursively referenced integer objects. Use a fresh process and `tracemalloc.start()` before constructing each representation, take snapshots or compare `get_traced_memory()` after construction, keep only one case alive at a time, and report interpreter/version/allocator. `tracemalloc` tracks traced Python allocations, not every native allocation or full RSS. `is` tests object identity, whereas `==` tests equality; use `is` for singletons such as `None`, not ordinary numeric/string value comparison. Small-integer caching and string interning can make some equal objects identical in a particular build/context, but that is not a value-semantics guarantee. PEP 683 immortalizes selected objects in CPython 3.12+ to reduce reference-count writes; it does not mean all integers/strings are immortal or that application code should rely on their identity.

### B15. Why RSS may not fall after `del`

Compatible reasons include: (1) references still exist, so objects were not reclaimed; (2) cycles or finalizers delay reclamation; (3) the allocator retains freed blocks for reuse; (4) pymalloc arenas are only returnable when sufficiently empty, so fragmentation can pin arenas; (5) libc/native libraries may retain their own arenas/caches; (6) RSS includes resident pages beyond live Python objects and can fluctuate with OS accounting. `gc.collect()` addresses unreachable cycles, not allocator policy or reachable references. Mitigations: process recycling or bounded batches; reduce per-record object overhead with `__slots__`, tuples/arrays/columnar storage where appropriate; fix references if a leak is found. Compare repeated `tracemalloc` snapshots/object counts with RSS and inspect retaining references using a suitable tool. If traced live allocations fall but RSS stays high, allocator retention becomes more plausible; that alone does not prove fragmentation. In pymalloc, arenas contain pools and pools contain fixed-size blocks; freeing objects returns blocks to pools, but mixed live/free occupancy can keep a pool or arena from being released to the operating system.

### B16. Required trace: exception in `__del__`

On ordinary CPython, if `del item` removes the last reference immediately, standard output contains (in order):

```text
finalizing
after delete
```

Standard error normally reports an unraisable exception in a form resembling `Exception ignored in: <function Item.__del__ at ...>` followed by a traceback and `RuntimeError: cleanup failed`. The exact function address, formatting, and relative interleaving of stdout and stderr vary. An exception raised by `__del__` cannot propagate normally to the statement that caused finalization; it is reported as an unraisable exception (handled through CPython's unraisable-exception machinery, including `sys.unraisablehook`). Finalization timing depends on implementation and reachability; cycles, shutdown, and other runtimes can differ. Use context managers, `try/finally`, and explicit `close()`/resource management for critical cleanup.

### B17. Memory representation trade-off

Plan: use the same numeric values and equivalent operations; run each representation in a separate fresh process; record interpreter/build, OS, allocator, NumPy version, input generation, peak RSS and `tracemalloc` peak, construction time and operation throughput. A list stores references plus separately allocated Python float objects; `array('d')` stores packed C doubles in a contiguous buffer; NumPy stores a contiguous typed buffer plus ndarray metadata (and may use native allocations not fully represented by `tracemalloc`). Avoid counting the source list while measuring the target, or explicitly include it if conversion is part of the real workload. Repeat runs, warm caches as appropriate, and report median/distribution. Numeric operations that need Python-level iteration can erase storage wins; vectorized NumPy operations can change throughput substantially; conversion cost and access pattern matter. No winner should be asserted without measurements for the actual workload.

### B18. Import instrumentation and plugin isolation

Use a configured, canonicalized plugin root and explicit plugin identifiers/entry points; validate each requested plugin against an allow-list before loading. For an import observer, preserve `sys.meta_path` order and delegate each `find_spec(fullname, path, target)` call to the next applicable finder exactly once. Wrap the resulting loader (delegating `create_module` when present and `exec_module` when supported) to time module execution with `time.perf_counter_ns()`; `find_spec` time alone is not import execution time. Record `spec.origin` where available and label built-in, frozen, namespace, or origin-less modules appropriately. Handle loaders without `exec_module` explicitly rather than silently breaking them, and avoid recursive imports in the observer. Keep per-plugin failures isolated and report traceback with secrets redacted. Prefer packaging entry points or a documented importlib-based loader over ad hoc `sys.path` mutation. Rename files that shadow stdlib packages and test under the same launch mode. Run plugins with least privilege and isolate genuinely untrusted code in a separate process/container with OS-level permissions/resource limits and a narrow IPC protocol. An import hook observes or controls some import resolution; it cannot constrain arbitrary already-imported capabilities, native extensions, filesystem/network access, or all execution paths, so it is not a sandbox.

## Phase C — Parallelism and Speed

### C19. GIL and thread prediction

Four CPU-bound pure-Python threads on a standard GIL-enabled build should not be expected to run four times faster; they contend for the GIL and incur scheduling/coordination overhead, and may be slower. Threads can help I/O-bound work because blocking operations often release the GIL, allowing another thread to progress. Results depend on CPU quota/affinity, OS scheduling, interpreter version/build, workload, extension code, warm-up, process/thread startup, memory bandwidth, and background load. Free-threaded builds and extensions that release the GIL are separate cases that must be identified explicitly.

### C20. Required trace: `sys.exit()` in a thread

Expected messages are `worker before` and `main after join`; an uncaught `SystemExit(7)` in the worker terminates that thread's execution. The threading machinery generally treats `SystemExit` specially rather than printing it like an ordinary uncaught exception. It does not normally set the whole process exit status to 7 because it is raised in a non-main thread. In the main thread, `sys.exit(7)` raises `SystemExit` and, if uncaught, terminates interpreter execution with status 7 after normal shutdown handling. `os._exit(7)` terminates the process immediately without normal Python cleanup, regardless of ordinary exception propagation.

### C21. Find the race

The operation `counter += 1` is a read/compute/write sequence, not an application-level atomic increment guaranteed by the language. The GIL protects interpreter execution in a standard build but does not promise compound invariants remain race-free; thread switches and implementation changes matter. Repair options: protect increments with a `threading.Lock`, or accumulate in per-thread local counters and combine after joining. Test by checking exact expected totals over repeated runs and varied workloads, but do not use a single run that happens to match as proof. On free-threaded builds, synchronization requirements become even more explicit.

### C22. Required trace: `fork` after threads

On POSIX/Linux, `fork()` creates a child with a copy-on-write snapshot of the calling process's address space, but only the calling thread exists in the child. A mutex may have been held by a different parent thread at the fork; the child inherits the locked state without inheriting the thread that could release it. The child can deadlock if it touches that lock or code that needs it. Prefer creating worker processes before starting threads, use a supported `spawn`/`forkserver` strategy where suitable, or redesign to avoid fork in a multithreaded process. Python and library versions can warn or change multiprocessing defaults; native libraries add risks. Since Python 3.12, CPython emits a `DeprecationWarning` when it can detect `os.fork()` in a multithreaded process; detection is not guaranteed in every case. In Python 3.14, `fork` is no longer the default multiprocessing start method on any platform; select a context explicitly if you have a justified need. Never generalize this Linux/POSIX explanation to Windows, which has no `fork()` API, or to arbitrary libraries as a guarantee of safety.

### C23. Fair concurrency benchmark

Use a fixed amount of work and validate equal results. Benchmark CPU-bound pure Python and blocking-I/O simulation separately; compare 1 thread, 4 threads, and 4 processes. Run several warm-up and measured repetitions, use `time.perf_counter()`, and report median plus spread/confidence interval rather than a single number. Decide whether process startup/pool setup is inside or outside the timed region and report both if deployment behavior depends on it. Record Python version/build (including GIL mode), OS, CPU model, usable CPU quota/affinity, workload size, and system load. Plausible result: pure-Python CPU work often does not scale with threads on a GIL build, processes can use multiple cores but pay IPC/startup costs, and sleep-based I/O can overlap well with threads. These are hypotheses, not guaranteed ratios; sleep measures scheduling/wait overhead rather than real network latency.

### C24. Specialization and de-specialization

PEP 659's adaptive interpreter can observe repeated operand types and specialize hot instructions; a specialized integer-add path may include guards that verify assumptions. When operand types change, a guard can fail, execution may fall back or de-specialize, and later specialize differently. `dis.dis(func, adaptive=True)` exposes an implementation-oriented view after warm-up, but opcode names, thresholds, caches, and transitions vary by version/build. Experiment with integer-only warm-up, inspect, then call with strings/mixed types and inspect again. Separate this from timing; an observed specialized opcode is not itself proof of end-to-end performance improvement.

### C25. Experimental JIT decision

Do not approve based on one microbenchmark. Verify the exact interpreter build has the experimental JIT compiled in, the supported runtime configuration/flags for that build, and whether the JIT is actually enabled (the 3.13–3.14 feature is experimental and availability differs across distributions/builds). Benchmark representative production-like workloads, cold startup and warmed steady state, memory and CPU, and latency percentiles; repeat across isolated runs and report uncertainty. Include instrumentation/profiling interactions and extension compatibility. Canary with comparable traffic and explicit SLO guardrails; define rollback to the known-good interpreter/configuration before rollout. A no-speedup or regression is plausible. Never assume every CPython 3.13/3.14 installation includes or enables the JIT.

### C26. Free-threaded build and thread safety

A free-threaded build aims to allow multiple threads to execute Python code concurrently without the traditional global interpreter lock, subject to build/runtime and extension constraints. It does not make multi-step business invariants atomic: shared mutable state still needs locks, queues, ownership, or other synchronization. Verify build configuration/runtime GIL state using the exact version's documented interfaces and build metadata; check whether third-party C extensions support free-threaded operation and whether importing them changes runtime behavior. For subinterpreters, account for separate interpreter state and the need to communicate/copy data rather than assume ordinary mutable Python objects are shared freely; verify availability and APIs for the exact version (the standard-library `concurrent.interpreters` and `InterpreterPoolExecutor` are Python 3.14 features). Compare equivalent builds, workloads, startup/transfer costs, and dependency versions. A result from a GIL-enabled binary is not evidence about a free-threaded build or an interpreter pool, and vice versa.

### C27. Benchmark result critique

Defects include: (1) one run is noise-sensitive; (2) `time.time()` is not the preferred monotonic high-resolution duration clock; (3) fewer bytecodes do not necessarily mean faster execution; (4) no warm-up ignores adaptive specialization; (5) tracing changes runtime cost and possibly specialization; (6) startup/cache/CPU-frequency effects are uncontrolled; (7) no environment/build metadata; (8) no correctness check; (9) no repeated measurements/uncertainty; (10) workload may not represent production. Improve with `pyperf` or a disciplined `perf_counter` harness, warm-up, multiple independent runs, identical correctness-checked workloads, explicit tracing/JIT/build settings, machine metadata, and confidence intervals. Use bytecode as explanatory evidence, not the performance conclusion itself.

## Phase D — Observing and Debugging

### D28. Design a safe `doctor` report

Include version/build/implementation and relevant flags, executable, prefix/base-prefix and venv indicator, OS/platform/machine, process and usable CPU hints, selected resource limits, GC counters/stats, thread count and optionally a bounded thread-stack summary, filesystem/default encoding and preferred locale encoding. Distinguish `os.cpu_count()` from effective usable CPUs: feature-detect `os.process_cpu_count()` (Python 3.13+), use affinity APIs where available, and inspect cgroup quota/limits only when supported. Use explicit schema/version and JSON-safe values. Omit/redact environment variables, access tokens, passwords, API keys, URL credentials/query strings, user data in locals, full argv, and unfiltered paths; do not dump the full environment or `sys.path` by default. Test with sentinel values such as `API_TOKEN=SECRET_SENTINEL` and assert the sentinel never appears in serialized output. Feature-detect OS-specific files/APIs and report `null` plus a reason/status instead of crashing. Ensure thread dumps are bounded and access-controlled. Explain that stdout may be block-buffered when redirected; use explicit flushing where appropriate or configure unbuffered output with `-u` / `PYTHONUNBUFFERED` when operationally justified, and do not assume flushing repairs lost data after a hard crash.

### D29. Post-mortem versus live hang

For the reproducible `KeyError`, preserve the full traceback and chained exceptions in logs (`logging.exception`, `traceback` formatting, or `TracebackException`); reproduce with minimal input and use `pdb.post_mortem(tb)`/`python -m pdb script.py` when interactive access is appropriate. For a live near-zero-CPU hang, first capture timestamps, health/latency metrics, thread stacks (`faulthandler`, `sys._current_frames()` via an in-process diagnostic path, or authorized `py-spy dump`), and OS wait state/dependency information. Avoid restarting before evidence is captured unless customer safety or SLO policy requires mitigation. Exception post-mortem examines a completed failure traceback; hang debugging examines a still-running process's current waits/stacks.

### D30. Process stuck with no CPU

A safe order: (1) record PID, start time, deployment/version, recent logs/metrics, thread count and whether all workers or one request are affected; (2) use an already-enabled signal-triggered `faulthandler` dump if configured; (3) if an approved in-process diagnostic endpoint exists, capture `sys._current_frames()` stacks with redaction; (4) with authorization, capture `py-spy dump --pid PID` if installed and permitted; (5) inspect OS state, file/socket waits, open descriptors and dependency health using platform-appropriate tools; (6) compare stacks across two captures to identify stable waits; (7) inspect lock ownership and external dependencies; (8) preserve evidence and only then mitigate. Near-zero CPU suggests blocking/waiting/deadlock or an external dependency, but does not prove it; a CPU spin usually consumes CPU and may require `top -H`, native stacks, or profiling. A stack alone may not show native lock ownership or kernel wait details; external attach may fail due to permissions, container namespaces, ptrace policy, or build limitations.

### D31. PEP 768 remote attach safety

PEP 768 adds a supported mechanism for executing a debugging script in a running CPython process at an interpreter safe point; `python -m pdb -p PID` is associated with the Python 3.14 feature set, but verify the exact 3.14 build/platform and documented CLI/API support before relying on it. Permissions and implementation support matter; Linux ptrace/credential/container restrictions and platform-specific process access can block attach. Where supported, `-X disable_remote_debug` and `PYTHON_DISABLE_REMOTE_DEBUG` provide controls to disable remote debugging; verify exact option/env availability in that interpreter's documentation. Before attach: obtain incident approval, verify PID/namespace, use the least-privileged authorized operator, preserve stacks/logs/metrics/core evidence, assess pause/latency risk, and avoid exposing a debug listener publicly. Stop if latency/SLO worsens, the target is critical and pause risk is unacceptable, or permissions/support are unclear. Attach can alter process state, expose secrets, or crash/perturb a service; it is not universal or risk-free.

### D32. Required trace: `sys.exit()` and process lifecycle contrast

- **(a) Main thread:** `sys.exit(3)` raises `SystemExit(3)`. If uncaught, it initiates interpreter shutdown and normally yields process exit status 3 after shutdown handling; it does not promise immediate process termination, because shutdown handlers and non-daemon threads can delay completion.
- **(b) Non-main thread:** it raises `SystemExit` in that thread and ordinarily terminates that thread; it does not normally terminate the entire process with status 3. Other non-daemon threads can keep the process alive.
- **(c) `os._exit(3)`:** terminates the process immediately with the OS exit status, bypassing normal Python cleanup such as `finally` blocks, `atexit` handlers, buffered stream flushing, and object finalization.

The numeric argument is interpreted at different control boundaries. For (b), the thread normally ends without setting the process status to 3; other non-daemon threads may keep the process alive. For (c), `_exit(3)` terminates the process immediately with status 3 and bypasses Python cleanup. In normal application code, use `sys.exit`/exceptions and coordinated shutdown; reserve `_exit` for narrow low-level child-process/error paths where bypassing cleanup is intentional.

### D33. Build a mini trace CLI

Use `sys.monitoring` when available (CPython 3.12+) and degrade clearly on older interpreters. Allocate a free tool ID with `use_tool_id`, register only required callbacks, and enable minimal events. `PY_START`/`PY_RESUME` and `PY_RETURN`/`PY_YIELD` can support call/generator lifecycle tracking; `LINE` supports line hits; timing should use `time.perf_counter_ns()` and define whether nested child time is inclusive or exclusive. Filter code by normalized filename/package root and exclude the tracer itself and standard-library code unless requested. Guard callbacks with a reentrancy flag or carefully designed state so callback work does not recursively pollute measurements. Use `sys.monitoring.DISABLE` only when an event at that code location no longer needs to fire; it disables that local event at that location, not the global event or other locations. Wrap execution in `try/finally`: disable global events, clear every local event mask installed by this tool, unregister each callback with `register_callback(tool_id, event, None)`, then call `free_tool_id`. `free_tool_id()` alone does not disable events or unregister callbacks. Perform this cleanup even when the target script or a callback raises; preserve the target exception while recording instrumentation failures safely. Test golden event sequences on tiny functions, branches, exceptions, generators and recursion; property-test that observed line hits are valid executable/source lines and compare against known executed lines and branch outcomes. Make callback bodies bounded and non-blocking; catch internal callback failures, stop or disable the tool according to a documented policy, and do not silently swallow the target script’s exception. Test target exceptions and assert that the tool ID is free and events no longer fire after cleanup. Event names/availability differ between 3.12, 3.13, and 3.14 (including branch-event changes), so feature-detect `monitoring.events` and validate exact semantics against the target docs. Compare overhead against `settrace` on identical workloads and report repeated measurements. Do not claim exact wall time from callbacks without accounting for callback cost. For source review, inspect `Lib/bdb.py`, `Lib/pdb.py`, `Lib/trace.py`, the coverage.py `sysmon` tracer, and `Python/instrumentation.c` in the matching version; record the file/function and do not mistake implementation details for language guarantees.

### D34. Tracing-hook coexistence and overhead

- `sys.settrace`: per-thread tracing protocol with call/line/return/exception and optional opcode events; useful for debuggers and line tracing but can impose high overhead and generally has one active trace function per thread context.
- `sys.setprofile`: call/return and C-call-related events; typically coarser than line tracing and useful for call profiling; it also needs correct thread installation/cleanup.
- `sys.monitoring`: CPython 3.12+ event API with tool IDs and event selection/local events; designed for lower overhead and multiple tools to coordinate, but tools still need to follow API ownership/event semantics.
- `cProfile`: standard profiler implemented using profiling hooks; convenient call statistics, not a substitute for line/branch coverage or all low-level/native observability.

For `sys.settrace`, the trace callback handles a `call` event and returns a local trace function for that frame; returning `None` declines further tracing of that frame. Installing `sys.settrace()` does not retroactively start tracing every frame already executing; a debugger that needs to trace an existing frame may have to assign its local function to `frame.f_trace` explicitly. `frame.f_trace_lines = False` and `frame.f_trace_opcodes = True` alter per-frame event requests where supported. `sys.settrace` and `sys.setprofile` affect the current thread; `threading.settrace` configures threads started via `threading`, while newer all-thread APIs are version-dependent. APM wrappers can create spans around selected library calls but may miss unwrapped/native work or duplicate spans; interpreter hooks expose execution events but do not automatically provide distributed trace context. Instrumentation may alter interpreter execution paths and interact with specialization/JIT, so benchmark the exact configuration. Benchmark the same executable/build, workload and correctness result; warm up; run repeated independent samples; compare uninstrumented baseline and each tool separately; report medians/spread and environment. Overhead depends on event frequency, callback work, filtering, workload and build; no API is universally fastest. Always remove hooks/disable events in `finally`, and test that later code is no longer instrumented.

### D35. Audit hooks are not a sandbox

Audit hooks report selected interpreter/runtime events and can support security telemetry; `sys.monitoring` exposes execution events such as calls/lines/branches. Neither guarantees interception of every dangerous behavior or prevents arbitrary code from using already-held capabilities, native extensions, direct system calls, or alternative paths. A `CALL` event does not by itself prove a call is malicious, and name-based detection of `eval`/`os.system` is incomplete. Hooks must be fast, avoid recursion/reentrancy, avoid leaking sensitive arguments, and have defined exception behavior; they can affect the observed program. For genuinely untrusted plugins, use a separate process/container/VM with OS-level isolation, restricted filesystem/network/credentials, resource limits, and a narrow authenticated protocol. Hooks are observability/policy signals inside a process, not a security boundary.

### D36. End-to-end incident and roadmap review

A strong model answer separates hypotheses and preserves evidence before intrusive instrumentation:

1. **Baseline metadata:** exact Python version/build/GIL mode/JIT availability, executable/venv, OS/kernel/container CPU and memory limits, dependency versions, deploy timestamp, process uptime, thread count, request/latency/error metrics, RSS and traced-memory snapshots.
2. **Import/startup:** compare startup/import timings and module origins across old/new releases (`-X importtime`, `python -v`, module `__spec__.origin`); verify no local shadowing and compare cold/warm starts. Lesson 04 and `pyx imports` apply.
3. **Memory:** take `tracemalloc` snapshots at comparable workload points, compare object growth and retaining references, and compare with RSS; do not infer a leak from RSS alone. Test representation/batch-size changes in a staging clone. Lesson 05 and Module 1.17 tools apply.
4. **Hang/contention/native blocking:** capture thread stacks twice, check CPU/wait states, locks, file descriptors and dependency latency; use authorized `py-spy`/native tools only when warranted. Separate GIL contention from a native call blocked on I/O/lock. Lessons 06 and 09 apply.
5. **Specialization/JIT:** verify exact build/flags; compare same workload with instrumentation disabled, warmed and cold, and JIT enabled only in a controlled canary. Lesson 07 applies.
6. **Observer effect:** compare an uninstrumented baseline with `settrace`, `cProfile`, a minimal `sys.monitoring` configuration, and the selected OpenTelemetry/APM auto-instrumentation separately; check duplicate spans, library wrappers, callback cost, specialization/JIT effects and cleanup. Lesson 10 applies.
7. **Evidence/security:** timestamp every capture; preserve logs, metrics, stack dumps, configuration, deployment IDs, benchmark scripts/results and checksums where appropriate. Redact credentials, user data, full environment and sensitive frame locals; restrict access and retention.
8. **Escalation/rollback:** if impact breaches SLO or error rate rises, stop experiments and roll back to the known-good release/configuration; do not attach or enable JIT/tracing on a critical worker without approval and a rollback path. Preserve evidence before restart when safe, but customer safety takes priority.
9. **Closure:** write a timeline, evidence-backed root cause, alternatives ruled out, contributing factors, mitigation, regression test, owner/action items and updated runbook. A good answer explicitly labels unverified hypotheses and defines measurable exit criteria. For `pyx-inspector`, report test coverage against the ≥85% non-experimental target, exercise feature-detection paths across 3.12–3.14, make measurements repeatable, and include `INTERNALS.md` notes with exact source file/function references and version.

---

# Practical lab checklist

For each lab, record the question, interpreter/build, OS, exact command, raw observations, interpretation, and limitations. These labs reinforce rather than replace the questions above.

1. **Pipeline lab (Q01–Q03):** inspect tokenization/AST/symbol table/disassembly for a small function. Compare semantic operations, not exact bytecode text.
2. **Import lab (Q10–Q12):** record `sys.modules`, `__spec__.origin`, and import order in a fresh process; create and then remove a local shadowing module.
3. **Memory lab (Q14–Q17):** measure separate representations in fresh processes using `tracemalloc` and RSS; state what each measurement covers.
4. **Concurrency lab (Q19–Q23):** compare CPU and I/O workloads with correctness checks, repeated timings, and machine metadata.
5. **Runtime observation lab (Q28–Q30):** generate a redacted JSON doctor report and compare thread stacks from a controlled blocked-worker demonstration.
6. **Monitoring lab (Q33–Q35):** record expected events for a tiny function, verify cleanup after an exception, and compare instrumentation overhead against a baseline.

## Compact coverage matrix

Question numbers can cover more than one lesson; the primary coverage is shown below.

| Roadmap lesson | Primary questions | Phase |
|---|---|---|
| 01 — Source-to-bytecode pipeline | Q01, Q03, Q04, Q09 | A |
| 02 — Reading bytecode with `dis` | Q02, Q08, Q24, Q27 | A / C |
| 03 — Frames, call stack, evaluation loop | Q05, Q06, Q07, Q13 | A / B |
| 04 — Import system, finders/loaders, `sys.modules` | Q10, Q11, Q12, Q18, Q36 | B / D |
| 05 — Memory allocator and small-object optimizations | Q14, Q15, Q16, Q17, Q36 | B / D |
| 06 — GIL internals and subinterpreters | Q19, Q21, Q22, Q23, Q26, Q36 | C / D |
| 07 — Specializing interpreter and JIT | Q08, Q24, Q25, Q27, Q36 | A / C / D |
| 08 — Runtime introspection (`sys`, `os`, etc.) | Q20, Q28, Q30, Q32, Q35, Q36 | C / D |
| 09 — Post-mortem and remote-attach debugging | Q29, Q30, Q31, Q36 | D |
| 10 — `sys.monitoring` and tracing hooks | Q33, Q34, Q35, Q36 | D |

| Phase | Question range | Main coverage |
|---|---|---|
| Phase A — From Source to Execution | Q01–Q09 | Compilation pipeline, `dis`, scope errors, `.pyc`, frames/recursion, generators, closures, specialization experiment, inspector design |
| Phase B — Modules and Memory | Q10–Q18 | Second import, shadowing, circular imports, closure reachability, memory estimates, allocator retention, `__del__`, representations, plugin loading |
| Phase C — Parallelism and Speed | Q19–Q27 | GIL, thread exit, races, fork-after-threads, fair benchmarks, specialization/JIT, free-threading, benchmark critique |
| Phase D — Observing and Debugging | Q28–Q36 | Doctor report, post-mortem vs hang, no-CPU diagnosis, PEP 768, exit semantics, mini trace, hooks/profilers, audit limits, incident synthesis |

**Question-to-lesson cross-check:** every question Q01–Q36 appears in at least one lesson row above. Q20 and Q32 are mapped to Lesson 08 because they assess `sys.exit`/process-lifecycle introspection; Q04 is mapped to Lesson 01 because `.pyc` caching belongs to the compilation pipeline, while import behavior itself is assessed by Q10–Q12 and Q18. Q36 is a deliberate cross-lesson synthesis question.

## Selected official references

Use the documentation for the **exact interpreter version under test** when an event, flag, opcode, build option, or platform behavior is version-sensitive.

- [CPython internals and development guide](https://devguide.python.org/internals/)
- [`dis` — bytecode disassembly](https://docs.python.org/3/library/dis.html)
- [`compile()` and code objects](https://docs.python.org/3/library/functions.html#compile)
- [PEP 552 — Deterministic `.pyc` files](https://peps.python.org/pep-0552/)
- [PEP 659 — Specializing Adaptive Interpreter](https://peps.python.org/pep-0659/)
- [PEP 683 — Immortal Objects](https://peps.python.org/pep-0683/)
- [Python import system reference](https://docs.python.org/3/reference/import.html)
- [`sys` module](https://docs.python.org/3/library/sys.html)
- [`tracemalloc`](https://docs.python.org/3/library/tracemalloc.html)
- [`threading`](https://docs.python.org/3/library/threading.html)
- [`sys.monitoring` in Python 3.12](https://docs.python.org/3.12/library/sys.monitoring.html)
- [`sys.monitoring` in Python 3.14](https://docs.python.org/3.14/library/sys.monitoring.html)
- [PEP 669 — Low Impact Monitoring for CPython](https://peps.python.org/pep-0669/)
- [CPython `sys.monitoring` implementation (`Python/instrumentation.c`)](https://github.com/python/cpython/blob/3.14/Python/instrumentation.c)
- [CPython debugger implementation (`Lib/bdb.py`)](https://github.com/python/cpython/blob/3.14/Lib/bdb.py)
- [CPython `pdb` implementation (`Lib/pdb.py`)](https://github.com/python/cpython/blob/3.14/Lib/pdb.py)
- [CPython `trace` module (`Lib/trace.py`)](https://github.com/python/cpython/blob/3.14/Lib/trace.py)
- [coverage.py source and `sysmon` tracer](https://github.com/nedbat/coveragepy)
- [PEP 768 — Safe external debugger interface for CPython](https://peps.python.org/pep-0768/)
- [Python 3.14 remote debugging attachment protocol](https://docs.python.org/3.14/howto/remote_debugging.html)
- [`pdb` command-line interface in Python 3.14](https://docs.python.org/3.14/library/pdb.html)

## Final self-assessment rubric

Use this rubric after completing the bank:

- **Strong:** answers identify assumptions, explain causal mechanisms, distinguish language guarantees from CPython/platform details, preserve evidence, and propose reproducible tests with explicit limitations.
- **Developing:** answers are directionally correct but omit build/platform constraints, memory-accounting boundaries, cleanup paths, or benchmark controls.
- **Needs review:** answers rely on one timing, exact cross-version bytecode, “the GIL makes it safe,” RSS as a direct live-object count, or hooks as a sandbox; revisit the corresponding lesson and redo its experiment.

A correct result is not merely a predicted output: it is a justified prediction with the assumptions and limits made explicit.
