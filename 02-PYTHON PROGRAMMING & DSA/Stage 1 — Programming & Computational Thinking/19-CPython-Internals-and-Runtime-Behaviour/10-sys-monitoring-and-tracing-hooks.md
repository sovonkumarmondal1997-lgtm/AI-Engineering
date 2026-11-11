# Lesson 10 — sys.monitoring and Tracing Hooks

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain the legacy `sys.settrace()`, `sys.setprofile()`, and `threading` tracing APIs, including their callback protocol and cleanup requirements.
- Explain how PEP 669's `sys.monitoring` API (CPython 3.12+) uses tool IDs, event masks, callbacks, code-object-local events, and `DISABLE`.
- Build and test a minimal line tracer, a function-start counter, and a small line-hit monitor.
- Design a useful mini-trace command-line tool and compare its overhead fairly with `settrace` and `cProfile`.
- Interpret line, call, return, yield/resume, exception, branch, and instruction events without assuming they are interchangeable.
- Recognize instrumentation interactions with CPython's specializing interpreter and experimental JIT, and distinguish interpreter events from APM monkey-patching.
- Apply tracing safely: avoid recursion, clean up after errors, account for other tools, and never mistake observability hooks for a security sandbox.

## Prerequisites and scope

You should already understand Python functions, code objects, frames, exceptions, generators, imports, and basic profiling. The preceding lessons in this module cover the source-to-bytecode pipeline, frames, the specializing interpreter/JIT, runtime introspection, and debugging.

Examples target **CPython 3.12–3.14**. The examples below were designed for that range; the monitoring examples were executed on CPython 3.13.5. They are not promises about PyPy or other Python implementations. Some event names and debugger behaviour differ between CPython minor versions, especially 3.14. Always check the documentation for the interpreter actually running your program.

## Mental model: instrumentation is a stream of execution events

A Python program normally executes without calling a tracing callback for every line or function. Instrumentation asks the runtime to notify a tool at selected execution points. The tool collects those notifications and infers a useful view: line hits, call counts, timings, breakpoints, or branch coverage.

```text
Python source
    │
    ▼
CPython executes code objects in frames
    │
    ├── legacy hooks: sys.settrace / sys.setprofile
    │       └── Python callback protocol, generally broad and comparatively costly
    │
    └── sys.monitoring (CPython 3.12+; PEP 669)
            ├── tool ID identifies a monitoring client
            ├── event mask selects notifications
            ├── optional local event mask narrows to a code object
            ├── callback records an event
            └── DISABLE can stop repeated local events at a location

Recorded events ──► aggregation ──► coverage / call counts / timings / diagnostics
```

The Python language does not guarantee CPython's frame internals or these monitoring APIs. `sys.monitoring` is a CPython-specific runtime API added in Python 3.12. Even on CPython, event definitions and performance characteristics are version-dependent.

---

## 1. Legacy tracing and profiling hooks

### 1.1 `sys.settrace()`: trace calls, lines, returns, exceptions

`sys.settrace(tracefunc)` installs a trace function for the current thread. CPython invokes the global trace function for events such as a function call; the function's return value determines the local trace function used for that frame. A trace function normally returns itself to keep receiving events, or returns `None` to stop tracing that frame.

The usual event names are `call`, `line`, `return`, `exception`, and (when enabled on a frame) `opcode`. The `arg` value depends on the event: it is generally `None` for `call` and `line`, the return value for `return`, an exception triple for `exception`, and is not a stable universal payload across event kinds. Consult the official `sys.settrace` documentation before relying on payload details.

**Why it matters:** this protocol underpins classic debuggers and tracing tools. **When useful:** teaching how a debugger sees execution, implementing a small diagnostic tracer, or supporting runtimes before 3.12. **Trade-off:** line-level callbacks can be expensive because the interpreter repeatedly enters Python-level callback code.

```python
# legacy_line_trace.py — CPython 3.12+
import sys


def tracer(frame, event, arg):
    # Trace only line events; the code object's name and source line are useful
    # labels, but do not uniquely identify a function across modules.
    if event == "line":
        print(f"{frame.f_code.co_name}:{frame.f_lineno}")
    return tracer


def work():
    a = 1
    b = a + 1
    return b


previous = sys.gettrace()
try:
    sys.settrace(tracer)
    result = work()
finally:
    # Never leave a development tracer installed accidentally.
    sys.settrace(previous)

print("result:", result)
```

Run with `python legacy_line_trace.py`. The exact line numbers and whether additional frames are reported depend on how the file is laid out. The meaningful result is that the tracer observes executed line transitions in `work`; `result` is `2`. A line event means the interpreter is about to execute an instruction associated with a different source line; it does not mean every expression or every machine instruction produces an event.

#### Trace protocol details

- `frame.f_trace` is the frame's local trace function. Assigning it can be useful for a debugger, but setting it alone is not the same as installing a global trace function for future calls.
- `frame.f_trace_lines = False` disables line events for that frame; `True` enables them.
- `frame.f_trace_opcodes = True` requests opcode events for that frame. Opcode tracing can be extremely expensive and bytecode offsets are CPython implementation details.
- The global trace function is called on new frame calls. Its return value selects the local trace function for that frame.
- `sys.settrace()` applies to the current thread. `threading.settrace()` configures tracing for threads started through the `threading` module after the call; `threading.setprofile()` provides the corresponding profile-hook setup. In CPython 3.12, `threading.settrace_all_threads()` and `threading.setprofile_all_threads()` were added to set the corresponding hooks on currently executing Python threads as well as future `threading` threads; check availability before using them. These APIs do not promise to instrument native threads that never enter Python, and third-party debuggers may already own hooks.
- A trace function runs with tracing disabled for itself, which prevents straightforward recursive self-tracing. That is not a reason to let callbacks perform unbounded work: another monitoring client may observe callback activity, and callback work still costs time.

### 1.2 `sys.setprofile()`: call/return-oriented profiling

`sys.setprofile()` is oriented toward function calls and returns rather than every source line. Events include `call`, `return`, `c_call`, `c_return`, and `c_exception`. The `c_*` events concern calls into C-level callables, such as many built-ins and extension functions. This makes profiling useful for understanding call volume, though it is not a replacement for a sampling profiler.

```python
# profile_calls.py
import sys
from collections import Counter

counts = Counter()


def profiler(frame, event, arg):
    if event == "call":
        code = frame.f_code
        counts[(code.co_filename, code.co_name)] += 1
    return profiler


def work():
    return sum(range(10))

previous = sys.getprofile()
try:
    sys.setprofile(profiler)
    work()
finally:
    sys.setprofile(previous)

for (filename, name), count in counts.most_common(5):
    print(name, count, filename)
```

The printed set can include the top-level module frame and library frames, and order depends on execution. The code counts `call` events, not elapsed time. `sys.setprofile()` has its own callback slot; it is not a drop-in way to run several independent profilers. Restore the prior hook rather than blindly leaving a new one installed.

### 1.3 Measuring tracing overhead

The roadmap warns that tracing every line can make code many times slower (often quoted as 10–100× for line tracing). Treat that as a rule of thumb, not a guaranteed multiplier. The actual overhead depends on workload, interpreter version/build, event selection, callback cost, and whether the baseline is CPU-bound or dominated by I/O.

A valid comparison must:

1. Run the same deterministic workload in the same interpreter and environment.
2. Warm up consistently where relevant and repeat each measurement.
3. Measure uninstrumented baseline, then each instrumented mode separately.
4. Keep the profiler's own output and file I/O outside the timed region.
5. Report median or distribution, not just the fastest run.
6. Avoid comparing a line tracer that prints each event with a profiler that only increments an integer; that compares callback work as much as API overhead.

Use `time.perf_counter()` or `time.perf_counter_ns()`. Profiling changes the program's execution cost and can change timing-sensitive behaviour; it is evidence, not a perfect observation of the uninstrumented program.

---

## 2. `sys.monitoring` and PEP 669

### 2.1 What it is and why it exists

`sys.monitoring` is a namespace under `sys`, introduced in CPython 3.12 by [PEP 669](https://peps.python.org/pep-0669/). It is not a separate importable module: use `import sys; sys.monitoring`. It was designed to make debugger, profiler, coverage, and optimizer instrumentation lower impact and more cooperative than legacy hooks.

The key design difference is event selection and location-specific disabling. A tool can request only the events it needs, optionally restrict local events to particular code objects, and return `sys.monitoring.DISABLE` when a local event at a location no longer matters. For example, a coverage tool usually needs to know that a line or branch has been reached at least once, not to receive that same event on every loop iteration.

**Limits:** monitoring is not zero-cost; callbacks run in the process, can affect timing, and can fail. Tool IDs coordinate clients but do not provide isolation or security. You must not assume all third-party tools cooperate correctly.

### 2.2 Tool IDs and coexistence

Tool IDs are integers from `0` through `5`. The conventional IDs are:

- `sys.monitoring.DEBUGGER_ID` (`0`)
- `sys.monitoring.COVERAGE_ID` (`1`)
- `sys.monitoring.PROFILER_ID` (`2`)
- `sys.monitoring.OPTIMIZER_ID` (`5`)

IDs `3` and `4` are available for other tools if they are not already claimed. A tool must call `use_tool_id(id, name)` before configuring that ID and should call `free_tool_id(id)` when finished. Always check whether the ID is available; do not overwrite another tool's registration.

The event system allows several tools to have different IDs. This is cooperation, not complete independence: instrumentation may interact through shared runtime state, and a callback for one tool can be visible to another tool. A tool should not assume it can observe another tool's callback internals.

### 2.3 Registering callbacks and enabling events

The general lifecycle is:

1. Claim an unused tool ID with `use_tool_id`.
2. Register a callback for each event of interest.
3. Enable those events with `set_events(tool_id, event_mask)` or `set_local_events(tool_id, code, event_mask)`.
4. Run the target workload.
5. In `finally`, disable global events, clear local event masks for code objects you modified, unregister callbacks, and release the tool ID.

`set_local_events()` adds local events for a code object; local events do **not** mask global events. Cleanup is version-sensitive: on CPython 3.12–3.13, explicitly disable events, clear any local masks you set, unregister callbacks, and then free the ID. CPython 3.14 added `clear_tool_id()` and changed `free_tool_id()` to clear that tool ID’s events and callbacks before releasing it; explicit cleanup is still useful for clear ownership and for code that supports 3.12–3.13. Do not assume `free_tool_id()` alone has identical semantics across the full target range.

### 2.4 Event families and version-sensitive names

Event constants are attributes of `sys.monitoring.events`. They are bit flags, so combine events with bitwise OR (`|`). Do not copy event names blindly between Python versions.

| Event | Meaning at a high level | Important qualification |
|---|---|---|
| `PY_START` | A Python function starts executing | Not the same as creating a generator object |
| `PY_RESUME` | A suspended generator/coroutine resumes | Resumption is a new execution segment, not a new source-level function definition |
| `PY_RETURN` | A Python function returns normally | Distinct from yielding a value |
| `PY_YIELD` | A generator/coroutine yields | The function remains suspended and may resume later |
| `PY_THROW` | A suspended Python function resumes through a `throw()` path | Event payload differs from start/resume callbacks |
| `PY_UNWIND` | A Python function exits through exception unwinding | Does not mean the exception was necessarily unhandled by the whole program |
| `CALL` | A Python-level call site is reached before the call | C return/raise events are tied to the call event group |
| `C_RETURN` / `C_RAISE` | A non-Python callable returns or raises | Controlled by the `CALL` event group |
| `LINE` | An instruction associated with a new source line is about to execute | Not a statement-coverage guarantee by itself |
| `INSTRUCTION` | A VM instruction is about to execute | High volume; CPython bytecode offsets are not stable APIs |
| `JUMP` | An unconditional control-flow jump is taken | Destination is a bytecode offset |
| `BRANCH` | Conditional branch outcome event | Supported in 3.12–3.13; deprecated in 3.14 |
| `BRANCH_LEFT` / `BRANCH_RIGHT` | Conditional branch direction events | Added in 3.14; `BRANCH` is deprecated, not removed, in 3.14. “Left/right” are not guaranteed to mean true/false; tools must map destinations using the version’s documented semantics |
| `RAISE` / `RERAISE` | An exception is raised / re-raised | `RERAISE` is available in CPython 3.13+; some internal `StopIteration` cases are represented by `STOP_ITERATION` instead |
| `EXCEPTION_HANDLED` | An exception is handled | It is not equivalent to function return |
| `STOP_ITERATION` | A `StopIteration` event relevant to monitoring | CPython may avoid materializing some internal exceptions; use this event for the specified monitoring purpose |

For exact callback signatures and availability, consult the official [Python 3.12](https://docs.python.org/3.12/library/sys.monitoring.html), [Python 3.13](https://docs.python.org/3.13/library/sys.monitoring.html), or [Python 3.14](https://docs.python.org/3.14/library/sys.monitoring.html) documentation. For example, `LINE` callbacks receive `(code, line_number)`, while `PY_START` callbacks receive `(code, instruction_offset)`. `CALL` callbacks receive the code object at the call site, instruction offset, callable, and an argument marker/value. `PY_THROW`, `PY_UNWIND`, `RAISE`, `RERAISE` (where available), `EXCEPTION_HANDLED`, and `STOP_ITERATION` have exception-related payloads. Do not assume all events have the same argument list, or that a callback signature from one minor version is universal.

### 2.5 A safe, minimal call counter

This example counts Python-function execution starts by code object's qualified name. It uses a non-predefined ID, detects conflicts, and cleans up even if the workload raises.

```python
# monitoring_call_counter.py — CPython 3.12+
import sys
from collections import Counter

if not hasattr(sys, "monitoring"):
    raise RuntimeError("This example requires CPython 3.12+ sys.monitoring")

mon = sys.monitoring
TOOL_ID = 3  # Available only if no other tool has claimed it.
counts = Counter()


def on_start(code, instruction_offset):
    counts[code.co_qualname] += 1
    # Returning None leaves the event enabled.
    return None


if mon.get_tool(TOOL_ID) is not None:
    raise RuntimeError(f"monitoring tool ID {TOOL_ID} is already in use")

claimed = False
try:
    mon.use_tool_id(TOOL_ID, "lesson-call-counter")
    claimed = True
    mon.register_callback(TOOL_ID, mon.events.PY_START, on_start)
    mon.set_events(TOOL_ID, mon.events.PY_START)

    def square(value):
        return value * value

    def workload():
        return [square(n) for n in range(4)]

    result = workload()
finally:
    if claimed:
        # Nested finally blocks ensure the ID is released even if one cleanup
        # operation unexpectedly raises.
        try:
            mon.set_events(TOOL_ID, 0)
        finally:
            try:
                mon.register_callback(TOOL_ID, mon.events.PY_START, None)
            finally:
                mon.free_tool_id(TOOL_ID)

print("result:", result)
print("square starts:", counts["square"])
print("workload starts:", counts["workload"])
```

Representative output (the exact number of other function names depends on the runtime and the lines executed):

```text
result: [0, 1, 4, 9]
square starts: 4
workload starts: 1
```

`PY_START` measures starts of Python execution, not all calls to C built-ins. It is also not a count of unique functions: one function may start many times. This example uses only global events, so it does not need to clear local event masks. A production implementation should put cleanup operations in nested `try/finally` blocks if cleanup itself must continue after one cleanup operation fails; it should also report an unavailable ID clearly rather than silently taking over another tool's ID.

### 2.6 Local events and `DISABLE`: the coverage optimization

Suppose a coverage tool only needs to record whether each line was executed at least once. A repeated event for the same location provides no new information after the first hit. Returning `sys.monitoring.DISABLE` from a local event callback suppresses that event at that code location until `sys.monitoring.restart_events()` is called. It does not globally turn off that event or disable other code locations.

```python
# monitoring_line_hits.py — CPython 3.12+
import sys
from collections import Counter

mon = sys.monitoring
TOOL_ID = 3
line_hits = Counter()

def on_line(code, line_number):
    # Count only one hit per (code object, line number) for this demonstration.
    line_hits[(code.co_filename, code.co_qualname, line_number)] += 1
    return mon.DISABLE

if mon.get_tool(TOOL_ID) is not None:
    raise RuntimeError(f"tool ID {TOOL_ID} is already in use")
claimed = False
try:
    mon.use_tool_id(TOOL_ID, "lesson-line-hit-demo")
    claimed = True
    mon.register_callback(TOOL_ID, mon.events.LINE, on_line)
    mon.set_events(TOOL_ID, mon.events.LINE)

    def loop():
        total = 0
        for value in range(3):
            total += value
        return total

    answer = loop()
finally:
    if claimed:
        try:
            mon.set_events(TOOL_ID, 0)
        finally:
            try:
                mon.register_callback(TOOL_ID, mon.events.LINE, None)
            finally:
                mon.free_tool_id(TOOL_ID)

print("answer:", answer)
for item in sorted(line_hits.items(), key=lambda pair: (pair[0][2], pair[0][1])):
    print(item)
```

The count here is deliberately a **first-hit map**, not a frequency counter: each event callback returns `DISABLE`. Exact line numbers depend on the file. `DISABLE` is location-specific; it is useful when repeated hits add no value. `restart_events()` restarts disabled locations across tools, so one tool should not casually call it without understanding that it affects other tools' disabled events.

In real coverage tools, `LINE` events alone may be insufficient for branch coverage. Branch tracking needs control-flow information and version-aware interpretation of `BRANCH` versus `BRANCH_LEFT`/`BRANCH_RIGHT`. A coverage tool must define what it means by a covered line/branch and test its mapping against source code, especially for compound statements, comprehensions, exceptions, and generated code.

---

## 3. Build a mini trace CLI

The module roadmap's mini-project asks for `pyx trace`: call counts, timings, line hits, filters, and an overhead report. The following compact CLI is a teaching implementation, not a production profiler. It supports CPython 3.12+, runs a script, records selected Python execution events, and guarantees that the events and tool ID are cleaned up on normal return or an exception in the target script.

Save as `mini_trace.py`:

```python
#!/usr/bin/env python3
"""Small CPython 3.12+ monitoring demo. Not a production profiler."""
from __future__ import annotations

import argparse
import runpy
import sys
import threading
import time
from collections import Counter
from pathlib import Path

TOOL_ID = 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", help="Python script to execute")
    parser.add_argument("script_args", nargs=argparse.REMAINDER,
                        help="arguments passed to the target script")
    parser.add_argument("--only-package", metavar="PACKAGE",
                        help="record only code whose filename is under this import package")
    args = parser.parse_args()

    if sys.implementation.name != "cpython" or not hasattr(sys, "monitoring"):
        parser.error("mini_trace requires CPython 3.12 or newer")

    import importlib.util
    mon = sys.monitoring
    script = Path(args.script).resolve()
    if not script.is_file():
        parser.error(f"script does not exist: {script}")

    # Resolve a package filter to its source directory. Namespace packages may
    # have several search locations, so retain every available location.
    roots: tuple[Path, ...] = ()
    if args.only_package:
        spec = importlib.util.find_spec(args.only_package)
        if spec is None:
            parser.error(f"cannot find package: {args.only_package}")
        locations = list(spec.submodule_search_locations or [])
        # A module's parent directory is not a package root; accepting it would
        # silently broaden the filter to unrelated sibling modules.
        if not locations:
            parser.error("--only-package requires a package with filesystem search locations")
        roots = tuple(Path(p).resolve() for p in locations)
        if not roots:
            parser.error("package has no filesystem source location to filter")

    def included(code) -> bool:
        filename = code.co_filename
        if filename.startswith("<"):
            return False
        try:
            path = Path(filename).resolve()
        except (OSError, RuntimeError):
            return False
        if args.only_package:
            return any(path == root or root in path.parents for root in roots)
        return path == script

    calls = Counter()
    lines = Counter()
    timings = []
    stacks = threading.local()

    def stack_for_thread():
        if not hasattr(stacks, "items"):
            stacks.items = []
        return stacks.items

    def push(code):
        if not included(code):
            return
        stack = stack_for_thread()
        parent_name = stack[-1][0].co_qualname if stack else None
        stack.append((code, time.perf_counter_ns(), len(stack), parent_name))
        calls[(code.co_filename, code.co_qualname)] += 1

    def finish(code):
        stack = stack_for_thread()
        # Normally the matching activation is the top entry. Search backward
        # defensively so unusual generator/exception paths do not corrupt all
        # later timing records if an event sequence differs by version.
        for index in range(len(stack) - 1, -1, -1):
            active_code, started, depth, parent_name = stack[index]
            if active_code is code:
                del stack[index:]
                timings.append((code.co_filename, code.co_qualname,
                                time.perf_counter_ns() - started, depth, parent_name))
                return

    def on_start(code, offset):
        push(code)

    def on_resume(code, offset):
        push(code)

    def on_throw(code, offset, exception):
        push(code)

    def on_return(code, offset, value):
        finish(code)

    def on_yield(code, offset, value):
        finish(code)

    def on_unwind(code, offset, exception):
        finish(code)

    def on_line(code, line_number):
        if included(code):
            lines[(code.co_filename, code.co_qualname, line_number)] += 1

    callbacks = {
        mon.events.PY_START: on_start,
        mon.events.PY_RESUME: on_resume,
        mon.events.PY_THROW: on_throw,
        mon.events.PY_RETURN: on_return,
        mon.events.PY_YIELD: on_yield,
        mon.events.PY_UNWIND: on_unwind,
        mon.events.LINE: on_line,
    }
    claimed = False
    previous_argv = sys.argv[:]
    previous_path = sys.path[:]
    started_ns = 0
    exit_code = 0
    try:
        if mon.get_tool(TOOL_ID) is not None:
            raise RuntimeError(f"monitoring tool ID {TOOL_ID} is already in use")
        mon.use_tool_id(TOOL_ID, "mini-trace")
        claimed = True
        for event, callback in callbacks.items():
            mon.register_callback(TOOL_ID, event, callback)
        event_mask = 0
        for event in callbacks:
            event_mask |= event
        mon.set_events(TOOL_ID, event_mask)

        sys.argv = [str(script), *args.script_args]
        # Match the important script-import behaviour of `python path/to/script.py`.
        sys.path.insert(0, str(script.parent))
        started_ns = time.perf_counter_ns()
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        # Preserve the target script's ordinary SystemExit meaning.
        if isinstance(exc.code, int):
            exit_code = exc.code
        elif exc.code is None:
            exit_code = 0
        else:
            print(exc.code, file=sys.stderr)
            exit_code = 1
    finally:
        sys.argv = previous_argv
        sys.path[:] = previous_path
        elapsed_ns = time.perf_counter_ns() - started_ns if started_ns else 0
        if claimed:
            # Stop delivery first. There are no local event masks in this CLI.
            try:
                mon.set_events(TOOL_ID, 0)
            finally:
                try:
                    for event in callbacks:
                        mon.register_callback(TOOL_ID, event, None)
                finally:
                    mon.free_tool_id(TOOL_ID)

    print(f"\nInstrumented target elapsed: {elapsed_ns / 1e6:.3f} ms (includes monitoring overhead; not a baseline comparison)")
    print("\nTop call counts:")
    for (filename, name), count in calls.most_common(20):
        print(f"{count:8d}  {name}  [{filename}]")
    print("\nTop line hits:")
    for (filename, name, line), count in lines.most_common(30):
        print(f"{count:8d}  {name}:{line}  [{filename}]")
    print("\nObserved call segments (completion order; nested children usually appear before parents):")
    for filename, name, elapsed, depth, parent_name in timings:
        parent = f" parent={parent_name}" if parent_name else ""
        print(f"{'  ' * depth}{elapsed / 1e6:9.3f} ms  {name}{parent}  [{filename}]")
    print("\nLongest observed execution segments (inclusive; includes callback/runtime effects):")
    for filename, name, elapsed, depth, parent_name in sorted(timings, key=lambda row: row[2], reverse=True)[:20]:
        print(f"{elapsed / 1e6:10.3f} ms  depth={depth}  {name}  [{filename}]")
    print("\nCaveat: timings are instrumented inclusive segments, not a calibrated production profile.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
```

### Run it

```bash
python mini_trace.py path/to/script.py arg1 arg2
python mini_trace.py --only-package requests path/to/script.py
```

`--only-package` resolves an import package to filesystem roots and filters code objects by filename. The default filter includes only the target script itself; `--only-package` instead selects code under the resolved package roots. This is a practical approximation, not a complete module identity system: editable installs, generated code, zip imports, namespace packages, and custom loaders may need extra handling.

The call tree is approximated by per-thread stacks. Timings are **inclusive execution segments** from start/resume to return/yield/unwind, not self-time. Generator yields split the time into segments. Callback events and other tools can perturb timing. The elapsed time shown is not an overhead estimate because there is no uninstrumented baseline in that run. Use the companion benchmark in Section 5 for a controlled report. The example is intentionally explicit about these limits instead of pretending a small script is a production-grade profiler.

**Failure handling note:** cleanup disables events and unregisters callbacks even if the target script exits with `SystemExit`. Unexpected exceptions propagate after `finally` cleanup, so the CLI may not print its report on such a failure. For a production CLI, catch the exception only after recording a sanitized traceback, preserve the original exit semantics, and make cleanup best-effort without masking the primary exception.

---

## 4. Testing monitoring tools correctly

A tracer is itself software and needs tests. Do not assert a complete event sequence for a large real program: event order can legitimately change with version and bytecode layout. Start with small deterministic functions and test the property you actually need.

### 4.1 Event sequence test

This test records selected events for a simple function and checks semantic facts rather than brittle exact offsets.

```python
# test_monitoring_events.py — run with CPython 3.12+
import sys

if not hasattr(sys, "monitoring"):
    raise RuntimeError("requires CPython 3.12+")

mon = sys.monitoring
TOOL_ID = 3
events_seen = []

def target(value):
    if value:
        return value + 1
    return 0

def on_start(code, offset):
    if code is target.__code__:
        events_seen.append(("start", code.co_qualname))

def on_line(code, line_number):
    if code is target.__code__:
        events_seen.append(("line", line_number))

claimed = False
try:
    if mon.get_tool(TOOL_ID) is not None:
        raise RuntimeError("choose a free monitoring tool ID")
    mon.use_tool_id(TOOL_ID, "event-test")
    claimed = True
    mon.register_callback(TOOL_ID, mon.events.PY_START, on_start)
    mon.register_callback(TOOL_ID, mon.events.LINE, on_line)
    mon.set_events(TOOL_ID, mon.events.PY_START | mon.events.LINE)
    assert target(1) == 2
finally:
    if claimed:
        try:
            mon.set_events(TOOL_ID, 0)
        finally:
            try:
                mon.register_callback(TOOL_ID, mon.events.PY_START, None)
            finally:
                try:
                    mon.register_callback(TOOL_ID, mon.events.LINE, None)
                finally:
                    mon.free_tool_id(TOOL_ID)

assert any(event[0] == "start" for event in events_seen)
assert any(event[0] == "line" for event in events_seen)
print("monitoring event smoke test passed")
```

The assertions verify that the selected function produced start and line events. They do not prove that every source line, branch, exception, or generator transition is covered correctly. Add dedicated tests for each feature your tool claims to support.

### 4.2 Coverage correctness properties

For a line-coverage tool, useful tests include:

- Every reported line belongs to a source line that can be mapped to the measured code object.
- A line is reported only if execution reached it.
- An unexecuted conditional branch is not reported as taken.
- Repeated execution does not change a first-hit coverage set after the first hit.
- Instrumentation cleanup leaves `mon.get_events(tool_id)` unavailable only after the ID has been released, and does not leave callbacks registered for the freed ID.

A simple property is `executed_lines ⊆ executable_lines`. Computing `executable_lines` correctly is nontrivial: comments, blank lines, multiline expressions, decorators, generated code, and optimized bytecode complicate the mapping. Use the implementation of a mature coverage tool as a reference rather than treating `co_firstlineno` and `LINE` events as a complete coverage algorithm.

### 4.3 Callback exceptions and reentrancy

Keep callbacks small, deterministic, and defensive. Avoid doing network I/O, blocking logging, expensive formatting, or importing large modules inside an event callback. Buffer minimal records and process them after instrumentation is disabled where feasible. A callback exception can disrupt the program being observed; it is not a harmless logging failure.

Monitoring callbacks and their callees are not reported back to the same tool in the same way as ordinary target execution, which helps prevent self-instrumentation. Other tools may still see callback execution. Avoid designs that assume callback code is invisible to every observer.

Always clean up with `try/finally`. For a tool using local events, track every code object whose local mask it changed and clear those masks before freeing the ID. Do not rely on `free_tool_id()` to clean up other state.

---

## 5. Fair performance comparisons: `settrace`, `sys.monitoring`, and `cProfile`

`sys.settrace()` is a flexible legacy hook, `sys.monitoring` is a selective event API, and `cProfile` is a C-implemented deterministic profiler. They answer overlapping but different questions. A line tracer, a call counter, and a call-time profiler do not do equal work, so do not compare their raw times as if they were interchangeable modes.

Use a benchmark script that measures the same workload repeatedly, for example:

```python
# benchmark_workload.py

def workload(rounds=20_000):
    total = 0
    for value in range(rounds):
        total += (value % 7) * (value % 11)
    return total
```

Then compare in separate processes, so profiler state from one mode does not leak into another. For a baseline, run:

```bash
python -m timeit -s 'from benchmark_workload import workload' 'workload()'
```

For a reproducible **overhead report against `settrace`**, save the following companion benchmark as `compare_monitoring_overhead.py`. It runs each mode in a fresh subprocess, warms the same deterministic workload, times only the workload, repeats the measurements, and reports medians and slowdowns. It compares equivalent line-hit callbacks—not a printing tracer against an integer counter. This is still a microbenchmark; it does not predict application or I/O-bound performance.

```python
# compare_monitoring_overhead.py — CPython 3.12+
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path


def workload(rounds: int = 100_000) -> int:
    total = 0
    for value in range(rounds):
        total += (value % 7) * (value % 11)
    return total


def child(mode: str, rounds: int) -> None:
    hits = [0]
    old_trace = None
    mon = getattr(sys, "monitoring", None)
    tool_id = None
    claimed = False
    local_events_set = False

    def trace(frame, event, arg):
        if frame.f_code is workload.__code__:
            if event == "line":
                hits[0] += 1
            return trace
        return None

    def on_line(code, line_number):
        hits[0] += 1
        return None

    try:
        if mode == "settrace":
            old_trace = sys.gettrace()
            sys.settrace(trace)
        elif mode == "monitoring":
            if mon is None:
                raise RuntimeError("sys.monitoring requires CPython 3.12+")
            for candidate in range(6):
                if mon.get_tool(candidate) is None:
                    tool_id = candidate
                    break
            if tool_id is None:
                raise RuntimeError("no free sys.monitoring tool ID")
            mon.use_tool_id(tool_id, "overhead-benchmark")
            claimed = True
            mon.register_callback(tool_id, mon.events.LINE, on_line)
            mon.set_local_events(tool_id, workload.__code__, mon.events.LINE)
            local_events_set = True
        elif mode != "baseline":
            raise ValueError(mode)

        # Warm up under the selected mode; don't include warm-up in the timing.
        workload(rounds)
        hits[0] = 0
        started = time.perf_counter_ns()
        result = workload(rounds)
        elapsed = time.perf_counter_ns() - started
        print(json.dumps({"mode": mode, "elapsed_ns": elapsed,
                          "line_events": hits[0], "result": result}))
    finally:
        if mode == "settrace":
            sys.settrace(old_trace)
        if claimed:
            # Explicit cleanup works across CPython 3.12–3.14.
            try:
                mon.set_events(tool_id, 0)
            finally:
                try:
                    if local_events_set:
                        mon.set_local_events(tool_id, workload.__code__, 0)
                finally:
                    try:
                        mon.register_callback(tool_id, mon.events.LINE, None)
                    finally:
                        mon.free_tool_id(tool_id)


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--child":
        child(sys.argv[2], int(sys.argv[3]))
        return 0

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5, help="fresh-process runs per mode")
    parser.add_argument("--rounds", type=int, default=100_000)
    args = parser.parse_args()
    if args.runs < 3 or args.rounds < 1:
        parser.error("use at least 3 runs and a positive --rounds value")

    samples: dict[str, list[float]] = {name: [] for name in ("baseline", "settrace", "monitoring")}
    expected_result = None
    for _ in range(args.runs):
        # Rotate order to reduce systematic bias from running one mode first.
        for mode in ("baseline", "settrace", "monitoring"):
            completed = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--child", mode, str(args.rounds)],
                check=True, capture_output=True, text=True,
            )
            record = json.loads(completed.stdout)
            samples[mode].append(record["elapsed_ns"] / 1e6)
            if expected_result is None:
                expected_result = record["result"]
            elif record["result"] != expected_result:
                raise RuntimeError("workload result differed between modes")

    medians = {mode: statistics.median(values) for mode, values in samples.items()}
    baseline = medians["baseline"]
    print(f"CPython: {sys.version.split()[0]} | rounds={args.rounds} | runs={args.runs}")
    print("mode         median_ms   slowdown_vs_baseline")
    for mode in ("baseline", "settrace", "monitoring"):
        slowdown = medians[mode] / baseline if baseline else float("nan")
        print(f"{mode:11s} {medians[mode]:9.3f}   {slowdown:8.2f}x")
    print(f"workload result: {expected_result}")
    print("Interpret only this workload and build; repeat on the target interpreter and host.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Run it with:

```bash
python compare_monitoring_overhead.py --runs 7 --rounds 100000
```

The report compares medians of timed workload regions; interpreter startup and module import happen outside those regions. It warms each mode separately, which is important because instrumentation and adaptive specialization can affect one another. Run on the same machine with low background load, preserve the printed interpreter version and arguments, and do not treat one microbenchmark as a universal ranking. The monitoring benchmark deliberately uses a local `LINE` event on `workload.__code__`, while `settrace` filters to the same code object. That is a fairer comparison than enabling all events for one mode and only a subset for the other.

For `cProfile`, use a short wrapper script:

```python
# run_cprofile.py
import cProfile
from benchmark_workload import workload
cProfile.run("workload()", sort="cumulative")
```

Run `python run_cprofile.py` separately from the baseline. To compare `settrace` and `sys.monitoring`, make a harness with three modes that all call `workload()` and keep callback work minimal. Record at least five runs, compare medians, and record interpreter version, build, OS, workload parameters, and whether warm-up was performed. Include a baseline with no instrumentation.

| Tool/mode | Strength | Typical limitation |
|---|---|---|
| `sys.settrace` | Fine-grained source-line and debugger protocol | Often high overhead; one trace function slot per thread |
| `sys.setprofile` | Function/C-call events | Not line/branch coverage; callback overhead remains |
| `sys.monitoring` | Selective events, local masks, disable-on-hit | CPython 3.12+ only; tool lifecycle and version differences matter |
| `cProfile` | Mature deterministic call profiling with C implementation | Profiling changes timing; not source-line coverage or sampling |
| Sampling profiler (for example, `py-spy`) | Low-overhead statistical view of stacks | Samples can miss short functions and need attach permissions |

Do not claim `sys.monitoring` is always faster by a fixed factor. It can be much cheaper when the event set is narrow and events are disabled once no longer useful; a callback that does heavy work can still dominate runtime.

---

## 6. Advanced tool design

### 6.1 Function timing and inclusive versus exclusive time

A minimal timer records a start timestamp at `PY_START` (and `PY_RESUME` for suspended functions), then calculates elapsed time at `PY_RETURN`, `PY_YIELD`, or `PY_UNWIND`. That elapsed interval is **inclusive**: it includes time spent in child calls and often includes waiting performed by the function. To compute exclusive/self time, maintain a stack and subtract the elapsed time of nested frames. That becomes more complex with generators, exceptions, threads, async tasks, and callbacks.

Use `time.perf_counter_ns()` for monotonic high-resolution elapsed-time measurements. Never interpret wall-clock duration as CPU time. A function waiting on a socket may have a long inclusive duration but consume little CPU.

### 6.2 Generators and coroutines

A generator function call usually creates a generator object; the body executes later. Therefore “call count” needs a definition. `PY_START`/`PY_RESUME`/`PY_YIELD` can help separate first execution from subsequent resumptions. If a tool reports one function duration from initial start until final return, it may include hours of suspension; many profilers instead report active execution segments. Document which definition you use.

Async tasks can interleave on one OS thread. A simple thread-local call stack is not necessarily an async-task stack: when a coroutine suspends, another task can run on the same thread. A production async profiler needs task-aware context tracking and careful handling of resume/yield transitions.

### 6.3 Debugger breakpoints and stepping

A debugger can use `LINE` events to implement line breakpoints and disable events at locations without breakpoints. Stepping into/over functions requires tracking function start/return and control-flow transitions. This is why an event system with selective enabling can reduce overhead compared with tracing every line unconditionally.

In **Python 3.14**, `pdb` supports `settrace` and `monitoring` backends. `Pdb` instances default to the `settrace` backend unless configured otherwise; the `pdb` CLI, `breakpoint()`, and `pdb.set_trace()` use the monitoring backend. This is a 3.14-specific behaviour. Check the [3.14 `pdb` documentation](https://docs.python.org/3.14/library/pdb.html) and [`bdb` documentation](https://docs.python.org/3.14/library/bdb.html) for the exact interface. Do not assume this behaviour exists in Python 3.12 or 3.13.

IDE debuggers such as `debugpy` have their own compatibility and tracing strategies. Avoid running multiple debuggers/profilers that compete for legacy hooks unless you understand their interaction. Monitoring tool IDs improve coexistence, but they do not guarantee that every third-party tool is compatible.

### 6.4 Specializing interpreter and JIT interaction

CPython's adaptive specializing interpreter can specialize instructions based on observed execution. Monitoring may require instrumented instruction paths or change optimization opportunities, so an instrumented run may not behave like an uninstrumented performance run. CPython 3.14's JIT is build- and configuration-dependent and remains experimental; do not claim that every monitoring event universally disables the entire JIT. Verify the exact build, event set, and release notes, then benchmark both instrumented and uninstrumented cases.

Useful source-reading locations in the CPython repository include:

- `Python/instrumentation.c` — implementation of instrumentation machinery in relevant CPython versions.
- `Lib/bdb.py` — debugger framework and backend integration.
- `Lib/pdb.py` — command-line/source debugger.
- `Lib/trace.py` — standard-library tracing and coverage-style functionality.

These are implementation details, not stable public API contracts. Source organization can change between branches; inspect the tag corresponding to the interpreter version being studied.

### 6.5 Coverage tools and `COVERAGE_CORE=sysmon`

The coverage.py project offers a `sysmon` core on compatible Python versions. The important design idea is that line/branch events can often be disabled after a location's first hit, reducing repeat event overhead. Do not assume the environment variable or core name is supported by every coverage.py release; check that release's documentation and changelog. Compare results with a known test suite before adopting it in CI.

### 6.6 APM auto-instrumentation versus interpreter monitoring

OpenTelemetry/APM agents often instrument libraries by monkey-patching functions (wrapping a database client, HTTP client, or framework call) to capture spans, attributes, and context propagation. `sys.monitoring` instead observes interpreter-level events. These approaches solve different problems:

- Monkey-patching knows library-specific semantics and can capture request IDs, URL routes, database operations, and span boundaries. It can break when library internals change and may miss unwrapped calls.
- Interpreter monitoring can see broad Python execution events without wrapping every library function, but an event like `CALL` alone does not tell you that a call is an HTTP request or which business operation it represents.
- Both approaches add overhead and can interact. APM tools may use context propagation and wrappers; a monitoring tool may observe wrapper code too unless filtered.

Use the most semantic instrumentation point available for distributed tracing; use interpreter hooks for runtime-wide diagnostics, coverage, profiling, and tool development. Avoid collecting argument values or local variables by default: they may contain credentials or personal data.

### 6.7 Audit hooks and `faulthandler` are complementary, not a sandbox

`sys.addaudithook()` registers audit hooks for supported runtime events, and `sys.audit()` emits events. Audit hooks are intended for observability and security auditing, but they do not make arbitrary Python code safe and are not a complete policy-enforcement boundary. Event coverage depends on the operation and runtime; an audit hook cannot be assumed to see every possible native action.

`faulthandler` is useful for traceback dumps on fatal faults or on request/timeout where supported. It complements event-based tracing: a traceback snapshot can show where threads are currently blocked even if a tracing tool is not active. `sys.unraisablehook` can help surface exceptions that cannot be propagated normally. These tools are diagnostics, not substitutes for correct synchronization, least privilege, or process isolation.

A security-oriented monitoring callback that watches calls to `eval`, `exec`, `os.system`, or `subprocess` can be useful for telemetry, but it is not a sandbox. Calls may be aliased, indirect, native, or reached through paths not covered by the selected events. Do not use an in-process Python hook as the only boundary for hostile code.

---

## 7. Common failure modes and troubleshooting

### “The program became much slower after I enabled tracing.”

1. Check whether `sys.gettrace()` or `sys.getprofile()` returns a hook unexpectedly.
2. Check whether a tool enabled `LINE` or `INSTRUCTION` globally when it needed only calls or selected code objects.
3. Confirm that callbacks do not print, log synchronously, perform network I/O, or allocate large data structures on every event.
4. Confirm all hooks and event masks are disabled in `finally` blocks.
5. Reproduce with a narrow event set and compare to an uninstrumented baseline.

### “My monitoring tool conflicts with a debugger or coverage.”

- Check `sys.monitoring.get_tool(id)` before claiming a tool ID.
- Do not unregister another tool's callback or call `free_tool_id()` for an ID you did not claim.
- Keep each tool's event mask narrow and document shared `restart_events()` behaviour.
- With legacy hooks, only one trace function and one profile function can be active per thread at a time; installing yours may replace a debugger's hook.

### “The call count seems wrong.”

Decide whether you are counting Python function starts, calls to C callables, generator creation, generator execution segments, or unique functions. `PY_START` is not a universal count of all calls. Add `CALL`/`C_RETURN`/`C_RAISE` when you need call-site or C-call observations, and account for their event-group semantics.

### “Coverage misses a branch or reports an unexpected line.”

Check whether the tool uses the correct branch event for that interpreter: `BRANCH` in 3.12–3.13; in 3.14, `BRANCH` remains available but is deprecated, and `BRANCH_LEFT`/`BRANCH_RIGHT` are preferred because each direction can be disabled independently. Inspect the source mapping and test compound conditions, exceptions, comprehensions, and generator code. A `LINE` event is not by itself a complete branch-coverage algorithm.

### “Timings are confusing.”

Check whether the measurement is inclusive or exclusive, whether callbacks are included, whether generators yielded, and whether the code waited on I/O. Repeat measurements and compare with sampling or OS-level evidence for production workloads.

---

## 8. Practical experiments

Perform these in a disposable virtual environment, not in a latency-sensitive production process.

### Experiment A — Observe legacy line events

- **Question:** Which source-line transitions occur when a small function runs?
- **Setup/command:** Save the `legacy_line_trace.py` example above; run `python legacy_line_trace.py`.
- **Procedure:** Add one conditional and one loop. Compare the printed line sequence for `work()`.
- **Expected observations:** Executed source lines appear as `function_name:line_number`; a loop body line may appear repeatedly.
- **Interpretation:** Trace events expose control flow at source-line granularity.
- **Does not prove:** It does not report every expression, bytecode instruction, native operation, or line that could execute on a different input.

### Experiment B — Compare monitoring first-hit and repeated events

- **Question:** What changes when the callback returns `DISABLE`?
- **Setup/command:** Run `monitoring_line_hits.py` on CPython 3.12+.
- **Procedure:** Change the callback to return `None`, rerun, and compare how often the loop's line events are recorded. Keep the same workload.
- **Expected observations:** Without `DISABLE`, repeated visits to active line locations can be recorded; with it, each location normally records only its first event until events are restarted.
- **Interpretation:** Per-location disabling is valuable for first-hit coverage.
- **Does not prove:** It does not prove a complete coverage implementation or establish a universal speedup factor.

### Experiment C — Measure overhead fairly

- **Question:** How much does each instrumentation mode cost for this workload?
- **Setup/command:** Use `benchmark_workload.py`, `run_cprofile.py`, and a small harness for baseline, `settrace`, and monitoring modes.
- **Procedure:** Run each mode in a separate process at least five times. Do not print events in the timed loop. Record the Python version/build and compare medians.
- **Expected observations:** Instrumented modes usually cost more than baseline; relative rankings depend on event set and callback implementation.
- **Interpretation:** Measurement should guide event selection for your workload.
- **Does not prove:** A synthetic CPU loop does not predict production web-service overhead or I/O-bound latency.

### Experiment D — Test cleanup after failure

- **Question:** Does an exception in the target workload leave monitoring active?
- **Setup/command:** Modify the call-counter workload to raise `RuntimeError`, catch it outside the instrumented region, and run again with a free tool ID.
- **Procedure:** Ensure the monitoring code's `finally` block executes. In a separate check, verify `get_tool(TOOL_ID)` returns `None` after cleanup and that the next run can claim the ID.
- **Expected observations:** The original exception propagates or is handled by the surrounding harness, but the monitoring ID is released.
- **Interpretation:** Cleanup must be tested on both success and failure paths.
- **Does not prove:** It does not prove that all possible failures during cleanup are harmless; robust tools must avoid masking the primary failure if cleanup itself raises.

### Experiment E — Compare Python and C call visibility

- **Question:** Does `PY_START` count built-in calls such as `sum()`?
- **Setup/command:** Extend the call-counter example to call both a Python function and `sum()`.
- **Procedure:** Compare `PY_START` counts with `CALL` events and, where enabled, `C_RETURN`/`C_RAISE`.
- **Expected observations:** `PY_START` is about Python function execution; C-level callables are observed through the appropriate call event group rather than as Python function starts.
- **Interpretation:** Event choice defines what “call count” means.
- **Does not prove:** It does not guarantee visibility into every native operation or call made inside an extension module.

---

## 9. Self-check questions and answers

### 1. Why can `sys.monitoring` disable events per location, and why can that make coverage faster?

**Answer:** `DISABLE` suppresses future delivery of that event for a particular code location until events are restarted. A first-hit coverage tool usually gains no additional line-coverage information from repeated visits to the same location, so disabling after the first hit reduces callback work. It is location-specific, not a global event shutdown, and `restart_events()` can re-enable disabled locations for all tools.

### 2. What are tool IDs, and why do they let a debugger and profiler coexist?

**Answer:** A tool ID identifies a monitoring client and its callbacks/event mask. Different clients can use different IDs and enable different events, unlike the legacy model where a new `sys.settrace()` call replaces the current trace function for that thread. IDs must be claimed and released carefully; they do not isolate tools or guarantee compatibility.

### 3. Build the mini call-counter profiler and compare overhead against `cProfile` on the same workload.

**Answer outline:** Use the call-counter example with a free monitoring ID and guaranteed cleanup. Run a deterministic workload with no instrumentation, with the monitoring call counter, and under `cProfile` in separate processes. Repeat runs, compare medians, record interpreter/build and workload parameters, and keep output outside the timed region. Interpret results as workload-specific because the tools collect different event data and impose different callback costs.

### 4. Why is `sys.settrace()` described as single-client and comparatively expensive?

**Answer:** It has a single active trace function slot per thread, and line tracing invokes Python callback code frequently. A debugger and another tracer can replace each other's hook unless they explicitly cooperate. `sys.monitoring` provides multiple tool IDs and selective event masks, but it still has overhead.

### 5. Why are `PY_START`, `PY_RESUME`, `PY_RETURN`, and `PY_YIELD` not interchangeable?

**Answer:** They describe different execution transitions. A generator/coroutine can be created before its body runs, then start, yield, resume, and finally return. Counting only starts misses resumption segments; timing from start to final return may include suspension time. A tool must define whether it counts invocations, resumptions, or active execution segments.

### 6. What should a tracer do if the target raises an exception?

**Answer:** Use `try/finally` to disable events, clear local masks that the tool set, unregister its callbacks, and free only the ID it claimed. Then preserve the target's exception/exit semantics. Cleanup itself should be best-effort and should not silently replace the primary error.

### 7. Why is an interpreter monitoring hook not a security sandbox?

**Answer:** It observes selected interpreter events inside the same process. It can miss operations outside the selected events, indirect/native actions, or paths not covered by the hook. The code being monitored can also affect the process. Use OS/process isolation and a defined security boundary for hostile code.

### 8. How do `sys.monitoring`, APM monkey-patching, audit hooks, and `faulthandler` differ?

**Answer:** Monitoring sees interpreter execution events; monkey-patching wraps selected library functions and can add domain-specific context; audit hooks expose supported runtime audit events; `faulthandler` produces diagnostic traceback dumps. They complement one another but have different coverage, overhead, and semantic information.

---

## 10. Concise summary

- `sys.settrace()` is useful for classic line-level tracing and debugging, but it has a single trace-function slot per thread and can be expensive.
- `sys.setprofile()` focuses on call/return events, including C-level callables.
- CPython 3.12+ `sys.monitoring` (PEP 669) provides tool IDs, event masks, callbacks, local code-object events, and location-specific `DISABLE`.
- Choose the smallest event set that answers the question. Define whether you measure calls, starts, resumptions, line hits, branches, inclusive time, or exclusive time.
- Clean up event masks and callbacks even on failure; `free_tool_id()` alone is not cleanup.
- Test event semantics and coverage correctness on small deterministic programs. Benchmark against an uninstrumented baseline and compare equivalent work.
- Monitoring, APM wrappers, audit hooks, and fault handlers are observability tools—not security boundaries.

## Official references and source-reading guide

- [PEP 669 — Low Impact Monitoring for CPython](https://peps.python.org/pep-0669/)
- [Python 3.12 `sys.monitoring`](https://docs.python.org/3.12/library/sys.monitoring.html)
- [Python 3.13 `sys.monitoring`](https://docs.python.org/3.13/library/sys.monitoring.html)
- [Python 3.14 `sys.monitoring`](https://docs.python.org/3.14/library/sys.monitoring.html)
- [What’s New in Python 3.14 — monitoring and debugger changes](https://docs.python.org/3.14/whatsnew/3.14.html)
- [`sys.settrace` and `sys.setprofile`](https://docs.python.org/3/library/sys.html#sys.settrace)
- [`threading` tracing APIs](https://docs.python.org/3/library/threading.html#threading.settrace)
- [Python 3.14 `pdb`](https://docs.python.org/3.14/library/pdb.html)
- [Python 3.14 `bdb`](https://docs.python.org/3.14/library/bdb.html)
- [CPython source repository](https://github.com/python/cpython): inspect `Lib/bdb.py`, `Lib/pdb.py`, `Lib/trace.py`, and `Python/instrumentation.c` at the tag matching your interpreter.
- [coverage.py documentation](https://coverage.readthedocs.io/): check the documentation for the installed release before selecting a monitoring core.

The APIs and implementation details in this lesson are version-sensitive. Verify them against the exact CPython release and third-party tool versions used in your project.
