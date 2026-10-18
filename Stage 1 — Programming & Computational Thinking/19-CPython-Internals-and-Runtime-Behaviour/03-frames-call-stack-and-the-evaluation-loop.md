# Frames, Call Stack, and the Evaluation Loop

> **Target:** CPython 3.12–3.14  
> **Version discipline:** Examples target CPython 3.12+. Private evaluator/frame details vary by release and build. Record `python --version` before comparing observations. Python language semantics are distinguished from CPython implementation details throughout.

## Learning outcomes

By the end of this lesson, you should be able to:

1. Explain the relationship between a code object, an executing frame, a call-stack chain, and a traceback.
2. Inspect caller frames with `sys._getframe()` and `inspect`, and interpret `f_code`, `f_back`, `f_lineno`, `f_globals`, and `f_locals`.
3. Explain `RecursionError`, the recursion limit, why CPython does not eliminate tail calls, and why Python recursion depth is not the same as C-stack depth.
4. Describe CPython 3.11+ interpreter frames, on-demand `PyFrameObject` materialisation, the evaluation loop, and the eval breaker without treating private details as stable contracts.
5. Inspect suspended generators, understand `send()`, `close()`, and `GeneratorExit`, and distinguish coroutine execution from event-loop scheduling.
6. Explain exception unwinding, traceback links, exception chaining, and frame/traceback retention.
7. Understand the Python 3.13 `locals()` and `frame.f_locals` changes introduced by PEP 667.
8. Use tracing and thread-stack capture while avoiding excessive overhead, sensitive-data exposure, and frame-retention leaks.
9. Complete the line-tracer and recursion-guard exercises and answer the self-checks.

## Prerequisites

You should know how to define and call functions, use local/global variables, handle exceptions, write a generator with `yield`, and distinguish a process from a thread. Code objects and bytecode from the previous lessons are helpful but not required. Useful tools include CPython 3.12, 3.13, or 3.14; `sys`, `inspect`, `traceback`, `dis`, `faulthandler`, `threading`, `asyncio`, and optionally a sampling profiler such as `py-spy`.

## 1. Mental model: code is a recipe; a frame is one execution

A **code object** describes compiled code. It contains information such as bytecode, constants, names, variable names, flags, and source-location tables. It does not represent one particular invocation of a function.

A **frame** is the execution record for one active or suspended code execution. Conceptually, it connects the code object to execution state: local bindings, instruction position, evaluation/value stack, globals, builtins, and the previous frame in the call chain.

A **call stack** is the chain of frames that explains how the current execution reached its present point. When an exception propagates, a **traceback** records frame/line information along the path of propagation.

```text
compiled function
   └── code object (shared recipe)
          │ called
          ▼
      frame for call A ──f_back──> caller frame ──f_back──> ...
          │
          ├── current instruction / execution state
          ├── local and closure bindings
          └── globals / builtins references

exception propagation:
traceback node (frame, line) ──tb_next──> next traceback node
```

This is a conceptual model, not a promise about CPython's physical memory layout. In CPython 3.11 and later, an internal interpreter frame can exist without a separately allocated public Python frame object.

### Why the model matters

- **Debugging:** a traceback is a route through calls, not just a list of source lines.
- **Profiling:** profilers attribute work to functions and call paths.
- **Recursion:** nested calls require execution state; uncontrolled recursion can exhaust a limit.
- **Generators/coroutines:** suspended execution retains enough state to resume later.
- **Memory diagnosis:** a retained frame can retain its locals, and those locals can retain large object graphs.

### Code object versus call frames

```python
def square(value):
    return value * value

print(square.__code__.co_name)
print(square.__code__.co_varnames)
print(square(3))
print(square(5))
```

Representative output:

```text
square
('value',)
9
25
```

`square.__code__` is the compiled code object associated with the function. Calling `square` twice executes that code twice with different argument values. The function object, code object, and each invocation's execution state are distinct concepts.

**This does not prove:** the public Python API does not expose the full internal frame layout or guarantee that each call allocates a particular C structure.

## 2. Inspecting frames from Python

### 2.1 `sys._getframe()`

`sys._getframe([depth])` returns a frame object from the current thread's call stack. Depth `0` means the current frame; depth `1` means its caller. It is explicitly a CPython-oriented, implementation-specific API and may not exist on every Python implementation. Access can raise an auditing event. Use it for focused diagnostics and debugging tools—not as a routine dependency in business logic.

```python
import sys

def inspect_caller():
    # depth=1 asks for this function's caller.
    frame = sys._getframe(1)
    print("function:", frame.f_code.co_name)
    print("line:", frame.f_lineno)
    print("local names:", sorted(frame.f_locals))

def outer():
    customer_id = "C-104"
    inspect_caller()

outer()
```

Representative output (the line number depends on where the code is saved):

```text
function: outer
line: <line where inspect_caller() is called>
local names: ['customer_id']
```

The key point is that the frame identifies the caller's code object and currently visible local bindings.

### 2.2 `inspect.currentframe()` and `inspect.stack()`

- `inspect.currentframe()` returns the current frame, if the implementation supports frame inspection; it may return `None`.
- `inspect.stack()` returns richer stack records including frame objects and source context where available. It has a cost: it may read source files and holds references to frames and their locals.
- `frame.f_back` links to the caller frame when available.
- `frame.f_code` is the code object executing in the frame.
- `frame.f_lineno` is the current line reported for the frame.
- `frame.f_globals` is the global namespace mapping.
- `frame.f_locals` exposes the frame's local namespace; its behaviour in optimised function scopes is version-sensitive (Section 9).

A smaller stack summary is often better than retaining `inspect.stack()` results:

```python
import sys

def stack_summary(limit=8):
    """Return names/lines only; do not return frame objects."""
    result = []
    frame = sys._getframe(1)  # caller of stack_summary
    try:
        while frame is not None and len(result) < limit:
            result.append((frame.f_code.co_name, frame.f_lineno))
            frame = frame.f_back
    finally:
        # Break our local reference to the last frame.
        del frame
    return result

def parse_record():
    return stack_summary()

print(parse_record())
```

Output shape (line numbers vary):

```text
[('parse_record', ...), ('<module>', ...)]
```

The returned list contains only strings/integers, not frames. This greatly reduces the chance that the diagnostic result itself keeps a stack and its locals alive.

### When frame inspection is useful

- Adding a caller name to a low-level diagnostic.
- Building a debugger, coverage tool, profiler, or structured traceback formatter.
- Capturing thread stacks during a hang.
- Investigating a recursion path.

### Trade-offs and safety

Frame inspection can be expensive, implementation-specific, and privacy-sensitive. Locals may contain credentials, tokens, personal data, database connections, or large caches. Avoid dumping `f_locals` into production logs. Prefer a short allowlisted summary and redact data before it leaves the process.

Do not use frame introspection as a substitute for explicit dependency passing. Code that depends on a caller's name or local variables is harder to refactor and test.

## 3. The call stack and tracebacks

A traceback is not identical to the live call stack. A live stack describes execution now. A traceback describes frames and source lines associated with an exception as it propagates, and it can be retained after propagation.

The traceback API exposes:
- `tb_frame`: frame associated with this traceback node.
- `tb_lineno`: source line associated with the node.
- `tb_next`: next traceback node in the chain.

The direction of traceback display and the order of `tb_next` traversal can be easy to confuse. Walk it and print the fields rather than assuming a visual order.

```python
import traceback

def divide():
    numerator = 10
    denominator = 0
    return numerator / denominator

try:
    divide()
except ZeroDivisionError as exc:
    tb = exc.__traceback__
    while tb is not None:
        print(tb.tb_frame.f_code.co_name, tb.tb_lineno)
        tb = tb.tb_next
    print("".join(traceback.format_exception(exc)), end="")
```

Representative output begins with frame/line pairs for the module and `divide`, followed by a `ZeroDivisionError` traceback. Exact line numbers and formatting depend on the file and Python version.

### Exception chaining

Python preserves context when one exception is raised while handling another:

```python
def load_config():
    try:
        int("not-an-integer")
    except ValueError as exc:
        raise RuntimeError("configuration value is invalid") from exc

try:
    load_config()
except RuntimeError as exc:
    print(type(exc).__name__)
    print(type(exc.__cause__).__name__)
```

Output:

```text
RuntimeError
ValueError
```

- `__cause__` is set explicitly by `raise NewError from old_error`.
- `__context__` records an exception being handled when another exception is raised.
- `raise ... from None` suppresses display of the implicit context; it does not mean the earlier event never happened.

### What exception unwinding does

When an exception is raised, the interpreter searches for a handler. If the current frame cannot handle it, execution leaves that frame and propagation continues toward a caller. CPython's compiled exception-handling metadata tells the evaluator where protected regions and handlers are. Since CPython 3.11, exception tables replaced many older bytecode setup instructions for `try`/`finally` handling; exact bytecode and evaluator mechanics are version-dependent.

A traceback records frames/lines associated with propagation. It is not a complete history of every statement that executed.

**Production example:** when a request handler raises inside a service layer, a traceback shows the path from the request entry point to the failing operation. Preserve exception chaining when adding domain context so operators can see both the user-facing failure and the original cause.

## 4. Recursion, `RecursionError`, and tail calls

### 4.1 Why recursion has a limit

Each recursive call needs execution state. A limit prevents unbounded recursive calls from continuing indefinitely. Python exposes:

```python
import sys
print(sys.getrecursionlimit())
```

The numeric value is interpreter configuration, not a universal constant. It can differ by environment and version.

`sys.setrecursionlimit(limit)` changes the interpreter's recursion limit. Setting it too low can make otherwise valid code fail. Setting it extremely high can risk a crash, especially when native C code or extension modules consume C stack. Do not treat increasing the limit as a general fix.

```python
def countdown(n):
    if n <= 0:
        return 0
    return countdown(n - 1)

try:
    countdown(100_000)
except RecursionError as exc:
    print(type(exc).__name__)
```

Representative output:

```text
RecursionError
```

The exact depth at which it occurs is intentionally not specified here; it depends on the configured limit, call path, and interpreter version.

### 4.2 Why CPython does not perform tail-call elimination

A tail call occurs when a function's final action is to return the result of another call:

```python
def factorial_tail(n, accumulator=1):
    if n <= 1:
        return accumulator
    return factorial_tail(n - 1, accumulator * n)
```

A compiler could theoretically reuse the current activation instead of keeping another one. CPython does not generally perform tail-call elimination for Python function calls. This preserves ordinary call structure and useful traceback/debugging information, and avoids making call visibility depend on whether an expression happens to be in tail position. The absence of tail-call elimination is a CPython design/implementation choice, not a universal requirement that every Python implementation must follow.

For input sizes that can be large, use an iterative algorithm or an explicit stack when appropriate:

```python
def factorial_iterative(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for value in range(2, n + 1):
        result *= value
    return result

print(factorial_iterative(5))
```

Output:

```text
120
```

Do not mechanically replace all recursion: recursion can make tree algorithms clearer, and not all recursion is deep. Choose based on input bounds, clarity, and measured constraints.

### 4.3 Python depth is not the same as C-stack depth

A common outdated simplification is: “Every Python call consumes one C stack frame.” CPython 3.11 changed the evaluation path so ordinary Python-to-Python calls can be handled using internal interpreter frames without recursively calling the C evaluator for each Python call. That reduced C-stack use and improved call performance.

This does **not** mean all recursion is harmless or that the recursion limit can be ignored:
- Python-level recursion checks still apply.
- Calls into C extensions, recursive C callbacks, destructors, or native libraries can consume C stack.
- Deeply nested `repr`, `json`, or `pickle` operations can encounter recursion safeguards in the relevant implementation path; do not assume their failure threshold is identical to a simple Python function's threshold.
- Recursion limits and C-stack protections have changed across CPython releases and build configurations.
- Starting with 3.12, CPython's C-recursion protection has separate implementation details from the Python recursion limit; don't infer native-stack safety from `sys.getrecursionlimit()` alone.
- CPython 3.14 removed undocumented internal recursion knobs such as `Py_C_RECURSION_LIMIT` and `PyThreadState.c_recursion_remaining`. C-extension authors should use the documented `Py_EnterRecursiveCall()` / matching exit API where appropriate, and verify the C API for their target release.

For native-extension authors, recursive entry between Python and C deserves explicit testing. A crash caused by C-stack exhaustion may terminate the process instead of raising a catchable `RecursionError`.

### 4.4 Threads and native stack

`threading.stack_size([size])` configures the stack size for subsequently created threads on platforms that support it; valid sizes are platform-dependent. On Unix-like systems, `ulimit -s` may show or configure a shell's stack limit, but its meaning depends on the OS and launch environment. Neither is a portable way to make Python recursion safe.

Operational guidance:
1. Prefer iterative algorithms for unbounded/deep inputs.
2. Validate input depth before recursive parsing or serialization.
3. Keep C-extension recursion bounded and check extension documentation.
4. Test on the actual OS, architecture, Python build, and worker configuration.
5. Do not raise recursion limits in production as a speculative performance fix.

## 5. CPython frame internals: 3.11 and later

### Public frame versus internal interpreter frame

Before CPython 3.11, the implementation model more closely associated each active execution frame with a heap-allocated `PyFrameObject`. CPython 3.11 introduced a more efficient internal representation, commonly discussed as `_PyInterpreterFrame`, which can live on an interpreter-managed data stack. A full Python-visible `PyFrameObject` is materialised when something needs to inspect the frame, such as `sys._getframe()`, traceback creation, or debugging.

Consequences:
- Ordinary calls can avoid allocating a public frame object for every invocation.
- A frame object may be created lazily when inspection requires it.
- If a public frame outlives the internal stack location, CPython must preserve the visible frame state appropriately.
- Generators and coroutines retain suspended execution state as part of their objects.

This is an implementation strategy, not a language guarantee. Exact structure and allocation strategy can change across CPython versions. In C extensions, treat `PyFrameObject` as opaque; use documented C APIs rather than reading struct fields.

### What the conceptual frame contains

| Concept | Purpose |
|---|---|
| Code object (`f_code`) | Compiled code and source metadata |
| Instruction position | Where execution is currently positioned |
| Local/fast-local storage | Arguments and local variable bindings |
| Evaluation/value stack | Temporary operands and intermediate values |
| Globals (`f_globals`) | Module namespace used for global lookup |
| Builtins | Builtins namespace used for fallback lookup |
| Back link (`f_back`) | Caller frame when available |

The exact physical layout, field names, and stack representation are private. Python's frame attributes are the supported inspection surface for Python code, with documented version differences.

### Reading implementation source

For a version-specific deep dive, browse the matching CPython tag—not `main` alone:
- `Include/internal/pycore_frame.h` — internal frame definitions (private).
- `Python/ceval.c` and/or the evaluator implementation for the target release — evaluation machinery; source organization changes.
- `Objects/frameobject.c` — Python-visible frame objects and related behavior.
- `Doc/c-api/frame.rst` — documented C API for frame objects.
- `InternalDocs/frames.md` in CPython source — design notes where present.

Names such as `_PyInterpreterFrame`, `_PyEval_EvalFrameDefault`, and evaluator dispatch machinery are internal. They are valuable for learning, but are not stable extension APIs.

## 6. The evaluation loop and the eval breaker

The evaluation loop is the machinery that executes bytecode for a code object. A useful high-level mental model is:

1. Obtain the current instruction and its operands.
2. Decode/dispatch the operation.
3. Read or update locals, the evaluation stack, and control-flow position.
4. Repeat until returning, yielding, or transferring control because of an exception or other runtime event.

This is a conceptual fetch/decode/execute model. CPython's actual evaluator is heavily optimised; bytecode dispatch, caches, superinstructions, and call paths vary by release and build.

### What is the eval breaker?

CPython uses internal checks—often described as the **eval breaker**—to notice runtime conditions that require attention at suitable points in evaluation. Depending on version and context, these can include pending signals, requests related to the GIL, pending calls, asynchronous exception requests, and other interpreter housekeeping (including work associated with garbage collection in some implementations). The eval breaker is a coordination mechanism, not a promise that every category is checked at every bytecode or that GC is always triggered through one identical path.

Do not assume every item is checked at every bytecode instruction or that internal flags and exact check points are fixed. The eval breaker is an implementation mechanism, not a Python-level API.

### CPython 3.14 note: tail-calling interpreter

CPython 3.14 includes an optional tail-calling interpreter configuration, enabled at build time with `--with-tail-call-interp`. The documented supported configuration requires Clang 19 or newer on x86-64 or AArch64; it is opt-in, and profile-guided optimization is recommended by the release notes. Availability depends on how CPython was built. This is about how the evaluator dispatches bytecode handlers internally; it is **not** the same as Python-level tail-call optimisation. It does not mean a recursive Python function suddenly reuses its caller's logical frame.

To investigate a particular build, record `sys.version`, `sys.implementation`, build configuration, and the exact release notes. Do not extrapolate timing or stack behavior from one build to another.

The roadmap also mentions `sys._is_interned`. This CPython-specific introspection function was **added in Python 3.13** (so it is present in 3.14 as well); it reports whether a string is interned. It is unrelated to tail-call elimination and is not a frame-inspection API. Like other underscored `sys` functions, it is not a portable language guarantee. Example with feature detection:

```python
import sys

check = getattr(sys, "_is_interned", None)
if check is None:
    print("string interning inspection is unavailable")
else:
    print(check("example"))
```

The boolean result depends on whether that particular string is interned in the running interpreter; do not assume a literal is interned merely because it appears in source.

### Practical interpretation

For application developers, the useful boundary is usually Python-level behavior: calls, returns, exceptions, yields, and tracebacks. For runtime engineers, inspect the matching CPython source and test a version-specific hypothesis. Do not infer production latency solely from bytecode count or from a diagram of the evaluator.

## 7. Generators: suspended frames

A generator function contains `yield`. Calling it creates a generator object; it does not immediately run the body to completion. The generator's execution state is preserved when it yields and resumed by `next()` or `send()`.

Useful attributes:
- `gi_frame`: the frame associated with the generator while it is available.
- `gi_running`: whether it is currently executing.
- `gi_code`: the generator's code object.
- `gi_yieldfrom`: delegated iterator/generator, if applicable.

After a generator finishes, `gi_frame` may be `None`; do not assume it is always a frame object.

```python
def conversation():
    received = yield "ready"
    print("received:", received)
    yield "working"

g = conversation()                 # body has not run yet
print(next(g))                     # starts and suspends at first yield
print(g.gi_frame.f_code.co_name)
print(g.gi_frame.f_locals)
print(g.send("continue"))          # resumes; value becomes result of yield
g.close()                          # injects GeneratorExit if still suspended
```

Representative output:

```text
ready
conversation
{}
received: continue
working
```

The exact local dictionary display can depend on the point of suspension and version. After the first `yield`, the assignment `received = ...` has not yet received the value sent back, so `received` may not yet appear as a bound local. The second `yield` suspends again; `close()` then requests termination.

### `send()`, `StopIteration`, and `close()`

- `next(g)` is effectively a request to resume without sending a non-`None` value.
- `g.send(value)` resumes the generator and makes `value` the result of the suspended `yield` expression. A non-`None` value cannot be sent to a generator that has not started.
- When a generator returns, iteration ends with `StopIteration`; its return value is carried by that exception's `.value`.
- `g.close()` injects `GeneratorExit` at the suspension point. A well-behaved generator normally lets it propagate or performs cleanup in `finally`. Yielding another value while closing is erroneous and can result in `RuntimeError`.

```python
def resource_like():
    try:
        yield "open"
    finally:
        print("cleanup")

g = resource_like()
print(next(g))
g.close()
```

Output:

```text
open
cleanup
```

Use `try/finally` to guarantee cleanup when a generator is closed normally. Do not rely on garbage collection timing to release resources.

### `yield from`

`yield from subgenerator` delegates iteration and, where applicable, send/throw/close behavior to the subgenerator. It can also propagate the subgenerator's return value. The exact bytecode used to implement delegation varies by Python version; reason first from the language semantics.

### Why suspended generators matter for memory

A suspended generator retains the state needed to resume. That can include locals and objects referenced by those locals. A generator waiting on a queue while holding a large batch, file handle, or request object can keep that object alive for as long as the generator remains reachable.

## 8. Coroutines and scheduling are separate concerns

Calling an `async def` function creates a coroutine object; its body runs when the coroutine is awaited or driven by an event loop. A coroutine is not automatically scheduled merely because it was created.

At a conceptual level, an event loop advances a task by stepping its coroutine (using the coroutine's `send()`/`throw()` protocol as appropriate); the coroutine may complete, raise, or suspend awaiting another operation. `await` delegates through the awaitable protocol (including `__await__` where applicable). The **interpreter** executes the currently running Python code; the **event loop** decides when a task gets another chance to run.

```python
import asyncio

async def child():
    await asyncio.sleep(0)
    return 42

async def main():
    coro = child()             # created, not yet running
    task = asyncio.create_task(coro)  # scheduled on this running loop
    result = await task
    print(result)

asyncio.run(main())
```

Output:

```text
42
```

### Common coroutine failure modes

- **“coroutine was never awaited” warning:** a coroutine object was created but neither awaited nor scheduled appropriately.
- **Blocking the event loop:** synchronous blocking work prevents other tasks on that loop from progressing.
- **Assuming `await` means a new thread:** `await` is a suspension/delegation mechanism, not an instruction to start a thread.
- **Confusing a coroutine's frame with a task's call graph:** coroutine frame inspection shows execution state, while task scheduling and awaited relationships belong to the async runtime.

For CPython 3.14, `asyncio.print_call_graph()` can print the current task's asynchronous call graph. It is not available in 3.12–3.13, so feature-detect it rather than importing it unconditionally:

```python
import asyncio

async def report_async_call_graph():
    printer = getattr(asyncio, "print_call_graph", None)
    if printer is None:
        print("async call-graph introspection is unavailable on this Python")
    else:
        # Call from within a running task; output format is version-specific.
        printer()
```

Run `await report_async_call_graph()` inside an event loop (or call it from an async `main()` run with `asyncio.run`). The 3.14 API prints a graph for the current task; it does not automatically explain native frames or every source of a hang.

## 9. Locals, fast locals, and PEP 667 (Python 3.13)

### Why local variables are special

For performance, CPython function locals are not simply a normal dictionary lookup for every variable. The compiler determines local names, and the interpreter uses optimised local-variable storage. Module and class execution use namespace mappings differently. This is why reading a local through bytecode machinery can differ from looking up a name in a dictionary.

### `locals()` versus `frame.f_locals`

The important version boundary:

- **CPython 3.12 and earlier:** in optimised function scopes, `locals()` and `frame.f_locals` have historical synchronization/copying quirks. Writing to a dictionary returned by `locals()` is not a reliable way to change a running function's local variables.
- **Python 3.13+ (PEP 667):** `locals()` in an optimised scope returns an independent snapshot of the current local bindings. `frame.f_locals` returns a write-through proxy for optimised scopes: changes to existing local bindings through the proxy are reflected in the running frame, and changes to local bindings are visible through the proxy.
- **Module and class scopes:** `locals()` continues to expose the namespace mapping used by that scope.

This does not make function locals dynamically creatable. Adding a new key to `frame.f_locals` does not make a new lexically local variable appear in compiled code. Deleting a real local binding through the proxy is not supported; assigning a value is the supported update operation.

```python
import sys

def inspect_locals():
    value = 10
    snapshot = locals()
    snapshot["value"] = 20
    print("local after snapshot edit:", value)

    frame = sys._getframe()
    frame.f_locals["value"] = 30
    print("local after frame edit:", value)

inspect_locals()
```

Expected version distinction:
- On CPython 3.13+, the first line prints `local after snapshot edit: 10`, while the second prints `local after frame edit: 30`.
- On CPython 3.12 and earlier, the first result is not a reliable contract for writing locals; the second write is not guaranteed to update the executing local variable.

**Do not use frame mutation as normal application design.** PEP 667 improves debugger and tooling behavior. It is not a recommendation to implement dynamic scoping.

## 10. Frame retention, reference cycles, and memory leaks

A frame references its local values. A local value can reference the frame, directly or indirectly. This can create reference cycles. A traceback retains its frames; frames can retain locals; locals can retain large objects. Keeping a traceback or frame in a long-lived object may therefore keep much more memory alive than expected.

Common sources:
- storing `exc.__traceback__` or the exception itself in a global list for later reporting;
- storing `inspect.stack()` results in a cache;
- retaining a frame in a closure or debugger object;
- keeping suspended generators/coroutines reachable;
- logging every local variable on every line event.

### Safer patterns

1. Format a traceback into text or extract a compact list of names/line numbers, then discard frame references.
2. Do not retain raw frame objects unless the tool truly needs them.
3. Keep exception-reporting queues bounded and redact secrets.
4. In a handler, avoid retaining the exception object and its traceback indefinitely. If you need only text, format it and store the text.
5. When diagnosing suspected retention, compare object reachability and memory over repeated operations; do not assume `del` immediately returns memory to the operating system.

```python
import traceback

def format_error():
    try:
        1 / 0
    except ZeroDivisionError as exc:
        # Save text, not the exception/traceback/frame graph.
        return "".join(traceback.format_exception(exc))

report = format_error()
print("ZeroDivisionError" in report)
```

Output:

```text
True
```

The string preserves a human-readable report without intentionally keeping the exception object itself. A formatted string can still contain sensitive values if a traceback renderer or custom exception includes them; apply logging policy and redaction.

### What about `except ... as exc` cleanup?

Python clears the exception target name at the end of an `except` suite to help break reference cycles. That does not protect you if you copied the exception or traceback into another long-lived container.

## 11. Tracing and debugger mechanics

`sys.settrace()` installs a tracing function for the current thread. A trace function receives events such as:
- `call`: a new frame is entered;
- `line`: execution is about to execute a new source line;
- `return`: the frame is leaving;
- `exception`: an exception is raised in the frame.

The global trace function returns a local trace function for a frame. Setting `frame.f_trace_lines` or `frame.f_trace_opcodes` can affect events for that frame. Tracing is invasive: it can change timing substantially and is intended for debugging, coverage, and tooling—not as a free production observability feature.

### Exercise 1 — build a line tracer

Create `line_trace_demo.py`:

```python
import sys

def work(limit):
    total = 0
    for number in range(limit):
        total += number
    return total

TARGET_CODE = work.__code__

def tracer(frame, event, arg):
    # Only install a local trace function for this exact function's code.
    if event == "call":
        return tracer if frame.f_code is TARGET_CODE else None
    if frame.f_code is TARGET_CODE and event == "line":
        # Educational example only: these locals are simple integers.
        # Real applications should redact values and avoid dumping secrets.
        print(f"{frame.f_code.co_name}:{frame.f_lineno} locals={frame.f_locals!r}")
    return tracer

if __name__ == "__main__":
    previous_trace = sys.gettrace()
    sys.settrace(tracer)
    try:
        print("result:", work(3))
    finally:
        # Restore the prior global trace function for this thread.
        sys.settrace(previous_trace)
```

Run:

```bash
python line_trace_demo.py
```

Representative output contains several `work:<line> locals={...}` records, repeated for loop lines, followed by `result: 3`. Local values change as the loop advances. Exact event count, line numbers, and which names are bound at each line depend on source layout and interpreter version.

**Procedure**
1. Run once with tracing enabled.
2. Run the same `work(3)` call with `sys.settrace` installation removed.
3. Increase `limit` and observe how the number of line events grows.
4. For a rough timing comparison, use `time.perf_counter()` around many calls in both modes; run multiple trials and report the median rather than trusting one measurement. For the traced trial, replace the printing callback with a callback that only increments a counter (or does no work). Keep the same target workload and avoid timing setup/teardown.
5. Keep the tracing callback small. Do not print every event in a benchmark of interpreter speed: terminal I/O will dominate the measurement. The local-printing version is for understanding trace events, not for measuring hook overhead.

**Expected observations:** line events reveal control flow, and tracing can slow the target substantially. The slowdown depends on callback work, workload, build, and version.

**What this does not prove:** a line event is not a hardware instruction, not every executed bytecode corresponds to a distinct line event, and a print-heavy tracer cannot isolate the cost of the tracing hook itself.

### Traceback versus tracing

A traceback is passive evidence associated with an exception. A trace function is an active callback invoked during execution. They serve different purposes and have different costs.

The standard-library debugger `pdb` is built on the `bdb.Bdb` debugging framework; traditional line breakpoints rely on tracing machinery. For newer tooling, `sys.monitoring` (introduced in Python 3.12) can offer lower-overhead, event-based instrumentation for supported use cases. It is covered in the module's later tracing lesson; check its events and behavior against the target version.

## 12. Capturing stacks from a hung process

A process can appear hung because a thread is waiting on a lock, blocked in I/O, stuck in a loop, or waiting for another task. Capturing thread stacks helps distinguish these cases.

### `faulthandler.dump_traceback()`

```python
import faulthandler

# Dumps Python tracebacks for all threads to the configured output.
faulthandler.dump_traceback()
```

This is useful for a process you can modify or for a diagnostic signal/timeout path configured before the hang. Signal registration is platform-dependent; consult the official docs before using `faulthandler.register()` in production.

### `sys._current_frames()`

`sys._current_frames()` returns a mapping from thread identifiers to their current topmost frames. It is useful for diagnosing deadlocks because it can inspect stacks without requiring the target threads to cooperate. It is a low-level diagnostic interface: thread IDs may change, and frame objects retain locals while referenced.

```python
import sys

def summarize_threads():
    summaries = {}
    frames = sys._current_frames()
    try:
        for ident, frame in frames.items():
            chain = []
            while frame is not None and len(chain) < 12:
                chain.append(f"{frame.f_code.co_name}:{frame.f_lineno}")
                frame = frame.f_back
            summaries[ident] = list(chain)
    finally:
        # Release references held by the mapping and loop variable.
        del frames
        try:
            del frame
        except UnboundLocalError:
            pass
    return summaries
```

Use this function only as a compact diagnostic example. In production, ensure all frame references are released even if formatting fails, limit depth, avoid serialising locals, and avoid blocking the hung process further with expensive logging. The sample reports Python-visible frames; it does not reveal every native/C frame.

### Safe operational checklist

- Prefer a preconfigured `faulthandler` dump or an approved external sampling tool for a truly wedged process.
- Capture to a controlled file or stderr destination with appropriate permissions.
- Treat stack traces and local variables as potentially sensitive.
- Bound dump frequency and output size.
- For deadlocks, compare each thread's top frames and look for lock acquisition/wait patterns; a stack dump is evidence, not automatic proof of which lock caused the deadlock.
- For native hangs or crashes, Python tracebacks may be incomplete; native stack capture may be required and should follow platform procedures.

## 13. Exercise 2 — recursion guard with a domain-specific error

A recursion guard can turn an unhelpful low-level failure into a domain-specific error before the interpreter's global recursion limit is reached. It is a guardrail, not a replacement for a sound algorithm.

```python
import functools
import sys

class ExcessiveNestingError(ValueError):
    """Raised when an operation exceeds the application's nesting budget."""

def recursion_guard(max_depth=40):
    def decorate(function):
        state = {"depth": 0}

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            state["depth"] += 1
            try:
                if state["depth"] > max_depth:
                    # Compact summary; do not retain frame objects.
                    frame = sys._getframe()
                    names = []
                    while frame is not None and len(names) < 6:
                        names.append(frame.f_code.co_name)
                        frame = frame.f_back
                    del frame  # Do not keep a separate reference to a frame.
                    raise ExcessiveNestingError(
                        f"{function.__name__} exceeded depth {max_depth}; "
                        f"recent calls: {' <- '.join(names)}"
                    )
                return function(*args, **kwargs)
            finally:
                state["depth"] -= 1
        return wrapped
    return decorate

@recursion_guard(max_depth=8)
def walk_down(n):
    if n <= 0:
        return 0
    return 1 + walk_down(n - 1)

try:
    print(walk_down(100))
except ExcessiveNestingError as exc:
    print(type(exc).__name__, str(exc).split(";")[0])
```

Representative output:

```text
ExcessiveNestingError walk_down exceeded depth 8
```

### Important limitations

- This simple decorator's `state` is shared across calls to the decorated function. That can be incorrect when concurrent threads or interleaved asynchronous calls invoke the same function. A production implementation should use context-local state (`contextvars`) or a carefully designed per-execution counter.
- It counts recursive entries through the decorated wrapper, not all frames in the process. Calls through another alias or bypassing the wrapper may not be counted.
- The guard adds call overhead and changes the exception type/traceback.
- It is not a security boundary. Validate input size and algorithmic complexity independently.

**Exercise extension:** redesign the guard to support recursive calls from independent top-level invocations and concurrent tasks without sharing a single mutable counter.

## 14. Practical experiments

At least two experiments are required by the module roadmap. This set lets you collect repeatable evidence.

### Experiment A — observe a live caller frame

**Question:** Does the caller's frame identify the caller's function and current locals?

**Setup/command:** Save the `sys._getframe(1)` example from Section 2 as `frame_probe.py`; run `python frame_probe.py`.

**Procedure:** Change the caller's local variable name/value, call the inspector from a second function, and compare `f_code.co_name`, `f_lineno`, and `f_locals`.

**Expected observations:** the function name and local bindings correspond to the caller at inspection time; line numbers change when the call site moves.

**Interpretation:** frame inspection exposes execution context useful for diagnostics.

**Does not prove:** that frame internals or output format are portable across implementations, nor that introspection is free.

### Experiment B — compare generator state before and after `send`

**Question:** What execution state remains available while a generator is suspended?

**Setup/command:** Run the generator example in Section 7 on CPython 3.12+.

**Procedure:** Inspect `gi_frame`, `gi_running`, `gi_code.co_name`, `f_lineno`, and `f_locals` before the first `next`, after the first `next`, after `send`, and after completion.

**Expected observations:** the body starts on first iteration; at a suspension point, `gi_frame` and local state are generally inspectable; once finished, `gi_frame` may be `None`.

**Interpretation:** a generator retains resumable execution state across yields.

**Does not prove:** a particular internal memory layout or that every implementation exposes identical attributes.

### Experiment C — observe recursion failure without changing global limits

**Question:** Does uncontrolled recursion eventually fail with `RecursionError`?

**Setup/command:** Run the `countdown(100_000)` example from Section 4 using the interpreter's default limit.

**Procedure:** Record `sys.getrecursionlimit()`, run the function, and catch `RecursionError`. Repeat with an iterative equivalent.

**Expected observations:** the recursive version raises `RecursionError`; the iterative version can finish for the same finite input, subject to runtime/resource limits.

**Interpretation:** recursion depth is a practical resource constraint; iteration can avoid nested call depth.

**Does not prove:** a fixed universal maximum depth, or that all recursive native/C calls are protected identically.

### Experiment D — measure tracing overhead carefully

**Question:** How much does line tracing affect a small loop?

**Setup/command:** Use Exercise 1. Time repeated calls with tracing disabled and enabled; do not print events during the timed region.

**Procedure:** Use the same function, inputs, Python build, and trial count. Warm up if appropriate; report median and spread. Ensure the tracer does minimal work.

**Expected observations:** tracing usually slows the workload, often substantially when line events are frequent. Magnitude is workload- and version-dependent.

**Interpretation:** active instrumentation changes runtime cost.

**Does not prove:** a universal slowdown multiplier or that all debuggers use the exact same tracing mechanism.

### Experiment E — verify PEP 667 locally

**Question:** How do `locals()` snapshots and `frame.f_locals` writes differ on the installed version?

**Setup/command:** Run the Section 9 example and record `python --version`.

**Procedure:** Test on CPython 3.12 and 3.13+ if both are available. Do not depend on mutation of `locals()` in application code.

**Expected observations:** in 3.13+, editing the `locals()` snapshot does not change the live local, while assigning through `frame.f_locals` updates it. Older versions have different, historically inconsistent behavior.

**Interpretation:** PEP 667 made namespace behavior more predictable for debuggers and introspection.

**Does not prove:** that arbitrary new names inserted into `f_locals` become compiled local variables.

## 15. Common misconceptions and failure modes

| Misconception / failure | Correction | Safer response |
|---|---|---|
| “A code object is a call frame.” | A code object is compiled code; a frame is one execution's state. | Inspect `function.__code__` separately from the current frame. |
| “A traceback is the live stack.” | A traceback records exception propagation; the live stack is current execution. | Use tracebacks for failures and stack capture for current hangs. |
| “Every Python call consumes a C stack frame.” | CPython 3.11+ changed ordinary Python-to-Python evaluation to reduce C recursion. | Test C-extension/native recursion separately. |
| “Increase the recursion limit until it works.” | This may hide algorithmic depth and can risk process crashes. | Bound input depth or use an iterative algorithm. |
| “Tail recursion is automatically optimised.” | CPython does not generally eliminate Python tail calls. | Use iteration or an explicit stack where depth matters. |
| “`locals()` is a writable live dictionary inside every function.” | Function-scope semantics differ by version; 3.13+ returns snapshots from `locals()`. | Use explicit data structures; use `frame.f_locals` only for tooling. |
| “Keeping a traceback only keeps text.” | Tracebacks retain frames, which can retain locals and object graphs. | Format to text and release references. |
| “A generator is just a function that returns an iterator.” | Its body can suspend with live execution state. | Close generators that own resources; keep suspended state small. |
| “`await` starts a thread.” | `await` suspends/delegates; event-loop scheduling is a separate layer. | Identify blocking synchronous work and scheduling points. |
| “A line tracer shows every bytecode operation.” | Line events are source-level instrumentation events, not one event per opcode. | Use bytecode/monitoring tools for the appropriate level. |
| “A Python stack dump explains all native hangs.” | Python frames may not show native C stack or OS wait details. | Combine with approved native/sampling diagnostics when needed. |

### Troubleshooting procedure

1. **Record the runtime:** `python --version`, `sys.version`, `sys.implementation`, OS, architecture, and whether it is a debug/free-threaded/custom build.
2. **Minimise the reproducer:** keep the smallest function or coroutine that reproduces the issue.
3. **Choose the right evidence:** traceback for an exception, live thread stack for a hang, sampling/native tools for C-level issues.
4. **Check references:** determine whether frames, tracebacks, generators, or tasks are retained by caches, globals, closures, or diagnostic queues.
5. **Avoid unsafe fixes:** do not blindly raise recursion limits, dump all locals, or add heavy tracing to production.
6. **Verify the exact release:** consult documentation and source tag matching the deployed CPython version.

## 16. Concept map / execution flow

```text
function object
  └── code object (compiled instructions + metadata)
        │ call
        ▼
  execution frame / interpreter frame
        │ bytecode evaluation
        ├── reads locals / globals / builtins
        ├── pushes and pops temporary values
        ├── calls another function → caller/callee relationship
        ├── yield/await → suspend and resume later
        ├── return → leave the frame normally
        └── exception → search handler / unwind / build traceback

live thread stack ──> current frames (diagnose what is running/waiting)
exception traceback ──> frames and lines from exception propagation
retained frame/traceback ──> may retain locals and large object graphs
```

The key separation is **execution state versus compiled code**, and **interpreter execution versus scheduling**. A frame explains a particular execution; a code object explains what can be executed; an event loop decides when a coroutine is advanced.

## 17. Self-check questions with answers

### 1. Why doesn't CPython do tail-call optimisation?

**Answer:** CPython does not generally eliminate Python-level tail calls. Retaining normal call structure keeps tracebacks and debugging/call visibility useful and avoids making those semantics depend on tail position. This is an implementation/design choice, not a universal Python-language prohibition. The CPython 3.14 optional tail-calling interpreter is a separate evaluator-dispatch optimisation, not Python function tail-call elimination.

### 2. What lives in a frame, and what stays alive when a generator is suspended?

**Answer:** Conceptually, a frame associates a code object with execution position, local/fast-local bindings, temporary evaluation stack, globals, builtins, and a caller link. Exact physical layout is CPython-version-specific. A suspended generator preserves enough execution state to resume at its `yield`, including relevant local bindings and references to objects reachable from those bindings. It may expose this state through `gi_frame` while the frame remains available.

### 3. Build the `settrace` line tracer and use it to explain why a loop is slow under a debugger.

**Answer:** Use Exercise 1. The trace callback is invoked for line events and its own Python work runs in the target's execution path, so frequent events add overhead. Printing each event adds substantial I/O cost. The experiment demonstrates the cost for that specific workload, not a universal debugger slowdown factor.

### 4. What is the difference between a code object, a frame, and a traceback?

**Answer:** A code object is compiled code and metadata; a frame is execution state for an active or suspended execution; a traceback is a linked record of frame/line information associated with exception propagation.

### 5. Why can storing an exception cause a memory leak?

**Answer:** An exception may retain its traceback; the traceback retains frames; frames retain local variables; those variables may reference large object graphs. Store formatted text or compact summaries when raw exception/frame objects are not needed.

### 6. What changed in Python 3.13 for `locals()` and `frame.f_locals`?

**Answer:** Under PEP 667, `locals()` in optimised function scopes returns an independent snapshot, while `frame.f_locals` provides a write-through proxy that reads and writes live local bindings. Module/class namespace behavior remains mapping-based. Earlier CPython versions have different, historically inconsistent behavior.

### 7. Does a Python stack dump always reveal why a process is hung?

**Answer:** No. It can show Python-level frames and where threads appear to be waiting, but may not reveal native C frames, kernel wait details, or the full lock ownership story. Use it as evidence and combine it with suitable native or sampling diagnostics when required.

## 18. Summary

- Code objects describe compiled code; frames describe one execution.
- Call-stack links and traceback frame/line pairs are foundational debugging evidence.
- Frame inspection is powerful but can be expensive, sensitive, and memory-retaining.
- `RecursionError` is a guardrail. CPython does not generally optimise away Python tail calls; Python recursion depth and C-stack depth are related but not identical.
- Since CPython 3.11, internal interpreter frames reduce the need to allocate public frame objects for every call; exact internals remain version-specific.
- The evaluation loop runs bytecode; the eval breaker lets the runtime notice pending work at appropriate points.
- Generators and coroutines can suspend with execution state and referenced objects alive. An event loop schedules coroutines; the interpreter executes code when they are advanced.
- Tracebacks retain frames, and frames retain locals. Prefer compact, redacted diagnostics and release references.
- PEP 667 changes `locals()` and `frame.f_locals` behavior in Python 3.13.
- For a hang, capture stacks safely, interpret them cautiously, and use native diagnostics when Python frames are insufficient.

## References

Use documentation for the exact interpreter version in production. Internal source links below point to official project documentation or source; implementation details can move between releases.

1. Python `sys` documentation (`_getframe`, recursion limit, `_current_frames`): https://docs.python.org/3/library/sys.html
2. Python `inspect` documentation (`currentframe`, `stack`, frame attributes): https://docs.python.org/3/library/inspect.html
3. Python data model — frame objects: https://docs.python.org/3/reference/datamodel.html#frame-objects
4. Python `traceback` documentation: https://docs.python.org/3/library/traceback.html
5. Python `faulthandler` documentation: https://docs.python.org/3/library/faulthandler.html
6. Python `threading` documentation (`stack_size`): https://docs.python.org/3/library/threading.html#threading.stack_size
7. Python `asyncio` documentation: https://docs.python.org/3/library/asyncio.html
8. PEP 667 — Consistent views of namespaces (Python 3.13): https://peps.python.org/pep-0667/
9. Python/C API — Frame Objects: https://docs.python.org/3/c-api/frame.html
10. CPython internal frame design notes (private implementation details): https://github.com/python/cpython/blob/main/InternalDocs/frames.md
11. CPython 3.11 release notes / “What’s New”: https://docs.python.org/3/whatsnew/3.11.html
12. CPython 3.12 release notes / “What’s New”: https://docs.python.org/3/whatsnew/3.12.html
13. CPython 3.13 release notes / “What’s New”: https://docs.python.org/3/whatsnew/3.13.html
14. CPython 3.14 release notes / “What’s New”: https://docs.python.org/3/whatsnew/3.14.html
