# Lesson 04 — Subprocess and Running External Commands Safely

> **Target:** Python 3.12+ · **Module:** Stage 1, Module 13 — Standard Library Toolkit  
> **Focus:** safe process invocation, output capture, timeouts, lifecycle management, and tests for data-engineering tools.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain when a Python program should invoke an external executable and what a process exit code means.
- Use `subprocess.run()` with an argument list, `check`, captured output, explicit encoding, input, environment, working directory, and timeout.
- Interpret `CompletedProcess`, `CalledProcessError`, `TimeoutExpired`, and launch errors without confusing them.
- Choose text or binary mode deliberately and handle output that is not valid UTF-8.
- Use `Popen`, `PIPE`, `communicate()`, and safe streaming patterns without deadlocking on full pipe buffers.
- Avoid shell injection, executable/PATH substitution, accidental secret disclosure, and uncontrolled child processes.
- Build a typed wrapper with a documented result and safe error context.
- Test success, non-zero exit, timeout, missing executables, captured streams, and fake tools with `pytest`.

## 1. Prerequisites and roadmap boundaries

This lesson follows the Stage 1 roadmap's **Phase B — Files, Processes and Local Data** sequence: `03-shutil-tempfile-zipfile-and-tarfile.md`, then this lesson, then `05-sqlite3-embedded-database.md`.

Prerequisites from earlier Stage 1 lessons:

- **Files, `pathlib`, and encodings** (Module 1.5, lessons 01–05): working directories, paths, and text decoding.
- **Standard streams and exit codes** (Module 1.5, lesson 07): stdin, stdout, stderr, and process status.
- **Logging versus print** (Module 1.5, lesson 08) and **environment configuration** (Module 1.5, lesson 09): operational diagnostics and child environments.
- **Exceptions and validation** (Modules 1.3 and 1.10): clear error boundaries.
- **Testing with pytest and monkeypatching** (Module 1.7): test external-command behavior without relying on a real service.
- **Safe writes and idempotency** (Module 1.10): make retries safe and avoid treating a successful process launch as a successful whole pipeline.

This lesson is about the Python `subprocess` API and process safety. It is not a general shell-scripting course. It previews `asyncio.create_subprocess_exec()` but does not teach asynchronous orchestration in depth. Logging, configuration, exception design, and testing are applied rather than repeated from scratch.

## 2. Process fundamentals

A **subprocess** is a separate operating-system process launched by the current Python process. Typical data-engineering examples include calling `git`, a database client, `ffmpeg`, `pdftotext`, a compressor, or a vendor-provided command-line utility when no suitable Python API exists.

A process has a lifecycle and streams:

- **stdin**: data sent to the child (`input=` or `stdin=PIPE`).
- **stdout**: normal output (`stdout=PIPE` or `capture_output=True`).
- **stderr**: diagnostics (`stderr=PIPE` or captured separately).
- **return code**: conventionally `0` means success; a non-zero value usually signals failure. The exact meaning is defined by the invoked program.

Launching a process is not the same as validating its result. A robust pipeline checks the exit status, bounds execution time, controls the executable and environment, handles output safely, and defines what happens on failure.

### 2.1 `run()` is the default

For a command that should complete before Python continues, start with `subprocess.run()`. It waits for completion and returns a `CompletedProcess` unless `check=True` raises for a non-zero status.

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-c", "print('ready')"],
    check=True,
    capture_output=True,
    text=True,
    encoding="utf-8",
    timeout=5,
)
print(result.returncode)
print(result.stdout.strip())
print(result.stderr)
```

Expected output:

```text
0
ready

```

This uses the current Python interpreter as the executable, so it does not depend on `echo`, `git`, or another optional tool being installed. The third printed value is an empty string, which produces the final blank line.

Important arguments:

| Argument | Behavior | Practical guidance |
|---|---|---|
| `args` | Sequence of executable and arguments | Prefer a list/tuple; do not interpolate untrusted text into a shell command. |
| `check=True` | Raises `CalledProcessError` for non-zero exit | Use when non-zero means the operation failed. |
| `capture_output=True` | Captures stdout and stderr using pipes | Output is buffered in memory; avoid for unbounded logs or huge binary output. |
| `text=True` | Requests text mode | Also specify `encoding=` and a deliberate `errors=` policy where relevant. |
| `timeout=seconds` | Bounds the wait for completion | Choose a workload-specific value; a timeout is a failure policy, not a guarantee that grandchildren are gone. |
| `cwd=path` | Sets child working directory | Use an explicit trusted directory when relative paths matter. |
| `env=mapping` | Supplies the child's environment | Supplying it replaces normal inheritance; copy `os.environ` if inheritance is intended. |
| `input=value` | Sends data to stdin and closes it | `input` is incompatible with an explicit `stdin=` argument in `run()`. |

### 2.2 `CompletedProcess` and common failures

`CompletedProcess` exposes `args`, `returncode`, `stdout`, and `stderr`. In text mode the captured streams are strings on normal completion; in binary mode they are bytes.

- `subprocess.CalledProcessError`: a process ran and exited non-zero while `check=True` was used. It includes `returncode` and may include captured `stdout`/`stderr`.
- `subprocess.TimeoutExpired`: the timeout elapsed before completion. Captured output on this exception may be bytes even when text mode was requested; do not assume its type without checking.
- `FileNotFoundError`: the executable could not be found (or an executable path component is missing).
- `PermissionError` / `OSError`: launch failures such as permission denial or OS-level resource errors.

```python
import subprocess
import sys

try:
    subprocess.run(
        [sys.executable, "-c", "import sys; print('bad', file=sys.stderr); sys.exit(7)"],
        check=True, capture_output=True, text=True, timeout=5,
    )
except subprocess.CalledProcessError as exc:
    print(exc.returncode)
    print(exc.stderr.strip())
```

Expected output:

```text
7
bad
```

For production code, be careful about printing `exc.stderr` blindly: diagnostics can contain tokens, connection strings, SQL, file paths, or personal data. Capture what you need, redact it, and log only the safe fields.

### 2.3 Send input to a child

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
    input="batch-42\n",
    text=True,
    encoding="utf-8",
    capture_output=True,
    check=True,
    timeout=5,
)
print(result.stdout.strip())
```

Expected output: `BATCH-42`.

Use `input=` for finite payloads. For large input, prefer streaming through `Popen.stdin` with a carefully managed lifecycle, or use a file/IPC interface if that is simpler and safer.

## 3. Argument lists, shell parsing, and injection

### 3.1 Why argument lists are safer

Given:

```python
import subprocess
import sys

user_supplied_path = "data files/input.csv"
subprocess.run(
    [sys.executable, "-c", "import sys; print(sys.argv[1:])", "--", user_supplied_path],
    check=True,
    timeout=5,
)
```

Expected output: `['--', 'data files/input.csv']`. The example demonstrates that the path with spaces remains one argument; `--` here is simply passed to the Python child, not interpreted by Python itself.

Python passes the path as one argument. Spaces, semicolons, dollar signs, and shell metacharacters are not reinterpreted by a shell because `shell=False` is the default.

By contrast, this pattern is dangerous:

```python
# UNSAFE demonstration: POSIX shell only; controlled harmless input.
import subprocess

user_text = "hello; printf 'INJECTED\\n'"
command = f"printf '%s\\n' {user_text}"
result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
print(result.stdout, end="")
```

Expected output on a POSIX shell:

```text
hello
INJECTED
```

The shell executes the `printf` added after the semicolon. This deliberately vulnerable demonstration is for a local lesson only; never use this pattern with external input.

On POSIX, if `user_text` is `hello; printf 'INJECTED\n'`, the shell treats the semicolon as a command separator. The input is no longer just data: it changes the command program. This is command injection.

The safe replacement passes the value as one argument to a known executable:

```python
import subprocess
import sys

user_text = "hello; printf 'INJECTED\\n'"
result = subprocess.run(
    [sys.executable, "-c", "import sys; print(sys.argv[1])", user_text],
    check=True, capture_output=True, text=True, encoding="utf-8", timeout=5,
)
print(result.stdout.strip())
```

Expected output is the literal input, not a second command:

```text
hello; printf 'INJECTED\n'
```

This example is portable because it invokes Python directly. The unsafe example is intentionally labelled POSIX-oriented and is illustrative; do not copy it into production.

### 3.2 Validation, executable selection, and PATH

Argument lists prevent shell metacharacter interpretation, but they do not make every argument semantically safe. For example, a user-controlled value beginning with `-` might be interpreted as an option by the target program. Defenses include:

1. Select the executable from a fixed allow-list; never let a request choose an arbitrary program.
2. Validate arguments against the target tool's expected grammar and bounds.
3. Use `--` to end option parsing when the target program supports it (this is a convention, not a universal feature).
4. Use a trusted absolute executable path for privileged or security-sensitive operations. A bare name is resolved through `PATH`, which may be attacker-controlled or unexpectedly modified.
5. Construct a minimal, deliberate environment and trusted `cwd` where practical.
6. Run with least privilege and appropriate OS/container isolation. `subprocess` is not a sandbox.

`shlex.quote()` and `shlex.split()` are **Unix-shell tools**, not universal cross-platform command-line serializers. They can help with a POSIX shell string when a string is unavoidable, but the result is not a defense against all injection, option confusion, or platform-specific parsing. Do not use `shlex.quote()` to construct a Windows command line.

```python
import shlex

parts = ["tool", "--label", "data set; not a command"]
print(shlex.join(parts))  # POSIX-shell representation for display/use in a POSIX shell
print(shlex.quote("data set; not a command"))  # quote one token for POSIX shell syntax
print(shlex.split("tool --label 'data set'"))
```

Expected output:

```text
tool --label 'data set; not a command'
'data set; not a command'
['tool', '--label', 'data set']
```

Prefer not to create a shell string in the first place. Logging a shell-quoted representation is not the same as executing it safely.

## 4. Working directory, environment, encoding, and streams

### 4.1 `cwd=` and `env=`

`cwd=` determines where relative paths in the child are interpreted. Use a known directory instead of relying on the parent process's current working directory.

When you pass `env=`, it replaces the child's inherited environment. Copy the parent environment before adding overrides if inheritance is intended:

```python
import os
import subprocess
import sys

child_env = os.environ.copy()
child_env["PIPELINE_MODE"] = "validation"
result = subprocess.run(
    [sys.executable, "-c", "import os; print(os.environ['PIPELINE_MODE'])"],
    env=child_env,
    check=True,
    capture_output=True,
    text=True,
    encoding="utf-8",
    timeout=5,
)
print(result.stdout.strip())
```

Expected output: `validation`.

Avoid passing secrets in command-line arguments: process listings, crash reports, and diagnostic logs may expose them. Environment variables are also not a perfect secret store, but can be preferable to arguments for some tools. Use the platform's secret-management facilities and narrowly scoped credentials when available; never dump the entire environment into logs.

### 4.2 Text versus binary mode

Use `text=True` for human-readable text. Set `encoding="utf-8"` only when the child output contract is UTF-8; some tools use the locale encoding or a configurable encoding. `errors="replace"` can preserve observability when invalid sequences occur, but it loses information. For exact output, binary mode (`text=False`, the default) avoids implicit decoding:

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xff\\x00')"],
    capture_output=True,
    check=True,
    timeout=5,
)
print(result.stdout)
```

Expected output: `b'\xff\x00'`.

Do not silently decode arbitrary binary output as UTF-8. Conversely, do not treat text as bytes without documenting the encoding boundary.

### 4.3 Return codes and signals

A return code of zero commonly means success. Non-zero meanings are tool-specific. On POSIX, Python represents termination by signal `N` as a negative return code `-N` (for example, `-9` indicates `SIGKILL`). Windows does not use this negative-signal convention in the same way. Do not assume `-9` means the same thing on every platform or that all tools use shell-style exit codes consistently.

## 5. A safe, typed wrapper

A wrapper centralizes timeout policy, executable allow-listing, environment handling, and error context. It should not blindly log all arguments or stderr. The example below deliberately stores only the executable name and status in the custom exception. It suppresses display of the underlying launch/timeout exception because that exception can contain the full command or captured output. This trades away the default chained traceback for safer diagnostics; Python still retains the suppressed exception as internal context, so do not serialize or log exception internals indiscriminately.

```python
from __future__ import annotations

import math
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping, Sequence, Collection


@dataclass(frozen=True)
class CommandResult:
    """Successful command result; output is text decoded with the chosen encoding."""
    executable: str
    returncode: int
    stdout: str
    stderr: str


class CommandExecutionError(RuntimeError):
    """Safe summary of a launch, timeout, or non-zero-exit failure."""

    def __init__(self, executable: str, reason: str, *, returncode: int | None = None):
        # Keep only a basename in the public message; absolute paths can expose deployment details.
        self.executable = Path(executable).name or "<executable>"
        self.reason = reason
        self.returncode = returncode
        suffix = "" if returncode is None else f" (return code {returncode})"
        super().__init__(f"Command {self.executable!r} {reason}{suffix}; arguments and output omitted")


def run_tool(
    args: Sequence[str],
    *,
    allowed_executables: Collection[str],
    timeout: float = 30.0,
    cwd: str | os.PathLike[str] | None = None,
    env_overrides: Mapping[str, str] | None = None,
    input_text: str | None = None,
) -> CommandResult:
    """Run an allow-listed executable without a shell.

    `allowed_executables` must contain the exact executable string supplied as args[0].
    For high-trust operations, use an absolute executable path in the allow-list.
    Output is buffered in memory; use a streaming design for large/unbounded output.
    """
    if isinstance(args, (str, bytes)) or not isinstance(args, Sequence):
        raise TypeError("args must be a sequence of argument strings, not a command string")
    argv = tuple(args)  # snapshot once so validation and execution use the same arguments
    if not argv:
        raise ValueError("args must not be empty")
    if not all(isinstance(arg, str) for arg in argv):
        raise TypeError("all command arguments must be strings")
    if not argv[0] or any("\x00" in arg for arg in argv):
        raise ValueError("executable and arguments must be non-empty where required and contain no NUL")

    if isinstance(allowed_executables, (str, bytes)):
        raise TypeError("allowed_executables must be a collection of complete executable strings")
    try:
        allowed = frozenset(allowed_executables)
    except TypeError as exc:
        raise TypeError("allowed_executables must be an iterable of strings") from exc
    if not all(isinstance(item, str) and item and "\x00" not in item for item in allowed):
        raise TypeError("allowed_executables must contain non-empty executable strings")
    executable = argv[0]
    if executable not in allowed:
        raise ValueError("executable is not allow-listed")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a finite positive number")

    if env_overrides is not None:
        if not isinstance(env_overrides, Mapping):
            raise TypeError("env_overrides must be a mapping of environment names to strings")
        for key, value in env_overrides.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("environment names and values must be strings")
            if not key or "=" in key or "\x00" in key or "\x00" in value:
                raise ValueError("environment names and values must be valid OS environment strings")

    child_env = os.environ.copy()
    if env_overrides:
        child_env.update(env_overrides)

    try:
        completed = subprocess.run(
            list(argv),
            check=False,
            shell=False,
            cwd=Path(cwd) if cwd is not None else None,
            env=child_env,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        # Suppress the displayed exception chain: TimeoutExpired.cmd can contain secrets.
        raise CommandExecutionError(executable, "timed out") from None
    except FileNotFoundError:
        raise CommandExecutionError(executable, "could not be launched") from None
    except (PermissionError, OSError, UnicodeError):
        # OS/decoding exceptions can contain paths, arguments, or output; do not display them.
        raise CommandExecutionError(executable, "failed during launch or output decoding") from None

    if completed.returncode != 0:
        raise CommandExecutionError(
            executable, "exited unsuccessfully", returncode=completed.returncode
        )
    return CommandResult(
        executable=Path(executable).name or "<executable>",
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
```

Example use:

```python
import sys

result = run_tool(
    [sys.executable, "-c", "print('validated')"],
    allowed_executables={sys.executable},
    timeout=5,
)
print(result.returncode, result.stdout.strip())
```

Expected output: `0 validated`.

**Design trade-offs and limitations:**

- The allow-list checks the exact executable string, but if that string is a bare name, the OS still resolves it through `PATH`. Prefer a trusted absolute path when executable substitution would be a security issue. If an override changes `PATH`, it can affect bare-name lookup even though the name is allow-listed.
- `env_overrides` inherits the parent environment. This is convenient but not a minimal environment; production callers should decide which variables are necessary and avoid inheriting untrusted `PATH`, loader variables, or credential-bearing values where relevant.
- Captured stdout/stderr are buffered in memory. For huge output, use streaming with an explicit output-size/log-retention policy.
- A timeout on `run()` terminates and waits for the direct child according to the standard-library implementation, but should not be treated as a guarantee that independently spawned grandchildren have exited. Use process-group/session management where that threat matters.
- `CommandExecutionError` intentionally omits captured output. If diagnostics are needed, add a deliberate redaction/allow-list policy at the application boundary rather than automatically embedding stderr in exception messages.
- The wrapper assumes UTF-8 output. If a tool has another documented encoding, make it an explicit configuration choice or use binary output.

## 6. Timeouts and lifecycle control

### 6.1 Timeout behavior with `run()`

```python
import subprocess
import sys

try:
    subprocess.run(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        timeout=0.2,
        check=True,
        capture_output=True,
        text=True,
    )
except subprocess.TimeoutExpired:
    print("command timed out")
```

Expected output: `command timed out`.

Timeouts need realistic budgets. A timeout that is too short creates false failures; no timeout can hang a worker indefinitely. Retry only when the operation is safe to retry. A killed process may have performed partial external side effects, so use idempotency keys, temp outputs, or reconciliation rather than assuming timeout means “nothing happened.”

### 6.2 `Popen`, `PIPE`, and `communicate()`

Use `Popen` when you need ongoing interaction, streaming, process lifecycle control, or coordination with multiple processes. If both stdout and stderr are pipes, reading only one stream while the child fills the other can deadlock: the child blocks writing to a full pipe while the parent waits for output from the first pipe.

For finite output, use `communicate()` to drain stdout and stderr together:

```python
import subprocess
import sys

process = subprocess.Popen(
    [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
)
try:
    stdout, stderr = process.communicate(timeout=5)
except subprocess.TimeoutExpired:
    process.kill()
    stdout, stderr = process.communicate()
    raise
finally:
    if process.poll() is None:
        process.kill()
        process.wait()

print(stdout.strip())
print(stderr.strip())
print(process.returncode)
```

Expected output:

```text
out
err
0
```

`communicate()` avoids the classic two-pipe deadlock, but it buffers all output in memory. It is not a solution for unlimited output.

### 6.3 Streaming without the two-pipe deadlock

If you want line-by-line output and do not need separate stderr, redirect stderr to stdout so the parent has only one pipe to drain. This example streams one merged output pipe and cleans up the direct child if iteration exits through an exception. **It does not impose a hard wall-clock timeout**: iteration can block waiting for the next newline or EOF. The next paragraph explains this limitation; do not use this loop alone when a strict deadline is required.

```python
import subprocess
import sys

process = subprocess.Popen(
    [sys.executable, "-u", "-c", "import time; print('start', flush=True); time.sleep(0.1); print('done', flush=True)"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    bufsize=1,
)
try:
    assert process.stdout is not None
    for line in process.stdout:
        print(f"child: {line.rstrip()}")
    returncode = process.wait(timeout=5)
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, process.args)
finally:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    if process.stdout is not None:
        process.stdout.close()
```

Expected output:

```text
child: start
child: done
```

This is suitable when a merged log stream is acceptable. It does **not** implement a hard timeout while blocked waiting for a line: if the child emits no newline and remains alive, the `for` loop can wait indefinitely. The `finally` block only runs once iteration returns or raises; it cannot interrupt a blocking `readline()` by itself. For a strict streaming deadline, use a reader thread/async I/O with coordinated timeout, or use `communicate(timeout=...)` if buffering is acceptable. Always close streams and wait for the child.

### 6.4 Managing descendants and process groups

`Popen.terminate()` and `Popen.kill()` target the direct child. They do not automatically guarantee termination of every descendant the child created.

On POSIX, `start_new_session=True` starts the child in a new session. If you need to stop the entire process group, a common pattern is to send a signal to the group using `os.killpg(process.pid, signal.SIGTERM)`, wait for a grace period, then send `SIGKILL` if necessary. This is platform-specific and should be implemented carefully: process identifiers can be reused, and the process may already have exited. Do not casually kill a group unless your program created and owns that group.

```python
# POSIX-only pattern sketch; test in a controlled environment before production use.
import os
import signal
import subprocess

proc = subprocess.Popen(
    ["/absolute/path/to/known-tool", "--bounded-task"],
    start_new_session=True,
)
try:
    proc.wait(timeout=30)
except subprocess.TimeoutExpired:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
```

This sketch assumes the launched process is the leader of a session/group that your code owns. **It is best-effort, not a complete process-tree supervisor.** Waiting for the leader does not prove every descendant has exited; a descendant can ignore `SIGTERM`, outlive the leader, or escape the group. The sample escalates only if the leader itself fails to exit within the grace period, so it must not be represented as a guarantee that all descendants are killed. For strict cleanup, use a supervisor or OS containment mechanism designed to track the whole workload (for example, a service manager/cgroup on Linux or a Windows Job Object). Real applications must also handle `PermissionError`, shutdown races, and platform differences. It is not a portable Windows recipe.

On Windows, process creation flags such as `CREATE_NEW_PROCESS_GROUP` and console-control events have different semantics; terminating a process tree robustly may require Windows-specific APIs or a job object. Avoid claiming that `terminate()` is equivalent to killing a whole tree on every OS.

## 7. Pipelines, resource controls, and restricted environments

### 7.1 Piping one process into another

If you connect one child’s stdout to another child’s stdin, close the parent's copy of the upstream stdout after starting the downstream process so the upstream can observe that no reader remains if the downstream exits. Also manage both processes' return codes and avoid leaving either child running if one fails. For many workflows, writing a temporary file is simpler and easier to recover than a live process pipeline. When a direct pipeline is appropriate, close the parent's duplicate of the producer's stdout after wiring it to the consumer. This allows the producer to observe a broken pipe if the consumer exits early. Check both return codes and clean up both children:

```python
import subprocess
import sys

producer = subprocess.Popen(
    [sys.executable, "-c", "print('row')"],
    stdout=subprocess.PIPE,
)
consumer = None
try:
    assert producer.stdout is not None
    consumer = subprocess.Popen(
        [sys.executable, "-c", "import sys; print(sys.stdin.read().upper(), end='')"],
        stdin=producer.stdout,
    )
    producer.stdout.close()  # close the parent's copy of the pipe
    consumer.wait(timeout=5)
    producer.wait(timeout=5)
    if producer.returncode != 0:
        raise subprocess.CalledProcessError(producer.returncode, producer.args)
    if consumer.returncode != 0:
        raise subprocess.CalledProcessError(consumer.returncode, consumer.args)
finally:
    if consumer is not None and consumer.poll() is None:
        consumer.kill()
        consumer.wait()
    if producer.poll() is None:
        producer.kill()
        producer.wait()
    if producer.stdout is not None and not producer.stdout.closed:
        producer.stdout.close()
```

Expected output: `ROW`. This minimal example leaves the consumer's output attached to the parent terminal; it avoids creating another pipe. In production, define timeout policy for both processes and decide how to handle partial output or a consumer that exits early.

Do not combine `stdout=PIPE` and `stderr=PIPE` with manual sequential reads unless you have a strategy to drain both concurrently. `communicate()` is the default for bounded output.

### 7.2 POSIX `resource` module (awareness)

The standard-library `resource` module is Unix/POSIX-oriented and is not available on standard Windows Python. On supported systems, `resource.setrlimit()` can constrain some process resources, such as CPU time or file size, but:

- available resource constants and semantics differ by OS;
- limits may be inherited by children;
- resource limits are not a complete sandbox and do not replace OS/container isolation;
- a process may still consume network access, memory, or other resources not adequately constrained by a chosen limit.

Use OS-level least privilege, restricted filesystem access, network policy, containers/sandboxing, and quotas where the threat model requires them. On Unix, dropping UID/GID privileges is possible in appropriate deployment designs, but should be configured deliberately and tested; a dedicated service account or container policy is often safer than ad hoc privilege changes in application code. Never treat an arbitrary third-party executable as safe merely because it was launched without a shell.

### 7.3 `asyncio.create_subprocess_exec()` awareness

For many concurrent subprocesses in an asynchronous application, `asyncio.create_subprocess_exec()` provides an async process API. It follows the same basic safety rule: pass the executable and arguments separately rather than building a shell command. Async code still needs output-draining, timeouts, cancellation cleanup, and process-tree decisions. It is a preview here; learn `asyncio` separately before mixing it into a synchronous ETL worker.

## 8. Windows and portability notes

- Argument passing differs between POSIX and Windows because Windows process creation uses command-line serialization that the child runtime parses. Python handles normal argument sequences, but unusual executables may implement their own parsing.
- `.bat` and `.cmd` files are shell-like command scripts on Windows and may be launched through a system shell even when `shell=False`. Do not assume `shell=False` makes arbitrary untrusted arguments to batch files safe. Prefer a real executable or a well-defined API and avoid batch scripts with untrusted values. If you must launch a batch file with untrusted arguments, consult the exact Python version's `subprocess` security note: it documents a special case where `shell=True` may allow Python to apply escaping. This exception is not a general reason to use `shell=True` for ordinary executables.
- `shlex` is designed around Unix shell syntax and is not a universal quoting tool.
- POSIX negative return codes represent signal termination; Windows status codes have different semantics.
- `start_new_session`, `os.killpg`, and `resource` examples are POSIX-specific. Windows process groups and process-tree cleanup require different handling.
- Executable discovery through `PATH` varies by environment. Use an absolute trusted executable path when predictable resolution matters.

## 9. Logging without leaking secrets

Logs should answer: which approved tool was invoked, when, with what timeout, what return code, how long it took, and what safe correlation/job ID applies. Avoid logging raw argument lists, environment dictionaries, stdin, captured output, credentials, signed URLs, or full exception strings by default.

Prefer a safe summary such as:

```python
logger.info(
    "external command completed",
    extra={"tool": "approved-exporter", "returncode": 0, "job_id": job_id},
)
```

Do not assume that redaction by matching a few token patterns is complete. Define an allow-list of fields safe to log. If stderr is required for diagnosis, sanitize it under a documented policy, truncate it, and protect log access. Keep logs useful but not secret-bearing.

## 10. Testing subprocess code

The most reliable design puts subprocess invocation behind a small function. Unit tests can monkeypatch `subprocess.run` to verify arguments and error mapping; integration tests can invoke the current Python interpreter with a tiny `-c` program; fake executables can test PATH behavior. Do not rely on `ping`, `git`, or platform-specific shell utilities being installed in CI.

The following tests exercise the wrapper from Section 5. Save the wrapper code in the same module as the tests or import it from your application module.

```python
# test_subprocess_wrapper.py
import os
import subprocess
import sys

import pytest

# Import CommandExecutionError and run_tool from the module under test.


def test_success_and_captured_output():
    result = run_tool(
        [sys.executable, "-c", "import sys; print('ok'); print('note', file=sys.stderr)"],
        allowed_executables={sys.executable}, timeout=5,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"
    assert result.stderr.strip() == "note"


def test_nonzero_exit_is_summarized_without_stderr_leak():
    with pytest.raises(CommandExecutionError) as caught:
        run_tool(
            [sys.executable, "-c", "import sys; print('SECRET_SENTINEL', file=sys.stderr); sys.exit(9)"],
            allowed_executables={sys.executable}, timeout=5,
        )
    assert caught.value.returncode == 9
    assert "SECRET_SENTINEL" not in str(caught.value)


def test_timeout_is_mapped():
    with pytest.raises(CommandExecutionError, match="timed out"):
        run_tool(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            allowed_executables={sys.executable}, timeout=0.1,
        )


def test_missing_executable_is_mapped():
    missing = "/definitely/not/a/real/executable/subprocess-lesson"
    with pytest.raises(CommandExecutionError, match="could not be launched"):
        run_tool([missing], allowed_executables={missing}, timeout=1)


def test_unapproved_executable_rejected_before_launch():
    with pytest.raises(ValueError, match="not allow-listed"):
        run_tool([sys.executable, "-c", "print('should not run')"],
                 allowed_executables={"/approved/only"}, timeout=5)


def test_environment_override_is_passed():
    result = run_tool(
        [sys.executable, "-c", "import os; print(os.environ['LESSON_FLAG'])"],
        allowed_executables={sys.executable},
        env_overrides={"LESSON_FLAG": "enabled"}, timeout=5,
    )
    assert result.stdout.strip() == "enabled"


def test_command_string_is_rejected():
    with pytest.raises(TypeError, match="not a command string"):
        run_tool(sys.executable, allowed_executables={sys.executable}, timeout=5)


def test_non_finite_timeout_is_rejected():
    with pytest.raises(ValueError, match="finite positive"):
        run_tool([sys.executable], allowed_executables={sys.executable}, timeout=float("nan"))


def test_boolean_timeout_is_rejected():
    with pytest.raises(ValueError, match="finite positive"):
        run_tool([sys.executable], allowed_executables={sys.executable}, timeout=True)


def test_invalid_environment_override_is_rejected_before_launch():
    with pytest.raises(TypeError, match="must be strings"):
        run_tool(
            [sys.executable, "-c", "print('should not run')"],
            allowed_executables={sys.executable}, env_overrides={"LESSON_FLAG": 1}, timeout=5,
        )


def test_nul_argument_is_rejected_before_launch():
    with pytest.raises(ValueError, match="NUL"):
        run_tool(
            [sys.executable, "-c", "print('should not run')\x00"],
            allowed_executables={sys.executable}, timeout=5,
        )


def test_timeout_traceback_does_not_display_sensitive_arguments():
    import traceback

    secret_argument = "SECRET_ARG_SENTINEL"
    with pytest.raises(CommandExecutionError) as caught:
        run_tool(
            [sys.executable, "-c", "import time; time.sleep(10)", secret_argument],
            allowed_executables={sys.executable}, timeout=0.1,
        )
    formatted = "".join(traceback.format_exception(caught.value))
    assert secret_argument not in formatted


def test_allow_list_must_be_a_collection_not_a_string():
    with pytest.raises(TypeError, match="collection of complete executable strings"):
        run_tool([sys.executable], allowed_executables=sys.executable, timeout=5)


@pytest.mark.skipif(os.name == "nt", reason="POSIX shebang executable; Windows needs a different fake tool")
def test_fake_executable_from_temporary_path(tmp_path):
    fake = tmp_path / "fake-validator"
    fake.write_text(f"#!{sys.executable}\nprint('fake-ok')\n", encoding="utf-8")
    fake.chmod(0o700)
    inherited_path = os.environ.get("PATH", "")
    child_path = str(tmp_path) + os.pathsep + inherited_path

    result = run_tool(
        ["fake-validator"],
        allowed_executables={"fake-validator"},
        env_overrides={"PATH": child_path},
        timeout=5,
    )
    assert result.stdout.strip() == "fake-ok"
```

The test suite assumes a Python interpreter at `sys.executable` and an OS where a missing absolute path can be attempted. It avoids dependencies on optional commands. `pytest`'s `monkeypatch` is useful when verifying a call without launching a process:

```python
def test_wrapper_uses_argument_list(monkeypatch):
    calls = {}

    def fake_run(args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_tool(
        [sys.executable, "-c", "print('ok')"],
        allowed_executables={sys.executable}, timeout=5,
    )
    assert calls["args"] == [sys.executable, "-c", "print('ok')"]
    assert calls["kwargs"]["shell"] is False
    assert result.stdout == "ok"
```

For an end-to-end fake executable, create an executable script in `tmp_path`, prepend its directory to a copied `PATH`, and invoke its fixed name. That pattern is straightforward on POSIX, but executable permissions and script formats differ on Windows. Prefer `sys.executable`-based integration tests when portability matters.

## 11. Common mistakes and debugging

| Mistake | Why it fails | Better practice |
|---|---|---|
| `shell=True` with interpolated user input | Allows shell syntax to become executable commands | Use an argument sequence and validate semantic arguments. |
| Assuming argument lists validate the tool's options | A value can still be interpreted as a dangerous option | Allow-list tools; validate argument grammar; use `--` if supported. |
| No timeout | A child can hang a worker indefinitely | Set a realistic timeout and define retry/recovery policy. |
| `capture_output=True` for unlimited output | Captured data grows in parent memory | Stream with a bounded logging/storage policy. |
| Reading stdout fully, then stderr fully | The child may block because the other pipe fills | Use `communicate()` or concurrent readers. |
| Assuming `run(timeout=...)` kills every descendant | It manages the direct child, not necessarily its whole process tree | Use owned process-group/session management when needed. |
| Passing `env={"MODE": "prod"}` expecting inheritance | The child receives only that mapping | Start from `os.environ.copy()` when inheritance is intended. |
| Printing `CalledProcessError` or stderr wholesale | Sensitive arguments/output can leak | Log approved fields and redact diagnostics deliberately. |
| Using `shlex.quote()` on Windows | It follows POSIX shell conventions | Avoid shell strings; use platform-aware APIs only when required. |
| Treating all non-zero statuses as equivalent | Tool-specific codes carry different meanings | Document status semantics and preserve the code. |
| Retrying every timeout | The child may have completed side effects before being killed | Make jobs idempotent or reconcile state before retrying. |

## 12. Hands-on exercises

1. **Basic invocation:** run the current interpreter to print a value; capture stdout and assert return code zero.
2. **Failure policy:** run a child that exits with code 12; catch `CalledProcessError` and report only safe metadata.
3. **Input and encoding:** send text to stdin, then run a child that writes invalid UTF-8 bytes. Compare text and binary mode.
4. **Environment:** set `JOB_MODE=staging` in a copied environment and prove the child sees it without modifying the parent environment.
5. **Injection:** explain why the POSIX example is vulnerable, then show that the safe argument-list version prints the entire string literally.
6. **Timeout:** add a timeout to a sleeping child and design a retry policy that accounts for partial side effects.
7. **Streaming:** merge stderr into stdout and stream line by line. Explain why this example does not enforce a deadline while blocked waiting for a newline.
8. **Tests:** add a test that a disallowed executable is rejected before launch and a test that secret-like stderr is absent from the custom exception message.
9. **Process groups:** write a POSIX-only integration test in a disposable environment that launches a parent and child process, then verifies your cleanup policy. Do not run broad process-kill commands on a shared machine.

## 13. Mini-project — reliable external validator

### Scenario

An ingestion job writes a batch manifest and calls an approved external validator. The validator may return malformed output, fail with a non-zero status, or hang. Your Python integration must be predictable and observable.

### Requirements

- Implement `run_tool()` from Section 5 in a module such as `external_tools.py`.
- The caller passes an explicit executable allow-list and a finite timeout.
- Invoke the executable without a shell, with an explicit working directory and copied environment plus only required overrides.
- Capture output only when its expected size is bounded. If the validator can emit large output, design a streaming/log-file alternative.
- Raise a custom exception for timeout, launch failure, or non-zero exit without embedding raw stderr or arbitrary arguments in its message.
- Add tests for success, stderr capture on success, non-zero status, timeout, missing executable, unapproved executable, environment override, and monkeypatched invocation arguments.
- Log an approved tool label, job ID, duration, and return code. Never log credentials or the full environment.
- Document whether a timed-out validation can have side effects and how retries are made safe.

### Acceptance criteria

- All tests pass on the supported CI platform.
- No untrusted input is concatenated into a shell command.
- Every invocation has a timeout or an explicitly justified streaming lifecycle policy.
- Failure logs contain enough context for triage without exposing raw output or secrets.
- The README documents required executable/version, expected exit codes, timeout, environment variables, and platform-specific behavior.

## 14. Self-check questions with explained answers

### 1. Why is `subprocess.run(f"ls {user_dir}", shell=True)` dangerous?

Because the interpolated value becomes part of shell program text. A value containing shell metacharacters can add commands or redirections. Prefer `["ls", user_dir]` where appropriate, validate the argument, and use an allow-listed executable. Even then, validate option semantics and use `--` when the tool supports it.

### 2. What does a POSIX `returncode` of `-9` mean?

It indicates termination by signal 9 (`SIGKILL`) under Python's POSIX convention. This negative-signal representation is not portable to Windows, and the reason for termination may require external logs or orchestration context.

### 3. How should `run_tool(args, timeout)` return a typed result and raise a useful custom error?

Return a `CommandResult` dataclass containing safe metadata and decoded output for successful bounded commands. Raise a `CommandExecutionError` for timeouts, launch failures, and non-zero exits, preserving the original exception with `raise ... from exc` while omitting raw arguments/output from the message. The caller can add policy-specific, sanitized diagnostics.

### 4. Why can reading stdout before stderr deadlock?

If the child fills stderr's pipe buffer, it blocks while writing. The parent is waiting for stdout to close, but the child cannot progress until stderr is drained. `communicate()` drains both streams for finite output; streaming needs concurrent draining or one merged stream.

### 5. Does `timeout=` guarantee that all descendants are stopped?

No. It controls the direct child lifecycle managed by `subprocess`; descendants can outlive it. Use platform-appropriate process groups/sessions or OS-level containment if descendant cleanup is part of the requirement.

### 6. Why is shell quoting not the primary defense?

Quoting rules depend on the shell/platform, and quoting does not validate what the target program does with an argument. An argument can still be interpreted as an option, a path, or a program-specific expression. Avoid the shell, use allow-lists, validate arguments, and apply least privilege.

### 7. Why copy `os.environ` before modifying it?

It preserves intended inherited configuration for the child while avoiding mutation of the parent environment mapping. If a minimal environment is needed, construct an explicit allow-list instead of inheriting everything.

## 15. Final mastery checklist

- [ ] I can explain stdin, stdout, stderr, and return codes.
- [ ] I use argument lists and avoid shell interpolation.
- [ ] I select trusted executables and validate arguments semantically.
- [ ] I set timeouts and handle `CalledProcessError`, `TimeoutExpired`, and launch errors.
- [ ] I choose text/binary mode and encoding deliberately.
- [ ] I know when `communicate()` is appropriate and why pipes can deadlock.
- [ ] I can stream output with an explicit lifecycle and memory policy.
- [ ] I distinguish direct-child termination from process-tree cleanup.
- [ ] I know the POSIX/Windows differences in signals, process groups, `resource`, `shlex`, and batch files.
- [ ] I log safe metadata rather than secrets, raw arguments, or unrestricted output.
- [ ] I test behavior using the current Python executable, monkeypatching, and fake tools.
- [ ] I design retries around idempotency and partial side effects.

## References for version-sensitive behavior

Use documentation for the Python version deployed in production, especially for process creation and Windows behavior:

- [Python 3.12 — `subprocess`](https://docs.python.org/3.12/library/subprocess.html): `run`, `Popen`, timeout handling, pipe behavior, security considerations, and Windows batch-file caveats.
- [Python 3.12 — `shlex`](https://docs.python.org/3.12/library/shlex.html): POSIX shell parsing and quoting; not a universal Windows quoting API.
- [Python 3.12 — `resource`](https://docs.python.org/3.12/library/resource.html): Unix resource limits and platform availability.
- [Python 3.12 — `asyncio` subprocesses](https://docs.python.org/3.12/library/asyncio-subprocess.html): async process creation and stream handling.

## Reference table

| API / concept | Purpose | Important caveat |
|---|---|---|
| `subprocess.run()` | Run and wait for a command | Captured output is buffered in memory. |
| `CompletedProcess` | Result of a completed command | `returncode` meaning is tool-specific. |
| `check=True` | Raise on non-zero status | Catch `CalledProcessError` at the correct boundary. |
| `capture_output=True` | Capture stdout and stderr | Not suitable for unbounded output. |
| `timeout=` | Bound wait time | Does not guarantee descendant cleanup. |
| `Popen` | Fine-grained lifecycle and streaming | Requires careful pipe and cleanup management. |
| `communicate()` | Send input and drain output pipes | Buffers output; use for bounded output. |
| `start_new_session=True` | Start a new POSIX session | Platform-specific; group cleanup must be deliberate. |
| `shlex.split/quote` | POSIX shell tokenization/quoting | Not universal Windows quoting or a complete security defense. |
| `asyncio.create_subprocess_exec()` | Async subprocess API | Cancellation and pipe lifecycle still need design. |
| `resource.setrlimit()` | POSIX resource limits | Not portable and not a complete sandbox. |

---

**Lesson outcome:** invoke external programs as bounded, observable, testable dependencies. Treat the executable, arguments, environment, output, timeout, and cleanup policy as part of the data pipeline's security and reliability contract.
