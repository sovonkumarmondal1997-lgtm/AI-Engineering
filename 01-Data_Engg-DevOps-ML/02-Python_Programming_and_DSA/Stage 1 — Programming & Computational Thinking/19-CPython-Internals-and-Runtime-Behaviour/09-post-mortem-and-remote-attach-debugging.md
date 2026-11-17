# Post-Mortem and Remote-Attach Debugging

**Target:** CPython 3.12–3.14; commands are labelled by operating system and version where they differ.  
**Purpose:** Diagnose exceptions, hangs, native crashes, and production stalls by collecting evidence safely before changing or terminating a process.

## Learning outcomes

By the end of this lesson, you should be able to:

- Distinguish an exception that has already happened from a process that is still alive but stuck.
- Preserve traceback chains, exception groups, relevant inputs, versions, and logs while creating a minimal reproduction.
- Use `pdb`, `pdb.pm()`, `pdb.post_mortem()`, `traceback`, and `logging.exception()` for exception forensics.
- Choose among `faulthandler`, `sys._current_frames()`, `py-spy`, core dumps, and OS-level tools based on the symptom and available permissions.
- Recognise Python-level lock waits, I/O waits, CPU spins, and native/C-extension deadlocks as different diagnostic cases.
- Explain the capabilities and limits of PEP 768 remote debugging in CPython 3.14, including why it is not universally available or risk-free.
- Follow a production incident runbook that preserves evidence, limits blast radius, and defines stop/rollback conditions.

## Prerequisites

You should know how to run Python scripts, read a traceback, use basic breakpoints, and distinguish a process from a thread. Helpful background includes exceptions and exception chaining, locks and deadlocks, signals, virtual memory, containers, and profiling. The earlier debugger lessons cover basic `pdb`; this lesson extends that knowledge to post-mortem and live-process diagnosis.

Examples target **CPython 3.12–3.14**. The shell commands labelled Linux, macOS, or Windows are not portable across operating systems. The available environment for preparing this lesson was Linux x86-64 with Python 3.13.5; `gdb`, `py-spy`, and `strace` were not installed there, so commands requiring those tools are instructional and were not executed in that environment. Python 3.14-only remote-attach examples were not executable on Python 3.13.5.

## 1. Mental model: two different debugging situations

An exception post-mortem starts **after an execution path has raised an exception**. A live-hang investigation starts while the process is still running—or blocked—and asks what every relevant thread or task is doing. A core dump is a snapshot of process state at a crash or when deliberately captured; it is not the same thing as a Python traceback.

```text
Symptom
  ├─ Process exited with an exception
  │    └─ Preserve traceback + inputs → pdb post-mortem → minimal reproduction
  ├─ Process alive, CPU high
  │    └─ Identify hot thread → Python/native samples → consider OS debugger
  ├─ Process alive, CPU near zero / requests stalled
  │    └─ Dump all thread stacks → inspect lock/I/O waits → inspect dependencies
  └─ Process crashed / segfaulted
       └─ Preserve core + logs → faulthandler output → native debugger and symbols
```

**Why this distinction matters:** `pdb.pm()` cannot inspect a hang that has not raised an exception. Conversely, attaching an interactive debugger to a live production process can pause it, mutate state, or execute arbitrary code. Start with the least invasive source of evidence that can answer the question.

A traceback is a chain of frames showing the path through Python code. It is not a complete process snapshot: it generally does not show all threads, native stack frames, kernel wait reasons, locks held by native code, or external dependency state. A native crash may prevent Python from running cleanup or logging code at all.

## 2. Basic: preserve and inspect exceptions

### 2.1 Capture the original failure

**What it is:** Exception forensics means preserving the exception type, message, traceback, chaining context, input/configuration identifiers, and relevant runtime details before the evidence disappears.

**Why it matters:** A traceback copied without its chained exception, worker context, or exact input may hide the real failure. A production log that contains only `request failed` is not enough to reconstruct the path.

Use `logging.exception()` from inside an `except` block. It records the current exception and traceback. Do not log secrets or unredacted request bodies merely because they might help reproduce the problem.

```python
import logging

logging.basicConfig(level=logging.INFO)


def parse_quantity(text: str) -> int:
    try:
        return int(text)
    except ValueError as exc:
        # Preserve causal context instead of silently replacing the error.
        raise ValueError("quantity must be an integer") from exc


try:
    parse_quantity("three")
except ValueError:
    # logging.exception includes the active traceback.
    logging.exception("Invalid quantity in import job_id=%s", "job-redacted-17")
```

**Expected observation:** the log includes the outer `ValueError`, the original conversion error, and the traceback chain. Timestamps and formatting depend on logging configuration. The example intentionally uses a synthetic identifier, not customer data.

Python stores exception context through `__context__` and explicit causes through `__cause__`. `raise NewError(...) from exc` makes the causal relationship explicit. `raise NewError(...) from None` suppresses display of the implicit context; use it only when deliberately hiding irrelevant implementation detail, not to erase evidence during incident handling.

### 2.2 Format a traceback for later inspection

`traceback` can render an exception into text suitable for a protected incident artifact. `TracebackException` supports structured formatting and, optionally, local-variable capture.

```python
import traceback

try:
    1 / 0
except Exception as exc:
    summary = traceback.TracebackException.from_exception(exc)
    rendered = "".join(summary.format(chain=True))
    print(rendered)
```

The rendered text contains the exception and stack frames. The exact source lines and paths depend on the file and runtime. Keep `chain=True` when the cause or context matters.

**Local-variable caution:** `traceback.TracebackException.from_exception(exc, capture_locals=True)` can be useful in a controlled reproduction, but local variables may include access tokens, passwords, session cookies, personal data, SQL parameters, and large objects. Do not enable it globally in production without a redaction and access-control design. A safer default is to capture selected, explicitly approved fields.

`logging.exception()` records the active exception traceback (equivalent to requesting exception information). `stack_info=True` is different: it records the current stack leading to the logging call, which can be useful for understanding where a log statement was reached. It is not a substitute for `exc_info` and may expose function names, paths, and arguments in custom logging formats. Use both only when they answer distinct questions and the output is appropriately protected.

Exception groups (Python 3.11+) can carry multiple failures from concurrent or structured work. Preserve the whole group rather than flattening it into one message:

```python
import traceback

try:
    raise ExceptionGroup(
        "batch failed",
        [ValueError("bad row"), OSError("storage unavailable")],
    )
except ExceptionGroup as exc:
    # TracebackException preserves the group structure when formatting.
    report = traceback.TracebackException.from_exception(exc)
    print("".join(report.format(chain=True)))
```

The rendered output shows the group and its nested exceptions; line layout varies by Python version. A group tells you which errors were collected, not necessarily which one caused the original system-level incident.

In CPython 3.12+, `sys.last_exc` can expose the last unhandled exception in interactive contexts. It is not a general replacement for explicitly retaining the exception or logging it at the point of failure. `exc.__traceback__` provides the traceback object while the exception remains available; retaining exceptions and frames can also retain objects in memory.

### 2.3 Post-mortem with `pdb`

`pdb` is the standard-library source-level debugger. Post-mortem debugging inspects frames from an exception that has already occurred.

**Run a script under the debugger:**

```bash
python -m pdb reproduce.py
```

The debugger starts the program under control. On abnormal termination it can enter post-mortem mode; normal command-loop behaviour, restarting, and prompts depend on how the program exits and the debugger is used.

**In an interactive session after an uncaught exception:**

```python
import pdb

# Run the failing expression first, then call:
pdb.pm()
```

`pdb.pm()` uses the most recent exception traceback known to the interactive interpreter. For code that has explicitly retained a traceback, call `pdb.post_mortem(tb)` with that traceback. These APIs are most useful when the original process/session is still available; they do not recover a traceback from an unrelated, already exited process.

Useful commands:

| Command | Meaning | Typical use |
|---|---|---|
| `w` or `bt` | Show the stack / traceback | Identify the call path |
| `u` / `d` | Move up/down a frame | Inspect caller context |
| `l` / `ll` | List source / longer source listing | Read surrounding code |
| `p expr` / `pp expr` | Evaluate and pretty-print an expression | Inspect values |
| `args` | Show function arguments | Check input assumptions |
| `interact` | Start an interactive namespace | Explore carefully |
| `b file.py:42, cond` | Conditional breakpoint | Reproduce a specific state |
| `tbreak file.py:42` | Temporary breakpoint | Stop once |
| `until` | Continue until a later line in the current frame | Skip a loop section |
| `return` | Continue until the current function returns | Inspect return behaviour |
| `commands` | Define commands to run when a breakpoint is hit | Automate a small, repeatable local inspection |
| `!statement` | Execute a Python statement | Change state intentionally, with caution |

A debugger expression can call functions and cause side effects. Do not assume `p expression` is read-only: property access, custom `repr`, lazy values, or method calls may execute application code.

### 2.4 Breakpoints and pytest

Use `breakpoint()` for a deliberately instrumented reproduction. Its behaviour is controlled by `PYTHONBREAKPOINT`; setting it to `0` disables the built-in breakpoint hook. Do not leave unconditional breakpoints in production code.

For tests, these are useful local commands:

```bash
pytest --pdb path/to/test_file.py::test_case
pytest --trace path/to/test_file.py::test_case
pytest -x --lf
```

- `--pdb` enters the debugger on test failure.
- `--trace` enters the debugger at the beginning of each selected test.
- `-x --lf` stops after the first failure and reruns last-failed tests, subject to pytest's recorded state.

An optional IPython debugger can be selected with `--pdbcls=IPython.terminal.debugger:TerminalPdb` if IPython is installed. These options are for a controlled test environment, not a production process.

### 2.5 Custom exception hooks: preserve, do not conceal

`sys.excepthook` handles uncaught exceptions reaching the top level of the main thread. It does not automatically replace exception handling for every thread, task, or native crash. `threading.excepthook` handles uncaught exceptions from `threading.Thread`; `sys.unraisablehook` handles exceptions that cannot be propagated normally, such as some failures in finalizers.

A minimal interactive-only hook can add post-mortem inspection while retaining traceback output:

```python
import pdb
import sys
import traceback


def exception_hook(exc_type, exc, tb):
    traceback.print_exception(exc_type, exc, tb)
    # Do not start an interactive prompt in a non-interactive service.
    if sys.stdin.isatty() and sys.stderr.isatty():
        pdb.post_mortem(tb)


sys.excepthook = exception_hook
```

This example is appropriate for a local diagnostic script, not as a blanket production configuration. A custom hook must not swallow the failure, block on unavailable stdin, expose locals, or interfere with a supervisor's restart policy. Production logging should generally be configured centrally and tested for failures in the logging path itself.

## 3. Minimal reproductions and evidence quality

A **minimal reproduction** is the smallest program, input, and environment that still exhibits the failure. It reduces noise so the cause can be isolated.

Record, where safe:

- Exact Python implementation and version, executable path, build mode, OS/kernel, architecture, and relevant dependency versions.
- The exception chain or thread stacks, timestamps, request/job correlation ID, and whether the symptom is repeatable.
- Redacted input shape, random seed, relevant configuration values, and concurrency/load conditions.
- What changed recently: deploy, dependency, feature flag, data shape, resource quota, or traffic pattern.

Do not publish credentials, full environment dumps, customer records, signed URLs, or raw core files in an open ticket. Restrict access to evidence, define retention, and record who collected it.

A minimal-reproduction checklist:

1. Preserve the first failure and logs before retrying or restarting.
2. Replace customer data with a synthetic fixture that retains the failing shape.
3. Remove unrelated services and reduce concurrency gradually.
4. Keep the same dependency versions and configuration that matter.
5. Add a regression test that fails before the fix and passes after it.

A reproduction that no longer fails after removing concurrency may indicate a race or timing-sensitive defect; it does not prove the removed component was the root cause.

## 4. Intermediate: hangs and thread-stack evidence

### 4.1 `faulthandler`: low-dependency traceback dumps

`faulthandler` can dump Python thread tracebacks on demand, after a timeout, or during selected fatal signals. It is useful when application logging is stalled or an exception cannot be raised normally.

Enable it at process startup:

```bash
python -X faulthandler service.py
```

or set `PYTHONFAULTHANDLER=1` in the service environment before launch. In code:

```python
import faulthandler

faulthandler.enable()
faulthandler.dump_traceback_later(30, repeat=False)

# Run the workload under investigation.
# Cancel the pending timeout if the operation finishes normally:
# faulthandler.cancel_dump_traceback_later()
```

The timeout example emits a dump after roughly 30 seconds unless cancelled. Timing and output destination depend on scheduling and configuration. A scheduled dump is a diagnostic alarm, not proof of a deadlock; slow I/O or overloaded hosts can also exceed the timeout.

On Unix-like platforms that support it, register a user signal such as `SIGUSR1`:

```python
import faulthandler
import signal

# Unix example only; SIGUSR1 is not available on Windows.
faulthandler.enable()
faulthandler.register(signal.SIGUSR1, all_threads=True)
```

Then, from another Linux shell, request a dump with `kill -USR1 PID` if signal permissions allow it. **Do not send this signal unless the target process has registered the handler**; the default action for an unhandled signal may terminate the process. Keep the output file descriptor open for as long as the handler is registered. Avoid replacing a service's existing signal handler without coordinating ownership and chaining behaviour.

`faulthandler` uses constrained, low-level output paths to remain useful during faults. It is not a full debugger and may not show native C stack frames or all interpreter internals. `faulthandler.register()` is unavailable on Windows. Fatal-signal support and output details are platform-dependent.

### 4.2 `sys._current_frames()` for live Python stacks

In CPython, `sys._current_frames()` returns a mapping from thread identifiers to the topmost Python frame for each thread. It is a private, implementation-specific API—not a language guarantee. It can help inspect a live process from code that is already running inside that process.

```python
import sys
import traceback


def dump_python_stacks(file=None):
    """Write Python stacks for threads visible to this interpreter."""
    if file is None:
        file = sys.stderr
    for thread_id, frame in sys._current_frames().items():
        print(f"\n--- thread ident={thread_id} ---", file=file)
        traceback.print_stack(frame, file=file)
```

This function is suitable for a controlled diagnostic command or a deliberately installed signal/health mechanism. It does not attach to an arbitrary PID from outside the process. It also does not reveal a thread that is executing only native code with no current Python frame, nor does a stack alone prove which lock is held. Be mindful that formatting and writing stacks can itself block if the destination is a blocked pipe or a slow network filesystem.

For a thread that appears to be waiting forever, collect more than one snapshot, spaced apart. Identical stacks suggest a stable wait but do not identify the underlying lock owner by themselves. Compare stack traces with CPU, request latency, thread states, lock instrumentation, dependency health, and system-call evidence.

### 4.3 `py-spy`: external sampling without application instrumentation

[`py-spy`](https://github.com/benfred/py-spy) is a third-party sampling profiler that can inspect Python stack samples from another process. It is often a good first external tool because it can collect stacks without requiring you to edit and redeploy application code.

Install it in an approved diagnostic environment, for example with `pipx install py-spy` or the package manager approved by your organisation. Verify the binary and version before use. Attaching still requires OS permissions and compatible process access; installation alone does not grant access.

```bash
# Linux/macOS, after verifying PID and authorization:
py-spy dump --pid 12345
py-spy top --pid 12345
py-spy record --pid 12345 --duration 20 --output profile.svg

# Native frames: only on supported OS/architecture/build combinations.
py-spy record --native --pid 12345 --duration 20 --output native-profile.svg
```

Replace `12345` with the verified target PID. `dump` requests a stack snapshot, `top` samples activity, and `record` creates a profile. These commands may be unavailable or behave differently depending on the `py-spy` version, OS, Python build, container namespace, and permissions. Check `py-spy --help` for the installed version before a production incident. Profiles and stack dumps may contain function names and code paths; restrict their access.

**Interpretation:**

- A hot Python function appearing repeatedly in samples supports a CPU-bound Python hypothesis.
- Threads repeatedly shown in the same blocking call can support a wait hypothesis.
- Missing or incomplete Python frames can occur with native code, stripped symbols, unsupported builds, or permission limitations.
- Sampling is statistical: a short capture can miss rare events, and a sample is not a complete trace of every instruction.

**Escalation path for a confirmed CPU spin (Linux example):** start with the least invasive evidence and stop when it is sufficient. `top -H -p PID` identifies hot OS threads; `py-spy dump --pid PID` captures Python stacks; a bounded `py-spy record` shows whether the same path dominates. If native work remains plausible and the architecture/build are supported, try `py-spy record --native ...` or `perf top -p PID` under the organisation's perf permissions. Only then consider an approved, brief `gdb -p PID` backtrace or `gcore PID`. Native attach can pause the process; `gcore` can pause it and consume substantial disk. Check latency, storage headroom, symbols, ptrace policy, and the rollback/stop condition first. Preserve stacks, profiles, metrics, logs, and build identifiers before a restart if safe; do not delay mitigation when impact is worsening.
### 4.4 asyncio task diagnostics

A process can have few OS threads yet many suspended asyncio tasks. In a running event loop, `asyncio.all_tasks()` returns tasks associated with that loop. A basic diagnostic coroutine can print task names and stacks:

```python
import asyncio


async def dump_tasks():
    for task in asyncio.all_tasks():
        print(f"TASK name={task.get_name()} done={task.done()}")
        for frame in task.get_stack(limit=10):
            print(f"  {frame.f_code.co_filename}:{frame.f_lineno} "
                  f"in {frame.f_code.co_name}")
```

Call this from the relevant event loop, not from an unrelated thread without thread-safe scheduling. A task stack shows where the coroutine is suspended, not necessarily why its awaited dependency has not completed. `PYTHONASYNCIODEBUG=1` and `asyncio.run(main(), debug=True)` can expose slow callbacks and some misuse in a reproduction, but debug mode adds overhead and should be enabled deliberately.

CPython 3.14 adds command-line introspection for tasks in another running process:

```bash
# CPython 3.14; supported platforms only; permission may be required.
python -m asyncio ps 12345
python -m asyncio pstree 12345
```

`ps` lists pending tasks and coroutine stacks; `pstree` presents the await/task relationships as a tree. These commands inspect the target process without executing code inside it, but they are available only on supported platforms and may require permission to inspect the process. Check `python -m asyncio --help` on the exact interpreter rather than assuming a 3.12/3.13 environment supports these 3.14 commands.

## 5. Diagnose the symptom before selecting a tool

### 5.1 Process stuck with near-zero CPU

Near-zero CPU usually means the process is waiting, sleeping, blocked on I/O, waiting for a lock, throttled, or not scheduled. It does not automatically mean a Python deadlock.

1. Confirm the process is alive and identify the exact PID/container/worker.
2. Check request latency, queue depth, dependency health, CPU, memory, file descriptors, and recent deployment changes.
3. Capture Python thread stacks with `faulthandler`, `py-spy dump`, or an approved in-process diagnostic.
4. Repeat the snapshot after a short interval; note which stacks change and which remain fixed.
5. If stacks indicate lock acquisition or a blocking native call, collect native/OS evidence where available.
6. If every thread is waiting on an external service, investigate that service and timeout/retry behaviour rather than assuming the Python runtime is at fault.

**Linux examples:**

```bash
ps -o pid,ppid,stat,pcpu,pmem,nlwp,etime,cmd -p 12345
cat /proc/12345/wchan
cat /proc/12345/status
```

`/proc` fields and permissions are Linux-specific. `wchan` can be unavailable or restricted and is only a clue about kernel wait state. Do not paste command output containing sensitive command-line arguments into a public ticket.

### 5.2 CPU at or near 100%

High CPU calls for a different first move: determine which thread is consuming CPU, then distinguish Python bytecode, native extension work, and kernel/system overhead.

**Linux:**

```bash
top -H -p 12345
```

Record the hot thread's Linux TID and CPU percentage. `py-spy dump --pid 12345` can show Python stacks; `py-spy record` can establish whether the same functions dominate over time. If samples point to a native extension or do not explain the CPU, consider a bounded `py-spy record --native --pid 12345 --duration 20 --output native-profile.svg` capture where supported, Linux `perf`, or an approved native debugger. Native profiling may require symbols, kernel permissions, compatible unwinding support, and additional overhead.

**macOS:** Activity Monitor or `top -pid 12345 -stats pid,command,cpu,threads` can help establish process activity. Tools such as `sample PID 10` can collect a time-limited sample on macOS, subject to OS permissions and version.  
**Windows:** Task Manager/Process Explorer and Windows Performance Recorder/Analyzer are possible OS-level starting points; exact tools and privileges vary. The Linux `top -H`, `/proc`, `strace`, `gcore`, and `SIGUSR1` examples do not apply to Windows.

### 5.3 Python deadlock versus native deadlock

A **deadlock** is a set of participants that cannot proceed because each waits for a condition another participant will never satisfy. A common Python-level pattern is two threads acquiring locks in opposite order. Native libraries can deadlock inside C/C++ locks, extension code, the allocator, or a third-party library. Python thread stacks alone may show only the boundary where execution entered native code.

For a Python-level lock deadlock, inspect all thread stacks and lock-acquisition order. For a native deadlock, a native backtrace can be necessary to identify C frames and mutex waits. A Python traceback ending at a C-extension call is evidence of the boundary, not proof the extension is faulty; the extension may be waiting correctly for an external resource.

Minimal local example (do not run as a service):

```python
import threading
import time

first = threading.Lock()
second = threading.Lock()
ready = threading.Barrier(2)


def worker(a, b):
    with a:
        ready.wait()
        time.sleep(0.05)  # Make the opposite-order acquisition easy to observe.
        with b:
            print("acquired both")


threading.Thread(target=worker, args=(first, second), daemon=True).start()
threading.Thread(target=worker, args=(second, first), daemon=True).start()
time.sleep(1)
print("main thread reached the end; daemon workers may remain blocked")
```

**Representative observation:** neither worker prints `acquired both`; both can remain blocked trying to acquire the other's lock. The exact timing is not a guarantee, though the barrier and opposite acquisition order make the deadlock likely. This demonstrates a lock-order deadlock, not every possible production hang. Use a disposable process because the example intentionally does not resolve the locks.

## 6. Core dumps and native debuggers

### 6.1 Core dumps: a post-crash process snapshot

A core dump records a process memory image and register/thread state at a point in time, subject to OS configuration and dump filters. It can help diagnose segmentation faults in C extensions, interpreter crashes, and native deadlocks. It may contain credentials, request data, encryption keys, and arbitrary process memory; handle it like highly sensitive production data.

**Linux, systemd-based distributions:**

```bash
# Inspect core-dump policy and resource limit in the service's actual context.
ulimit -c
cat /proc/sys/kernel/core_pattern
coredumpctl list --no-pager
coredumpctl info 12345
```

The PID passed to `coredumpctl info` is meaningful only if it corresponds to a recorded dump. `coredumpctl` availability depends on systemd and local policy. `ulimit -c unlimited` in a shell affects children of that shell, not an already-running service; changing a service's unit or system policy requires the appropriate controlled deployment/restart. Core collection may be disabled by container runtime, service manager, resource limits, security policy, or storage limits.

If a core is already available and authorized, use the matching executable and libraries:

```bash
# Linux: use the executable and symbols matching the crashed process.
gdb /path/to/python /path/to/core
```

Inside `gdb`, useful initial commands include `info threads`, `thread apply all bt`, and (when Python debug helpers are installed and match the interpreter) `py-bt` or `py-list`. Python-specific helpers are not guaranteed to be present. Distribution debug packages such as `python3-dbg` are distribution/version-specific; install matching symbols and helpers rather than assuming any `gdb` binary can decode every Python build. A mismatched executable or shared library can produce misleading output.

**Linux, capture a live process:** `gcore PID` may create a core of a running process if installed and permitted. This can pause or significantly disrupt the process and can consume substantial disk space. Do not use it casually on a latency-sensitive production worker. Confirm storage, access controls, incident approval, and a rollback plan first.

**macOS:** core-dump policy and native debugger availability differ; `lldb` is commonly used for native debugging and process attachment is governed by system security, code signing, and entitlements. Do not assume Linux `gcore` or `coredumpctl` commands exist.  
**Windows:** Windows Error Reporting dumps and WinDbg are common native-crash routes; Linux core commands do not apply.

### 6.2 `gdb` and `strace` are conditional tools

`gdb` can inspect native threads, registers, and C/C++ backtraces on supported platforms. Attaching to a live process generally pauses it while the debugger controls it. It may require the same UID, `CAP_SYS_PTRACE`, root-equivalent privileges, compatible namespaces, and suitable symbols. Containers often restrict `ptrace` through capabilities, seccomp, Yama, or runtime policy. Do not add `SYS_PTRACE` or run a privileged container solely as an unreviewed troubleshooting shortcut.

**Linux only, authorized diagnostic session:**

```bash
gdb -p 12345
```

Then inspect threads (`info threads`) and native backtraces (`thread apply all bt`). Detach with `detach` before quitting when appropriate. Attaching may stop the target; ensure the service owner understands this risk. Debugger commands can modify process state. Use a staging reproduction first when possible.

`strace` traces Linux system calls and signals; it can help determine whether a process repeatedly waits in `futex`, polls a descriptor, or retries a failing syscall. It does not explain Python semantics by itself, and tracing may add significant overhead or reveal sensitive paths/data.

```bash
# Linux only; limit duration and output, and obtain approval first.
timeout 10s strace -ff -tt -T -p 12345 -o /secure/incident/strace
```

Use a restricted directory with appropriate permissions. The command may not be installed, may be blocked by ptrace policy, and may alter timing. Interpret syscall names and durations with care; a `futex` wait alone does not prove a deadlock. `dtruss`/DTrace and Windows ETW are different platform-specific alternatives, not drop-in syntax replacements for `strace`.

### 6.3 Segfault triage and native extensions

A segmentation fault is usually a process-level memory access fault, not a normal Python exception. Python may not execute `except`, `finally`, `atexit`, or logging handlers. Enable `faulthandler` before the fault to capture the Python stack where possible, and preserve the core when configured.

For a reproducible local failure, try one change at a time:

- Run with `python -X dev` to enable additional runtime checks and warnings.
- Use `PYTHONMALLOC=debug` for allocator diagnostics where supported; it can change memory layout/timing and is not a production fix.
- Reduce to a minimal input and bisect native-extension/dependency versions.
- If you own the native code, rebuild with appropriate address/undefined-behaviour sanitizers and matching symbols.

`ctypes` can deliberately invoke invalid memory operations, but intentionally causing a segfault can terminate the interpreter and is unsafe outside a disposable test process. Do not run a destructive crash example against production or a shared notebook kernel.

## 7. PEP 768 and CPython 3.14 remote attach

### 7.1 What the feature does

[PEP 768](https://peps.python.org/pep-0768/) adds a safe external debugger interface to **CPython 3.14**. Its public Python API is `sys.remote_exec(pid, script)`, which asks a target process to execute a Python script at a safe interpreter execution point. CPython 3.14's `pdb` adds `-p` / `--pid` support:

```bash
# CPython 3.14 only, with OS permission and target support:
python -m pdb -p 12345
```

The feature can make interactive debugging possible without restarting a compatible running interpreter. It is not a universal remote-debug protocol for arbitrary Python implementations, older CPython versions, every OS, or every build. For direct `sys.remote_exec()` use, the local caller and target must be CPython with the same major and minor version (for example, both 3.14); if either interpreter is a pre-release, the exact versions must match. Build mode also matters: do not assume a GIL-enabled build and a free-threaded build are interchangeable; CPython's remote-debug metadata includes build characteristics that tools must validate. The function takes a path to a Python script file, returns immediately, and provides no completion acknowledgement. Keep the file accessible and unchanged until the target has executed it. `pdb -p` depends on this mechanism and the local debugger should therefore match the target's version requirements.

**Critical timing limitation:** `sys.remote_exec()` returns after scheduling the request; it does not provide a reliable acknowledgement that the target script has finished. The target executes the script on its main thread when it reaches a suitable safe point. If the target is blocked in a system call or waiting for I/O, execution may not happen until the next bytecode instruction is reached or a signal is received. Therefore, a process that is completely wedged in native code may not respond promptly to `pdb -p`.

### 7.2 Permissions and availability

Remote attach is gated by the operating system. On Linux, tracing generally requires suitable `CAP_SYS_PTRACE` or equivalent permissions and is subject to ptrace policy, namespaces, ownership, and restrictions on set-user-ID/set-group-ID processes. macOS and Windows have their own process-inspection and security rules. The target may be running in a container or PID namespace that makes the visible PID differ from the host PID.

Availability also depends on interpreter build and platform support. CPython 3.14 supports disabling the feature with:

- `PYTHON_DISABLE_REMOTE_DEBUG=1` set before interpreter startup;
- `-X disable_remote_debug` at interpreter startup;
- a build configured with `--without-remote-debug`.

For CPython 3.14, follow the versioned command-line and remote-debugging documentation: use a **non-empty** value such as `PYTHON_DISABLE_REMOTE_DEBUG=1`, or the documented `-X disable_remote_debug` spelling. PEP text and documentation have differed in how they describe empty values, so do not rely on an empty environment-variable value as a disable switch. A distributor may build Python without support, and some platforms may not support the mechanism. Check the exact interpreter's documentation and build rather than inferring availability from `sys.version_info` alone.

### 7.3 Security and operational trade-offs

Remote attach can execute arbitrary Python code inside the target process with that process's privileges. It can inspect secrets, alter in-memory flags, change globals, trigger requests, write files, or destabilise the service. OS-level access checks reduce who can invoke it, but do not make an authorised attach harmless. Treat access as equivalent to privileged code execution in the target process.

Before attaching:

1. Verify the exact PID and executable; avoid PID-reuse mistakes.
2. Confirm incident approval, owner, permissions, and a stop condition.
3. Prefer a low-impact stack dump first; do not start by patching a production flag.
4. Use a protected script path controlled by the operator; ensure the file exists and is not overwritten until the target has read it.
5. Restrict output, redact secrets, record timestamps and operator actions, and do not expose a debug listener to the public internet.
6. If the attach stalls, do not repeatedly inject scripts or escalate privileges without reassessing. Switch to external evidence collection or controlled restart if the risk becomes unacceptable.

For a controlled test, use a disposable worker with a harmless script and verify that the feature is available. Do not use a production process to learn the protocol for the first time.

### 7.4 `debugpy` remote debugging is a different mechanism

VS Code's `debugpy` can support remote debugging through a listener and IDE connection. This is not the same thing as PEP 768. A debug listener creates a network access path and must be bound and protected appropriately. Never expose an unauthenticated debugging port to the internet. Prefer a private network or SSH tunnel, firewall restrictions, short-lived enablement, and explicit authentication/authorisation. Exact `debugpy` invocation and attach support depend on the installed version and deployment architecture; follow its versioned documentation.

### 7.5 If you build an in-process diagnostic endpoint

Prefer a **narrow diagnostic interface**, not a generic code-execution backdoor. Good examples include an authenticated request to dump thread stacks, report selected counters, or return a bounded heap histogram. Design it with:

- local-only binding or a private control plane; strong authentication and authorisation; no public unauthenticated listener;
- an explicit feature flag, a short enablement window, rate limits, request timeouts, and a documented disable/rollback path;
- an allowlist of diagnostics rather than arbitrary Python expressions or shell commands;
- redaction before output, size limits, access-controlled storage, and audit records for operator, timestamp, request, and result;
- tests showing that diagnostics fail safely when output storage is unavailable and do not block the main request path.

A signal-triggered `faulthandler` dump is often narrower than a general endpoint, but signal ownership and file-descriptor lifetime still need to be managed. Do not introduce a new production backdoor during an incident as an improvised fix; add and rehearse the mechanism through normal review and deployment controls.

## 8. More evidence: native stacks, memory, and record/replay

### 8.1 Python and native stack evidence complement each other

Use Python stacks to learn where Python code is running or suspended. Use a native debugger or native profiler when the relevant work is in C/C++, a system library, the interpreter, or a native lock. For an extension call, collect both views if possible: the Python frame at the extension boundary and the native thread backtrace below it.

A native backtrace without symbols may show addresses or library names but not useful function names. Install matching debug symbols in a controlled environment; symbols from another build can mislead. Keep executable, shared libraries, core file, Python version/build, and package versions together as evidence.

### 8.2 Memory growth during a hang or degradation

If the symptom is memory growth rather than a pure hang, use tools appropriate to the allocation source. `tracemalloc` tracks Python memory allocations after tracing is started; it does not account for every native allocation. `memray` can track Python and native allocations when configured appropriately; `memray attach PID` is a third-party live-attach workflow whose availability depends on OS, permissions, Python build, and tool version. It has overhead and should be rehearsed in a disposable environment first. `objgraph`, `pympler`, and `guppy3` can help inspect object relationships or heap summaries but are third-party tools with different coverage and overhead.

For a **bounded diagnostic snapshot inside a controlled process**, `gc.get_objects()` can be used to count GC-tracked objects by type:

```python
from collections import Counter
import gc

counts = Counter(type(obj).__name__ for obj in gc.get_objects())
for type_name, count in counts.most_common(20):
    print(f"{type_name}: {count}")
```

This is only a histogram of objects tracked by the cyclic garbage collector at that moment. It is not a complete heap census: many objects are not GC-tracked, native allocations are omitted, and the inspection itself allocates objects and can perturb the process. Do not run repeated full-heap scans in a latency-sensitive production worker without approval.

Capture comparable snapshots at defined intervals, then compare growth by allocation site or object type. Avoid dumping every object or local variable by default: this can pause the service, increase memory pressure, and expose secrets. A rising RSS is not alone proof of a Python object leak; native allocations, allocator arenas, fragmentation, memory-mapped files, and caches can also contribute. Compare `tracemalloc`/allocator evidence with RSS and workload metrics before concluding that Python objects are leaking.

### 8.3 Record-and-replay awareness

`rr` is a record-and-replay debugger available for certain Linux environments and workloads. It can be valuable for deterministic native-code failures, but compatibility with CPU features, kernel settings, sandboxing, and runtime behaviour must be verified. Recording adds overhead and can consume significant storage. It is an advanced option for a reproducible lab or approved capture, not a default production intervention.

Deterministic reproduction often starts with less invasive measures: log a redacted input fixture, random seed, dependency versions, relevant timing/concurrency configuration, and the exact command. Do not log secrets merely to make a failure reproducible.

## 9. Production runbook: “service hangs under load”

This runbook is a decision process, not permission to run every command. Adapt it to the service's SLO, incident severity, data classification, and change-control policy. Commands use example PID `12345`; replace it only after verifying the target. Store evidence in a restricted directory, not a public working directory.

### Phase A — Stabilise and preserve

1. **Declare the incident and assign an incident lead.** Record UTC timestamps, deploy version, affected workers, request/queue latency, error rate, CPU, memory, restarts, and dependency health.
2. **Do not kill the process immediately** if a short evidence capture is safe. Do not delay mitigation if the service is causing data corruption, cascading failure, or a severe customer impact.
3. **Check identity and impact.** Confirm PID, container/pod, worker role, deployment version, and whether it is a leader or holds exclusive work. Avoid attaching to the wrong PID after a restart.
4. **Define stop conditions before attach:** unexpected latency increase, service health worsening, storage pressure, evidence containing secrets, a debugger that cannot be detached, or any action outside the approved scope.

### Phase B — classify CPU and wait state

**Linux only:**

```bash
ps -o pid,ppid,stat,pcpu,pmem,nlwp,etime,cmd -p 12345
top -H -p 12345
```

- If one thread is consuming CPU, capture a short stack/profile sample.
- If CPU is near zero, capture thread stacks and inspect dependencies, locks, and I/O waits.
- If the process has crashed, move to core/log evidence; do not attempt a live attach to a dead PID.

**First Python-level capture, if the process already has a supported mechanism:** use its authenticated, local-only diagnostic endpoint or configured `faulthandler` signal. For example, if the service has deliberately registered `SIGUSR1`, then on Linux:

```bash
kill -USR1 12345
```

Do not send `SIGUSR1` unless the application has registered it for this purpose. Otherwise use an approved `py-spy dump --pid 12345` where supported and permitted. Preserve output with timestamps and access controls.

### Phase C — select the next tool conditionally

**Case 1: CPU high and Python samples identify a hot loop**

- Capture a bounded `py-spy record` or equivalent profile.
- Compare the hot path with recent changes and request data shape.
- Reproduce under controlled load, then fix or roll back the application change.
- Do not jump to `gdb` if Python-level evidence already identifies a safe, testable fix.

**Case 2: CPU near zero and stacks remain unchanged**

- Inspect whether stacks are waiting on locks, sockets, queues, futures, or a native call.
- Check the dependent service's health, network timeout, queue consumer state, and retry storm.
- If a Python lock deadlock is plausible, preserve all thread stacks and identify lock ordering/ownership from application instrumentation.
- If a native wait remains plausible, request approval for a brief OS-level capture (`strace` on Linux, or an appropriate platform tool). Treat syscall traces as sensitive.

**Case 3: Python stacks end at a C extension or are insufficient**

- Confirm native extension and shared-library versions.
- If the service can tolerate it and approval is granted, consider a short native backtrace using `gdb -p PID` on Linux, or the platform-appropriate debugger.
- If the process is latency-sensitive, prefer a staging reproduction or a controlled replacement worker over a live debugger.

**Case 4: process crashes or segfaults**

- Preserve stderr/service logs and existing core-dump evidence.
- On systemd Linux, use `coredumpctl list` and `coredumpctl info PID` to locate relevant metadata.
- Analyse the core with the exact executable/libraries and matching symbols. Do not infer the cause from a single Python frame.

### Phase D — preserve evidence package

Store a restricted incident bundle with:

- Incident ID, timestamps, operator, PID/container identity, deployment/build hash, and exact commands used.
- Redacted logs, metrics snapshots, Python stack dumps, bounded profiles, and relevant OS output.
- Core dump only if authorised, encrypted/controlled storage is available, and retention policy permits it.
- Python version/build, OS/kernel, dependency versions, symbols/build IDs where relevant, and whether remote attach/debugging was enabled.
- A hypothesis log: observation → hypothesis → test → result → confidence. Separate facts from guesses.

Hash collected artifacts if chain-of-custody requirements apply. Keep raw sensitive evidence separate from redacted summaries; define who can access each and when it will be deleted.

### Phase E — mitigate, stop, and verify

Choose mitigation based on impact and evidence. Options may include rolling back a release, reducing concurrency, disabling a feature flag, draining a single worker, or restarting a worker. A restart can destroy volatile evidence and may not fix a shared dependency or deterministic deadlock.

**Stop live debugging and move to mitigation immediately if:**

- latency/error rate or customer impact increases after attach;
- the target is the only healthy worker or holds critical state;
- a core/profile is filling disk or increasing memory pressure;
- the tool behaves unexpectedly or cannot be detached safely;
- sensitive data is being captured beyond the approved scope;
- the required permissions would entail an unapproved security-policy change.

After mitigation, verify recovery using service-level indicators, not just process liveness. Record whether the incident recurred and whether the suspected cause was proven. Finish with a postmortem: timeline, impact, root cause (or remaining uncertainty), contributing factors, corrective actions, regression test, owner, due date, and runbook updates.

## 10. Practical experiments

Run experiments only on a local disposable process unless the exercise explicitly says otherwise. Record observations in an experiment notebook.

### Experiment A — post-mortem a real exception

**Question:** Can you move from the visible exception to the frame and value that caused it?

**Setup/command:** Save as `pm_demo.py`:

```python
def calculate(total, count):
    return total / count


def main():
    calculate(10, 0)


if __name__ == "__main__":
    main()
```

Run `python -m pdb pm_demo.py` using CPython 3.12–3.14.

**Procedure:** Let the exception occur. Use `w`/`bt`, move up/down frames, list source, and inspect `total` and `count` where available. Rerun with a nonzero denominator to compare.

**Expected observations:** a `ZeroDivisionError` traceback points to the division. `pdb` can show the call chain and locals for frames that remain in the traceback. Exact prompts/line formatting vary.

**Interpretation:** the traceback identifies the Python path and relevant arguments for this failure.  
**Does not prove:** that production uses the same inputs, or that an unrelated live hang has the same cause.

### Experiment B — dump a live thread hang

**Question:** Can a thread dump reveal a thread waiting on a lock?

**Setup/command:** Save as `hang_demo.py`:

```python
import faulthandler
import threading
import time

faulthandler.enable()
faulthandler.dump_traceback_later(3)
lock = threading.Lock()
lock.acquire()


def waiter():
    with lock:
        print("acquired")

threading.Thread(target=waiter, daemon=True).start()
time.sleep(5)
faulthandler.cancel_dump_traceback_later()
```

Run `python hang_demo.py` in a disposable terminal.

**Procedure:** Observe the traceback dump after the timeout. Compare the main thread and waiter stacks. Repeat with the `lock.acquire()` line removed.

**Expected observations:** the worker can be shown blocked acquiring the lock, while the main thread sleeps. The dump's exact formatting and thread ordering can vary.

**Interpretation:** the worker is waiting for a lock held by the main thread in this constructed example.  
**Does not prove:** every unchanged stack is a deadlock; the lock may eventually be released in a real program.

### Experiment C — compare CPU spin with blocking wait

**Question:** Do high CPU and low CPU hangs produce different sampling evidence?

**Setup/command:** Create two local programs: one repeatedly performs arithmetic in a loop, and one waits on `threading.Event().wait()` without setting the event. Run each in a separate disposable process. If `py-spy` is installed and your OS permits it, use `py-spy top --pid PID` and `py-spy dump --pid PID`.

**Procedure:** Observe CPU use and sample stacks for a bounded interval. Stop the test processes normally when possible.

**Expected observations:** the spin process consumes CPU and samples tend to land in the loop; the waiting process uses little CPU and samples show a wait path. Sampling output depends on timing, interpreter build, and permissions.

**Interpretation:** CPU level helps choose between profiling a hot path and investigating a wait.  
**Does not prove:** a low-CPU process is deadlocked or that a high-CPU process is running Python rather than native code.

### Experiment D — test PEP 768 only on CPython 3.14

**Question:** Can an approved operator attach `pdb` to a disposable worker, and what conditions prevent it?

**Setup/command:** Use a disposable CPython 3.14 process owned by the same user, on a platform/build that supports PEP 768. Start a worker that periodically executes Python bytecode. From a second terminal, run `python -m pdb -p PID` after verifying the PID and reviewing local documentation.

**Procedure:** Start a worker in the disposable environment with a module-level flag that the worker checks periodically, for example `FEATURE_ENABLED = True`. Attach from a second terminal using the same CPython 3.14 minor version:

```text
python -m pdb -p PID
(Pdb) p FEATURE_ENABLED
(Pdb) !FEATURE_ENABLED = False
(Pdb) p FEATURE_ENABLED
(Pdb) continue
```

These are interactive debugger commands, not shell commands. Confirm that the worker observes the change, then resume it with `continue`. This deliberately changes target state and is appropriate only for a disposable worker; never patch a production flag just to learn the mechanism. Test disabling remote debugging only in a separate disposable process, using the documented CPython 3.14 `-X disable_remote_debug` option or `PYTHON_DISABLE_REMOTE_DEBUG=1` environment configuration. Record permission errors and attach timing.

**Expected observations:** when supported and permitted, the debugger can attach when the target reaches an appropriate safe point. A blocked target may not respond promptly; disabled or unsupported builds may reject or fail to service the request. The local debugger and target must have matching CPython major/minor versions.

**Interpretation:** PEP 768 provides a controlled attach mechanism, not guaranteed immediate execution.  
**Does not prove:** all OSes, Python distributions, containers, or hardened production services will permit attach.

### Experiment E — practise a core-dump workflow without crashing production

**Question:** What evidence is required to interpret a core file correctly?

**Setup/command:** Use a disposable native test program or an approved test fixture in an isolated VM/container configured for core dumps. Check `ulimit -c`, `core_pattern`, and whether `coredumpctl` is present before generating any crash.

**Procedure:** Generate a test dump only if your lab policy permits it. Preserve the executable, libraries, symbols, and exact build identifiers. Open the dump with the matching native debugger and inspect thread backtraces.

**Expected observations:** a core is produced only if OS and service policy permit it. Missing symbols reduce the usefulness of the backtrace.

**Interpretation:** core analysis requires build-matched artifacts and careful handling.  
**Does not prove:** that a Python traceback alone explains a native crash, or that the same dump policy applies in containers and production.

### Experiment F — four-symptom incident practicum

**Question:** Can you select evidence based on the failure mode instead of using one debugger for every problem?

Use four independent disposable programs/processes; never combine the crash case with the other experiments, and never run the crash case in your working interpreter, notebook kernel, or production service.

1. **Deadlock:** use Experiment B or the opposite-lock-order program in Section 5.3. Capture at least two thread dumps and describe the suspected wait cycle.
2. **Native crash:** create a separate `ctypes_crash_child.py` containing the following intentionally destructive code, then run it only inside a disposable VM/container where a process crash is acceptable. The child may terminate with a segmentation fault; do not expect Python exception handlers to catch it.

   ```python
   # INTENTIONALLY CRASHES THE CHILD PROCESS. Isolated lab only.
   import ctypes
   ctypes.string_at(0)
   ```

   Preserve the child exit status, stderr/faulthandler output (if enabled before the fault), and a core only if the lab's policy and storage permit. Do not run this example to “test” a production debugger.
3. **Memory growth:** in a separate process, run this bounded `tracemalloc` comparison, then compare it with the type histogram in Section 8.2:

   ```python
   import gc
   import tracemalloc

   # A deliberate, bounded retention bug: the list keeps each batch alive.
   retained = []
   tracemalloc.start()
   baseline = tracemalloc.take_snapshot()
   for batch in range(3):
       retained.extend(
           {"payload": "x" * 256, "batch": batch, "index": i}
           for i in range(1_000)
       )
   grown = tracemalloc.take_snapshot()
   print(grown.compare_to(baseline, "lineno")[:5])
   retained.clear()
   gc.collect()
   released = tracemalloc.take_snapshot()
   print(released.compare_to(baseline, "lineno")[:5])
   ```

   The retained list intentionally keeps three bounded batches alive; clearing it should reduce the live traced allocation difference, though allocator behaviour means the values need not return exactly to baseline. This is a controlled retention demonstration, not a production leak proof. Explain why allocator behaviour, untracked objects, and native allocations mean that neither the histogram nor RSS alone proves a leak.
4. **CPU spin:** in a separate process, run a finite or externally stoppable arithmetic loop. Capture `top -H`, a bounded `py-spy dump`/profile where permitted, and (only if needed and approved) native/perf evidence. Ensure the test can be stopped without affecting other processes.

For each case, write a mini-postmortem with symptom, observations, competing hypotheses, tool/permission assumptions, evidence collected, confidence, mitigation, and a regression test. Record commands that were actually run separately from commands that were unavailable or merely proposed. The crash and attach exercises are not to be executed on a production host.

## 11. Troubleshooting guide

| Symptom | Likely next step | Common trap |
|---|---|---|
| `pdb.pm()` says no recent exception | Reproduce in the same interactive process or retain/pass the traceback to `pdb.post_mortem(tb)` | Expecting it to recover an exception from an unrelated process |
| `py-spy` cannot attach | Verify PID, UID/capabilities, ptrace policy, namespace, tool compatibility, and target build | Assuming installation grants process access |
| `pdb -p PID` is unsupported | Check Python is CPython 3.14+, build/platform support, and remote-debug disablement | Assuming Python 3.12/3.13 has PEP 768 |
| Remote attach waits indefinitely | Target may be blocked in native code or I/O, or may not reach a safe point | Repeatedly injecting scripts or escalating privileges blindly |
| Thread dumps show no obvious cause | Repeat snapshots; inspect native stacks, dependency health, locks, and system calls | Treating a Python stack as a full native process snapshot |
| Core dump missing | Check resource limits, `core_pattern`, service manager, container policy, storage and permissions | Assuming `ulimit` in a new shell changes an existing service |
| `gdb` shows addresses but no functions | Obtain matching debug symbols and exact executable/shared libraries | Using symbols from a different build |
| Service worsens during debugging | Detach/stop capture and follow the incident stop condition | Continuing to collect evidence at the expense of availability |
| Logs are absent after a crash | Check buffering and configure durable structured logging; preserve stderr | Assuming `finally`, `atexit`, or Python logging always runs on a segfault |
| Evidence contains secrets | Restrict access, redact summaries, follow incident retention policy | Attaching raw stack dumps/core files to public tickets |

## 12. Common misconceptions

- **“Post-mortem debugging can diagnose any hang.”** No. It inspects an exception traceback. A live hang needs live stack, task, native, or OS evidence.
- **“A thread dump proves deadlock.”** No. A snapshot shows where execution is observed. Repeated evidence and lock/dependency analysis are needed to establish a deadlock.
- **“`faulthandler` is a native debugger.”** No. It provides constrained Python traceback evidence and selected fault handling, not a full native backtrace.
- **“`py-spy` always attaches without privileges.”** No. OS policy, containers, build compatibility, and permissions can block it.
- **“PEP 768 makes remote debugging safe by default.”** No. It adds a safer protocol for executing code at an interpreter safe point, but authorised access still means code execution inside the target process and can destabilise production.
- **“`gdb` or `strace` is harmless because it is read-only.”** Attaching can pause the process, change timing, add overhead, and expose memory or syscall data.
- **“A core file is just a traceback.”** It may contain most of process memory and native thread state; treat it as sensitive.
- **“Restart first, investigate later.”** Sometimes mitigation must be immediate, but if safe, collect bounded evidence before restart because restart destroys volatile state. Availability and data safety take precedence over evidence collection.
- **“An exception hook catches every crash.”** Python hooks do not reliably run for segfaults, forced termination, `os._exit()`, or all native failures.

## 13. Concept map: evidence before hypothesis

```text
Observe symptom
   ↓
Classify: exception | high CPU | low CPU | crash | memory growth
   ↓
Capture least-invasive evidence
   ├─ exception → traceback / pdb post-mortem
   ├─ live Python state → faulthandler / thread or task stacks / py-spy
   ├─ native boundary → symbols + native debugger / OS tool, if approved
   └─ crash → logs + core dump + exact executable and libraries
   ↓
Compare snapshots and test competing hypotheses
   ↓
Reproduce in a controlled environment
   ↓
Mitigate and verify service-level recovery
   ↓
Postmortem: timeline, root cause/confidence, regression test, owners, runbook update
```

The discipline is to separate **observation** (e.g. “worker stack remains at `Lock.acquire` across three snapshots”) from **hypothesis** (e.g. “lock-order deadlock”) and from **confirmed cause** (e.g. a reproduced lock cycle with identified owners).

## 14. Self-check questions and answers

### 1. How do you diagnose a Python process stuck with no CPU use?

**Answer:** Verify the process and affected worker; capture all Python thread stacks using a preconfigured `faulthandler` dump, an approved in-process diagnostic, or `py-spy`; repeat snapshots; check I/O, queues, dependency health, and lock waits; use native/OS tools only if the evidence indicates a native or kernel wait and permissions/impact are acceptable. Near-zero CPU alone does not prove deadlock.

### 2. What does PEP 768 add, and what are the security trade-offs?

**Answer:** PEP 768 is Final and applies to CPython 3.14. It defines `sys.remote_exec(pid, script)` and underpins `python -m pdb -p PID`. The script path is executed by the target's main thread at a safe point; the call returns immediately and has no completion acknowledgement. The caller and target must use the same CPython major/minor version (exact version for prereleases). OS permissions still gate access. Because the script runs inside the target with its privileges, it can inspect secrets and change state. CPython 3.14 documents `PYTHON_DISABLE_REMOTE_DEBUG=1`, `-X disable_remote_debug`, and a `--without-remote-debug` build option; support is platform/build dependent.

### 3. Write a runbook for “service hangs under load.” What evidence should be preserved?

**Answer:** Declare the incident; record timestamps, deployment, impact, metrics, and target identity; classify CPU and wait state; capture bounded thread/profile evidence; escalate to native/core tools only conditionally; preserve redacted logs, stack dumps, profiles, build/dependency/symbol metadata, and an incident hypothesis log; protect raw dumps/core files; define stop conditions; mitigate, verify service-level recovery, and write a postmortem with a regression test and runbook update. For a hot thread, use Linux `top -H -p PID` → `py-spy dump --pid PID`/bounded profile → `perf top -p PID` or `py-spy record --native --pid PID --duration 20 --output native-profile.svg` only if supported → approved native backtrace or `gcore` only if necessary and safe. Stop if latency, disk pressure, or data exposure worsens.

### 4. Why is `pdb.pm()` different from `python -m pdb -p PID`?

**Answer:** `pdb.pm()` enters post-mortem inspection of a traceback already available to the current interactive process. `python -m pdb -p PID` is a CPython 3.14 remote-attach path based on PEP 768 and requires a live compatible target plus OS permissions.

### 5. What can a Python thread dump not tell you?

**Answer:** It may not expose native C/C++ frames, the owner of a native mutex, kernel-level details, or the state of an external service. Combine it with repeated snapshots, metrics, native backtraces, or OS evidence when warranted.

### 6. Why should you avoid collecting all locals or a core dump by default?

**Answer:** They can contain credentials, personal data, request bodies, keys, and large object graphs; capture can pause the process, increase resource pressure, or fill storage. Use data minimisation, access controls, retention limits, and explicit approval.

### 7. When is `strace` appropriate?

**Answer:** On Linux, with appropriate permission and approval, it can show system calls, signals, and blocking patterns when Python stacks do not explain the wait. It has overhead and does not itself prove a Python-level deadlock. It is not a portable command for macOS or Windows.

## 15. Summary

Post-mortem debugging examines an exception that has already happened; live-hang debugging collects evidence from a process that is still running. Preserve exception chains and relevant inputs, use `pdb` for Python-level failures, and use `faulthandler`, thread/task dumps, and `py-spy` to understand live state. Escalate to core dumps, `gdb`, `strace`, or platform-native tools only when the symptom warrants it and the operating system, symbols, permissions, and service risk have been checked. PEP 768 improves external attach support in CPython 3.14 but does not make attach universally available, immediate, or harmless. In production, evidence collection must be bounded and secure; availability and safety take precedence over a perfect diagnosis.

## References

Prefer documentation for the exact interpreter, operating system, debugger, and installed tool version.

- Python 3.14 `pdb`: https://docs.python.org/3.14/library/pdb.html
- Python 3.14 `faulthandler`: https://docs.python.org/3.14/library/faulthandler.html
- Python 3.14 `traceback`: https://docs.python.org/3.14/library/traceback.html
- Python 3.14 `sys`: https://docs.python.org/3.14/library/sys.html
- Python 3.14 remote debugging HOWTO: https://docs.python.org/3.14/howto/remote_debugging.html
- PEP 768 — Safe external debugger interface for CPython: https://peps.python.org/pep-0768/
- Python 3.14 “What’s New”: https://docs.python.org/3.14/whatsnew/3.14.html
- `py-spy` project and usage: https://github.com/benfred/py-spy
- GNU GDB manual: https://sourceware.org/gdb/documentation/
- `strace` manual: https://strace.io/
- Python `asyncio` task introspection: https://docs.python.org/3.14/library/asyncio-task.html
