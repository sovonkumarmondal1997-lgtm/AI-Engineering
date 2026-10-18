# Lesson 04 — Shell and Subprocess Injection

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain the difference between shell interpretation and an executable receiving an argument vector (`argv`).
- Replace shell command construction with fixed executables and validated argument lists, while recognizing option/protocol injection that remains possible with `shell=False`.
- Control executable resolution, environment, working directory, inherited handles, output, time, process groups, privileges, and secrets.
- Identify nested interpreter boundaries in Bash, PowerShell, SSH, Docker, Kubernetes, `find`, `xargs`, `awk`, `sed`, and CI workflows.
- Choose a library instead of a subprocess where practical, and define a sandbox boundary for unavoidable external tools.
- Use Bandit and Ruff security rules, write regression tests, and respond to suspected command execution compromise.

## Prerequisites and scope

This lesson builds on Python functions/exceptions/logging, environment variables and secrets hygiene, `subprocess` and `tempfile`, `eval`/`exec`, input validation, testing/fuzzing, and basic OS process and permission concepts. The roadmap's broader `vulnpy` project is a deliberately vulnerable service that you build or are given; all demonstrations here are limited to a temporary directory and processes you own. Do not test these patterns against real hosts, shared systems, or production workloads.

The roadmap's intended thumbnail exercise is: find a thumbnail generator that passes a user-controlled filename and format to ImageMagick; demonstrate the flaw locally with harmless marker operations and option injection; replace the path with Pillow where possible; if an ImageMagick fallback is required, constrain it to allow-listed options inside a no-network, least-privilege sandbox; add malicious-input regression tests and a Bandit CI check.

## 1. Vocabulary and threat model

- **Process**: a running program with credentials, environment, current working directory, open file descriptors/handles, and resource limits.
- **Executable**: the program image selected by the operating system, such as `/usr/bin/convert` or a pinned Windows executable path.
- **Argument vector (`argv`)**: the executable and distinct argument strings supplied to it. On POSIX, `execve` receives an array of strings; no shell parses those strings unless a shell is itself the executable.
- **Shell**: a command interpreter such as `sh`, Bash, `cmd.exe`, or PowerShell. It parses syntax, expands variables/globs, handles redirections and pipelines, and may launch further programs.
- **Shell injection**: attacker-controlled data changes the shell program's meaning because it is embedded in shell syntax.
- **Argument/option injection**: attacker-controlled data is interpreted as an option, subcommand, path, URL scheme, expression, or other control language by the target program. This can occur with `shell=False`.
- **Nested interpreter**: a shell or other interpreter invoked by a program that itself was launched safely. Examples include `bash -c`, `ssh host command`, `awk 'PROGRAM'`, ImageMagick delegates, and FFmpeg protocol handlers.
- **Trust boundary**: the point where data from a user, upload, job metadata, branch/PR title, model output, environment, or external service enters a command decision.
- **Least privilege**: the process can access only the files, network destinations, credentials, and operating-system capabilities it needs.

A command-injection threat model should name the input source, interpreter/tool that consumes it, privileges available to that process, reachable files and network, expected resource use, and observable evidence. The goal is not merely to remove a metacharacter: keep data separate from instructions and restrict the impact if a tool is compromised.

## 2. How processes receive commands: shell versus argv

### 2.1 No shell: preserve argument boundaries

```python
import subprocess

# One executable, with four distinct arguments.
result = subprocess.run(
    ["/usr/bin/printf", "%s\\n", "hello world"],
    shell=False,
    check=True,
    timeout=5,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
print(result.stdout)
```

On POSIX, Python asks the OS to execute the named program with distinct arguments. The space in `hello world` is part of one argument; it is not split by a shell. Use `sys.executable` for invoking the current Python interpreter when appropriate, not a bare `python` that might resolve to a different installation.

### 2.2 Shell strings are programs, not data

**VULNERABLE / LAB ONLY — do not use in an application.** This intentionally demonstrates the boundary mistake; it does not execute an exploit payload.

```python
import subprocess

filename = "report image.png"  # Imagine this came from an upload.
subprocess.run(f"printf '%s\\n' {filename}", shell=True, check=True)
```

The string is parsed by a shell. Whitespace, quotes, substitutions, redirections, separators, globbing, and newlines can change what runs. Real-world impact depends on shell, quoting, and exact input, but string interpolation is the design flaw.

**Safe alternative — do not invoke a shell.**

```python
import subprocess

filename = "report image.png"
subprocess.run(
    ["/usr/bin/printf", "%s\\n", filename],
    shell=False,
    check=True,
    timeout=5,
)
```

The filename remains one argument. This fixes shell parsing, not the target program's own interpretation of the argument; validate the value for the intended operation as well.

### 2.3 Dangerous APIs and boundaries

| API / pattern | Why it is risky | Preferred approach |
|---|---|---|
| `os.system(command)` | Runs a command through a system shell; returns a status encoding that is easy to misuse. | `subprocess.run([executable, ...], shell=False, check=True, timeout=...)`. |
| `os.popen(command)` | Shell command string and pipe; weak lifecycle/error control. | `subprocess.run` or `Popen` with an argument list. |
| `subprocess.*(..., shell=True)` | Shell interprets the string; platform-specific parsing. | Argument list and `shell=False`. |
| `eval()` / `exec()` | Executes Python expressions/statements; not a command API, but a code-injection boundary. | Parse data (`json`, TOML) or implement a constrained typed operation. |
| `pty.spawn(...)` | Interactive terminal helpers can launch a shell or program with user-influenced arguments; PTY use does not sanitize data. | Avoid PTYs for routine automation; use explicit executable + argv and controlled I/O. |
| `python -c`, `bash -c`, `sh -c`, PowerShell `-Command` | The next argument is program text for another interpreter. | Avoid the interpreter mode; if unavoidable, use a fixed script and pass data separately through a documented input channel. |
| Remote command strings (`ssh`, orchestration APIs) | Local argv may be safe while a remote shell or API parses another command language. | Use structured remote APIs, fixed remote commands, typed parameters, and explicit host/identity allow-lists. |

**VULNERABLE / LAB ONLY — dynamic code execution, not a subprocess fix.**

```python
# Never evaluate a value received from a user, upload, model, or job record.
user_expression = "1 + 1"
result = eval(user_expression)
```

**Safe alternative:** define the small set of supported operations explicitly; parse data with a data parser and validate its schema. Do not try to turn arbitrary Python into a safe calculator by blacklisting words.

```python
import operator

_ALLOWED = {"add": operator.add, "subtract": operator.sub}

def calculate(operation: str, left: int, right: int) -> int:
    if operation not in _ALLOWED:
        raise ValueError("unsupported operation")
    if type(left) is not int or type(right) is not int:
        raise TypeError("operands must be integers")
    return _ALLOWED[operation](left, right)
```

This example intentionally supports only two integer operations; a production API would also define integer magnitude/range limits and an error contract.

## 3. Safe subprocess patterns

### 3.1 Fixed executable and bounded output wrapper

Prefer a wrapper that accepts a typed operation, not an arbitrary command string or executable name. This POSIX-aware example caps the combined stdout/stderr bytes while reading, kills the child's process group on output overflow or timeout when the child remains in that session, and reaps the direct child. On Windows it kills only the direct child; production Windows services should place the process in a Job Object or use a supervisor that guarantees descendant cleanup.

```python
from __future__ import annotations

import os
import signal
import subprocess
import threading
from pathlib import Path
from typing import Sequence


def run_fixed_tool(
    executable: Path,
    args: Sequence[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: float = 10,
    output_limit: int = 1_000_000,
) -> tuple[bytes, bytes]:
    """Run a trusted executable with a combined streaming output cap.

    Callers must validate args against the tool's grammar. This is not a
    general-purpose arbitrary-command runner or a complete OS sandbox.
    """
    if not executable.is_absolute():
        raise ValueError("executable must be an absolute path")
    if timeout_seconds <= 0 or output_limit <= 0:
        raise ValueError("invalid resource limit")
    if not cwd.is_absolute() or not cwd.is_dir():
        raise ValueError("cwd must be an existing absolute directory")
    if any(not isinstance(arg, str) or "\x00" in arg for arg in args):
        raise ValueError("arguments must be NUL-free strings")

    argv = [str(executable), *args]
    proc = subprocess.Popen(
        argv,
        shell=False,
        cwd=cwd,
        env=dict(env),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        start_new_session=(os.name == "posix"),
    )
    assert proc.stdout is not None and proc.stderr is not None
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    total = 0
    lock = threading.Lock()
    output_exceeded = threading.Event()

    def stop_process() -> None:
        try:
            if os.name == "posix":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()  # Descendants require a Windows Job Object/supervisor.
        except ProcessLookupError:
            pass

    def drain(pipe, key: str) -> None:
        nonlocal total
        try:
            while True:
                chunk = pipe.read1(8192)
                if not chunk:
                    return
                with lock:
                    remaining = output_limit - total
                    accepted = chunk[:max(0, remaining)]
                    buffers[key].extend(accepted)
                    total += len(accepted)
                    overflow = len(chunk) > len(accepted)
                if overflow:
                    output_exceeded.set()
                    stop_process()
                    return
        except OSError:
            # The main thread may close a pipe during bounded cleanup.
            return
        finally:
            pipe.close()

    readers = [
        threading.Thread(target=drain, args=(proc.stdout, "stdout"), daemon=True),
        threading.Thread(target=drain, args=(proc.stderr, "stderr"), daemon=True),
    ]
    for reader in readers:
        reader.start()

    timed_out = False
    try:
        proc.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        stop_process()
        proc.wait()
    finally:
        for reader in readers:
            reader.join(timeout=1.0)
        stuck_readers = [reader for reader in readers if reader.is_alive()]
        if stuck_readers:
            # A detached descendant may have inherited a pipe. Do not hang the
            # caller indefinitely; a real hostile-workload service needs an
            # external supervisor that can enforce process-tree containment.
            stop_process()
            proc.stdout.close()
            proc.stderr.close()
            raise RuntimeError("subprocess output pipe remained open after cleanup")

    stdout, stderr = bytes(buffers["stdout"]), bytes(buffers["stderr"])
    if output_exceeded.is_set():
        raise ValueError("tool output exceeded configured byte limit")
    if timed_out:
        raise subprocess.TimeoutExpired(argv, timeout_seconds, output=stdout, stderr=stderr)
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, argv, output=stdout, stderr=stderr)
    return stdout, stderr
```

The byte cap is enforced as the pipes are drained, rather than checking a fully buffered `CompletedProcess` after it returns. Reader joins are bounded so an inherited pipe cannot hang the caller forever; a detached descendant may still survive and require external cleanup. The cap bounds bytes retained by this wrapper, not every byte a descendant might emit before termination. A child that deliberately escapes its process group, platform process-creation overhead, CPU/memory/disk use, and parser vulnerabilities require external worker/container/supervisor controls. Treat this as an instructional wrapper for trusted tools, not a replacement for OS-level containment of hostile workloads. Pass only the environment entries the tool needs; never blindly copy `os.environ` or include secrets by default.

### 3.2 `check`, timeouts, and errors

- `check=True` raises `subprocess.CalledProcessError` on a non-zero exit. It does not make the command safe; it makes failure harder to overlook.
- `timeout=` bounds the wait from Python's perspective. Python kills the direct child when the timeout expires; grandchildren may survive if the tool created them.
- Catch `TimeoutExpired` and `CalledProcessError` at the application boundary. Return a stable user-facing error; log a request/job ID and exit status without leaking secrets or full internal paths.
- Do not blindly retry non-idempotent commands after timeouts. The child may have performed part of the operation before it was killed.
- `start_new_session=True` on POSIX can create a process group/session for cleanup. On timeout, a POSIX supervisor can send signals to the process group with `os.killpg`; implement escalation (TERM then KILL), handle `ProcessLookupError`, and always reap the child. Windows uses different process-tree controls (for example Job Objects); `CREATE_NEW_PROCESS_GROUP` alone is not a universal descendant-kill guarantee.
- Avoid `preexec_fn` in threaded applications: it can deadlock between `fork` and `exec`. Prefer `start_new_session`, supported `Popen` parameters, an external supervisor, `prlimit`, cgroups, containers, or a dedicated worker process for limits. `resource.setrlimit` is Unix-oriented and is not a portable sandbox.

### 3.3 Executable, environment, and working-directory controls

- Resolve the executable during trusted startup, deploy it at a controlled absolute path, and ensure untrusted users cannot replace it or any writable parent directory. `shutil.which()` can be useful during trusted initialization, but its result must be checked and pinned; calling it on each untrusted request with a mutable `PATH` is not hardening.
- Pass a deliberately constructed environment rather than copying `os.environ` wholesale. Include only required variables, such as a controlled `PATH`, locale, and tool-specific settings. Some programs require `HOME`, certificate settings, or platform variables; decide explicitly rather than blindly deleting or inheriting.
- Do not pass cloud tokens, database passwords, or all service environment variables to a child that does not need them. Command-line arguments and environment variables can be exposed through process inspection, crash dumps, diagnostics, or logs; prefer file descriptors, protected files, or a secret manager integration when supported.
- Use a private, pre-created `cwd` that is not writable by untrusted users. The working directory affects relative paths, config discovery, plugin loading, and output placement.
- `close_fds=True` prevents most unintended descriptor inheritance (it is the default in modern Python); intentionally passed descriptors must be enumerated and documented. Windows handle inheritance has separate semantics.
- Set `stdin=subprocess.DEVNULL` for non-interactive tools unless input is explicitly required. Never allow an unexpected prompt to hang a worker indefinitely.

### 3.4 Logging and output handling

- Treat stdout, stderr, exit status, filenames, and tool-generated diagnostics as untrusted. Do not interpolate raw output into HTML, SQL, shell commands, or structured logs without the appropriate encoding.
- Prefer structured events: operation name, job ID, pinned executable identity, validated option names, duration, exit code, timeout/limit outcome. Redact tokens and sensitive paths. Do not log the complete environment or raw command line if arguments may contain secrets.
- Decode output with an explicit encoding and a deliberate error policy (`errors="replace"` is useful for diagnostics). Binary output should remain bytes.
- A capped streaming design should count bytes as they arrive, stop reading/terminate when the cap is crossed, and drain/close pipes to avoid deadlocks. Redirecting to a quota-limited file is another option. Ensure stderr is drained too; a full pipe can block a child.

## 4. Argument injection and option terminators

### 4.1 `shell=False` is necessary, not sufficient

Suppose a user supplies a filename beginning with `-`. The shell is out of the picture, but the target executable may treat that value as an option. The program may support a dangerous option, read a response file, open a protocol URL, or interpret a pattern as an expression.

**VULNERABLE / LAB ONLY — do not pass untrusted patterns to this command.**

```python
import subprocess

user_pattern = "--help"  # Represents a user-controlled grep pattern.
subprocess.run(["/usr/bin/grep", user_pattern, "/srv/job-inputs/example.txt"],
               check=False, timeout=5)
```

Here the first operand position is still parsed by `grep` as an option; a leading dash can change the operation or cause failure. Exact behavior depends on the tool and option. This example is about argument parsing, not shell metacharacters.

**Safer pattern:** use the documented `--` operand terminator when supported, validate the pattern according to the application's purpose, and use a fixed file selected from trusted state.

```python
import subprocess

user_pattern = validated_search_text
subprocess.run(
    ["/usr/bin/grep", "--", user_pattern, "/srv/job-inputs/example.txt"],
    shell=False,
    check=True,
    timeout=5,
    cwd="/srv/job-work",
)
```

This example assumes a POSIX `grep` implementation that supports `--`. The terminator protects the pattern from option parsing; it does not make arbitrary regular expressions harmless or prevent ReDoS in tools with vulnerable regex behavior. For archive extraction, prefer Python's `tarfile`/`zipfile` with explicit member validation and resource limits (see the previous lesson), or use a tested wrapper for the exact installed implementation. Never assume every utility supports `--` or has the same option grammar.

A clearer portable strategy for a command that supports `--` is:

```python
# Example for a utility whose documented syntax is: tool [OPTIONS] -- OPERAND
subprocess.run([TRUSTED_TOOL, "--mode", "read", "--", validated_operand],
               shell=False, check=True, timeout=10)
```

`--` is a convention, not a universal feature. Some programs do not support it, and it does not stop the program from interpreting the operand as a URL, expression, config file, or special file. Keep validation and tool-specific policy.

### 4.2 Validate by meaning, not by deleting punctuation

Use typed values and allow-lists:

- A format should be an enum such as `{"png", "jpeg"}`, not an arbitrary suffix or option fragment.
- A quality value should parse as an integer and fall in a narrow range, not be concatenated into a flag.
- A file should be selected by a server-generated ID and opened from a controlled directory, not supplied as an arbitrary path.
- A URL should have a permitted scheme/host policy; a path such as `http://...` may be a protocol handler, not a filename.
- An executable name, subcommand, option name, `awk` program, `sed` expression, or shell fragment should never come directly from user data.

Do not remove `;`, quotes, spaces, `$`, or hyphens and assume the result is safe. Reject unknown values and fail closed.

### 4.3 Quoting is not a universal fix

`shlex.quote()` produces shell quoting for POSIX-like shells; it is not a Windows `cmd.exe` or PowerShell quoting function, and it does not neutralize the target program's option or protocol grammar. It is not a substitute for avoiding the shell. If a shell is genuinely required, use fixed shell code and pass values through a carefully defined channel; document the exact shell and test it on that platform. Never assemble a command from independently “quoted” pieces without understanding the grammar and expansion stages.

## 5. Nested interpreters and tool-specific boundaries

| Tool / boundary | Risk | Safer design |
|---|---|---|
| `bash -c`, `sh -c`, PowerShell `-Command` | Argument is interpreted as a program. | Avoid `-c`/`-Command`; use a fixed script or native API. If unavoidable, keep program text constant and send data via stdin or a constrained file format. |
| `ssh host command` | Remote command may be assembled and parsed by a remote shell; local argv separation does not imply remote argv separation. | Use a fixed remote command, strict host/user/key allow-lists, avoid concatenating user data, and prefer a structured remote service/API. Understand the SSH client's remote-command semantics. |
| `docker exec` | Docker CLI argument parsing, container command semantics, and possible access to the Docker daemon/socket. | Fixed container ID/name from trusted state, fixed executable and argv, no Docker socket in untrusted workers, least-privilege daemon access. |
| `kubectl exec` | User-controlled pod/container/command selection or shell command; Kubernetes credentials may permit broad cluster actions. | Restrict RBAC, namespace, pod identity, and allowed executable; do not let requests provide arbitrary commands; prefer Kubernetes API operations or a narrow job service. |
| `find -exec`, `xargs` | Filename/argument boundary and command-template interpretation; whitespace/newline filenames can confuse naive pipelines. | Prefer Python filesystem APIs; if using `find`, use `-exec ... {} +` or NUL-delimited forms supported by the tools, and keep command template fixed. |
| `awk`, `sed`, `perl`, SQL clients | Program/expression is a second language. | Fixed program text, data passed separately, validated simple values, or use a library. |
| `curl`, `wget`, FFmpeg, ImageMagick | URL schemes, output paths, delegates, protocols, config files, and options can cause file access or network access. | Allow-list schemes and options, disable unneeded protocols/delegates, fixed output directory, network isolation, use HTTP/image libraries when possible. |
| `git`, `tar`, `rsync`, `openssl` | Options can change destination, execute helpers, load config, or access unexpected paths. | Tool-specific option validation, documented `--` use, fixed config/environment, least privilege, and a library or API if it fits. |

The security review must follow data through every interpreter. A safe Python argv can still contain an unsafe Bash program; a safe shell invocation can still pass a dangerous FFmpeg protocol; a fixed `kubectl` command can still be overprivileged.

## 6. Windows, POSIX, and portability

- POSIX `execve` receives an argument array. Windows `CreateProcess` receives a command-line string; Python serializes argv (commonly using `subprocess.list2cmdline`-style rules), and the child runtime parses it. Different Windows programs may use different parsing rules.
- Avoid `.bat` and `.cmd` targets with untrusted arguments. Batch files are interpreted by `cmd.exe` and can have special behavior even when Python is called with `shell=False`; this family of problems is often discussed under BatBadBut. Prefer a native `.exe` or a library, and test the exact Python/Windows combination.
- `cmd.exe` and PowerShell have different quoting, variable expansion, and metacharacter rules. `shlex.quote` is not suitable for them. Do not pass untrusted strings to PowerShell `-Command` or `cmd /c`.
- Windows paths include drive-relative paths (`C:foo`), drive-absolute paths (`C:\\foo`), UNC paths (`\\\\server\\share`), reserved device names, alternate separators, and case-insensitive behavior in common filesystems. Validate paths according to the intended API, not a POSIX-only assumption.
- POSIX `start_new_session`, `os.killpg`, `pass_fds`, file descriptors, `resource`, and `prlimit` are not all available or equivalent on Windows. Windows uses handles and process creation flags; robust descendant cleanup may require Job Objects or an external supervisor.
- Do not use `shell=True` as a compatibility shortcut. Write platform-specific adapters with tests, or use a cross-platform library.

## 7. Resource controls, sandboxing, and privilege

### 7.1 Process lifecycle controls

For a worker that processes untrusted documents or images, define explicit limits for wall-clock time, CPU, memory, number of child processes, output bytes, input bytes, open files, temporary disk usage, and network egress. A Python timeout alone does not impose all of these limits.

On POSIX, a supervisor can use a new session/process group and terminate descendants on timeout. For strong guarantees, place the worker under cgroups/systemd, `prlimit`, a container runtime, or a dedicated job supervisor. On Windows, use a Job Object or a service manager with process-tree controls. Validate that the supervisor kills descendants, reaps processes, closes pipes, and cleans temporary files in tests.

### 7.2 Sandbox layers

For an unavoidable converter fallback, use multiple independent controls:

1. Dedicated unprivileged worker identity; no `sudo` and no host credentials.
2. Read-only application filesystem; a fresh, quota-limited scratch directory for input/output.
3. No network (`--network none` or an equivalent policy), unless a specific destination is required.
4. Drop Linux capabilities, enable `no-new-privileges`, use a restrictive seccomp profile and SELinux/AppArmor policy where available.
5. Do not mount the Docker socket, host root, home directory, cloud credentials, or writable shared volumes into the worker.
6. CPU, memory, process-count, file-size, open-file, and wall-clock limits; output validation after the tool exits.
7. Pin and patch the image and tool; restrict ImageMagick delegates and FFmpeg protocols to the required subset.
8. Per-tenant/per-job isolation and cleanup; no shared writable directories between untrusted jobs.

Containers reduce blast radius but are not automatically a security boundary against every kernel/runtime vulnerability. For higher-risk code or hostile documents, consider stronger isolation such as gVisor, Firecracker/microVMs, or a dedicated sandbox service. Select controls based on threat model and operational cost.

### 7.3 `sudo`, file descriptors, and secrets

Do not run a web/data worker as root. If privileged work is unavoidable, expose a narrow privileged helper with a fixed operation set and validated typed inputs; a broad `sudo` rule or wildcard command is not least privilege. Do not let the child inherit database sockets, agent sockets, cloud credentials, or file descriptors it does not need. `close_fds=True` is useful but does not remove secrets in environment, arguments, mounted files, or accessible sockets.

## 8. Prefer a library; analyze residual risk

A library removes a process boundary and often avoids a command-language boundary, but it is not automatically safe: parser bugs, decompression bombs, image decoder vulnerabilities, resource exhaustion, and malicious file formats remain.

| Task | Prefer | Residual risks / controls |
|---|---|---|
| Thumbnail/image conversion | Pillow for supported formats and operations | Decoder CVEs, decompression/resource exhaustion, image bombs; cap dimensions/pixels/bytes, update Pillow, isolate hostile inputs. |
| ZIP/TAR handling | `zipfile` / `tarfile` with explicit member and size policy | Traversal, links, device files, archive bombs, parser bugs; use Lesson 03's policy and fresh directories. |
| HTTP fetch | `httpx` or `urllib` with explicit policy | SSRF, redirects, DNS rebinding, oversized bodies; use scheme/host/IP policy, redirect revalidation, timeout and streaming caps. |
| Git operations | `dulwich` or a narrow Git library/API where suitable | Protocol/config/auth behavior still matters; pin remotes and disable unneeded protocols. |
| Database backup | Database driver/backup API | Privileges, consistency, credential handling, large output; scope credentials and stream to protected storage. |
| File search/transforms | `pathlib`, `os.scandir`, Python parsing | Symlinks, races, untrusted parser inputs, resource use; use directory-relative APIs and isolation as needed. |

Document the reason for every remaining subprocess: required capability, accepted input grammar, executable provenance, exact argv template, environment, cwd, resource controls, sandbox, monitoring, and fallback behavior.

## 9. The thumbnail-generator lab (`vulnpy`)

### 9.1 Lab safety and setup

Use a disposable virtual environment and temporary directory. Run only against files you created. Do not use real uploads, shared machines, production buckets, or network-accessible systems. The vulnerable sample below uses a harmless marker file inside a temporary directory; it does not delete files or contact a host. The optional POSIX-only demonstration below is deliberately isolated: it creates a marker under a temporary directory and removes the entire directory afterward. Do not adapt the pattern to arbitrary paths.

**VULNERABLE / LAB ONLY — isolated shell-injection demonstration (POSIX only).**

```python
import os
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="subprocess-lab-") as temporary:
    root = Path(temporary)
    marker = root / "marker.txt"
    # The untrusted value is inserted as shell syntax. The only side effect
    # is a marker inside this disposable directory.
    user_value = f"safe; touch {marker} #"
    os.system(f"printf '%s\n' {user_value}")
    assert marker.is_file(), "the lab should demonstrate shell interpretation"
# TemporaryDirectory removes the marker and all other lab files.
```

**Safe alternative:** pass the entire value as one argument to a fixed executable, or avoid the subprocess entirely. For example, `subprocess.run(["/usr/bin/printf", "%s\n", user_value], shell=False, check=True)` prints the literal punctuation and does not create the marker. This demonstration requires a POSIX shell and `touch`; it is not a Windows exercise.

Suggested setup:

```bash
python -m venv .venv
# POSIX activation:
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pillow pytest bandit ruff
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`. If activation is restricted by policy, invoke `.venv\\Scripts\\python.exe` directly. Python 3.11+ is recommended for the lab; the core code below uses standard library features available in Python 3.10+ plus Pillow for the library alternative. The exact external converter and sandbox configuration is platform/deployment specific.

### 9.2 Vulnerable design

**VULNERABLE / LAB ONLY — intentionally unsafe; do not run this implementation.**

```python
import os


def make_thumbnail(input_name: str, output_name: str, image_format: str) -> None:
    # Both user-controlled strings are embedded in a shell program.
    os.system(f"convert {input_name} -resize 128x128 -format {image_format} {output_name}")
```

Problems:

1. Shell metacharacters in either filename can change shell behavior.
2. A leading dash or special option in a filename/format can change ImageMagick behavior even after removing the shell. In ImageMagick command grammars, options such as `-write` can have file-writing effects; whether a value is parsed as an option depends on its exact argv position and version. Never let an untrusted format string or filename become an option. The regression test below rejects `-write` as a format without invoking ImageMagick; it does not execute an option-injection payload.
3. Paths can escape the intended input/output directory or target symlinks.
4. ImageMagick delegates/protocols may reach files or network, depending on build/configuration.
5. No timeout, output quota, controlled environment, or privilege boundary exists.

**Safe preferred alternative — use Pillow, controlled IDs, and a fixed format mapping.**

```python
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageOps

_FORMATS = {"png": ("PNG", ".png"), "jpeg": ("JPEG", ".jpg")}


def make_thumbnail_pillow(
    source: Path,
    destination: Path,
    image_format: str,
    *,
    max_pixels: int = 20_000_000,
) -> None:
    """Convert one trusted-resolved source to a controlled destination.

    The caller must enforce storage containment/ID lookup and ensure the
    source is a regular file in the worker's input area. Hostile image parsing
    should still happen in a resource-limited worker.
    """
    if image_format not in _FORMATS:
        raise ValueError("unsupported image format")
    output_format, expected_suffix = _FORMATS[image_format]
    if destination.suffix.lower() != expected_suffix:
        raise ValueError("destination suffix does not match selected format")

    with Image.open(source) as opened:
        width, height = opened.size
        if width <= 0 or height <= 0 or width * height > max_pixels:
            raise ValueError("image dimensions exceed policy")
        opened.verify()

    # Reopen after verify(); Pillow documents that verify() invalidates normal
    # subsequent use of that Image object.
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB" if output_format == "JPEG" else "RGBA")
        image.thumbnail((128, 128))
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Write to a private temporary sibling, then replace the final path.
        # The destination directory must not be writable by an attacker.
        import os
        import tempfile

        fd, temp_name = tempfile.mkstemp(prefix=".thumb-", suffix=expected_suffix, dir=destination.parent)
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as stream:
                image.save(stream, format=output_format)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, destination)
        except BaseException:
            try:
                temp_path.unlink(missing_ok=True)
            finally:
                raise
```

This example improves command-injection resistance by not invoking a process and uses a server-selected format. It is not a complete storage service: source/destination containment, per-user authorization, quotas, symlink-safe directory handling, and atomic durability of the containing directory need to be addressed by the application. `os.replace` can replace a destination path; keep the directory private and use exclusive/capability-style APIs when concurrent untrusted actors can mutate it. Image dimensions are checked before decoding, but hostile formats can still stress parsers; isolate parsing and apply memory/CPU limits.

### 9.3 Regression tests for the safe library path

Save `make_thumbnail_pillow()` in `thumbnail.py`, the bounded runner from Section 3.1 in `safe_subprocess.py`, and this test module as `test_thumbnail.py`.

```python
from pathlib import Path
import os
import subprocess
import sys

import pytest
from PIL import Image

from thumbnail import make_thumbnail_pillow
from safe_subprocess import run_fixed_tool


def test_creates_thumbnail_with_allowlisted_format(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    destination = tmp_path / "out.png"
    Image.new("RGB", (320, 200), (20, 40, 60)).save(source)

    make_thumbnail_pillow(source, destination, "png")

    assert destination.is_file()
    with Image.open(destination) as result:
        assert result.format == "PNG"
        assert result.size == (128, 80)


def test_rejects_unknown_format_before_processing(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (8, 8)).save(source)
    with pytest.raises(ValueError, match="unsupported image format"):
        make_thumbnail_pillow(source, tmp_path / "out.png", "png;touch-marker")


def test_rejects_suffix_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (8, 8)).save(source)
    with pytest.raises(ValueError, match="suffix"):
        make_thumbnail_pillow(source, tmp_path / "out.jpg", "png")


def test_rejects_imagemagick_option_as_format(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (8, 8)).save(source)
    with pytest.raises(ValueError, match="unsupported image format"):
        make_thumbnail_pillow(source, tmp_path / "out.png", "-write")


def test_rejects_oversized_dimensions(tmp_path: Path) -> None:
    source = tmp_path / "large.png"
    Image.new("RGB", (101, 101)).save(source)
    with pytest.raises(ValueError, match="dimensions"):
        make_thumbnail_pillow(source, tmp_path / "out.png", "png", max_pixels=10_000)




def test_bounded_runner_caps_streamed_output(tmp_path: Path) -> None:
    # The child program is a fixed test literal, not user-supplied code.
    with pytest.raises(ValueError, match="output exceeded"):
        run_fixed_tool(
            Path(sys.executable),
            ["-c", "import sys; sys.stdout.write('x' * 200000)"],
            cwd=tmp_path,
            env={"PATH": os.environ.get("PATH", "")},
            timeout_seconds=5,
            output_limit=1024,
        )


def test_bounded_runner_times_out(tmp_path: Path) -> None:
    with pytest.raises(subprocess.TimeoutExpired):
        run_fixed_tool(
            Path(sys.executable),
            ["-c", "import time; time.sleep(2)"],
            cwd=tmp_path,
            env={"PATH": os.environ.get("PATH", "")},
            timeout_seconds=0.1,
            output_limit=1024,
        )


def test_filename_is_not_used_as_command_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Keep any hypothetical marker inside this isolated test directory.
    monkeypatch.chdir(tmp_path)
    # A filename with shell punctuation is just a filename to Pillow.
    source = tmp_path / "x; touch SHOULD_NOT_EXIST.png"
    destination = tmp_path / "out.png"
    Image.new("RGB", (8, 8)).save(source)
    make_thumbnail_pillow(source, destination, "png")
    assert destination.is_file()
    assert not (tmp_path / "SHOULD_NOT_EXIST.png").exists()
```

Run `pytest -q`. These tests cover allow-list rejection, size-policy enforcement, normal conversion, literal filename punctuation, bounded output, and timeout behavior. They do not prove that Pillow has no parser vulnerabilities, that Windows descendants are killed by this wrapper, or that the broader storage service is race-free.

### 9.4 If ImageMagick must remain

Treat this as a separate, explicitly accepted residual risk. Do not pass user-provided format strings or arbitrary paths. Map a small typed operation to fixed options; map a server-generated file ID to a source path inside a private input directory; create output names on the server; set a controlled environment and cwd; use an absolute pinned executable path; disable unused delegates/protocols in ImageMagick policy; and run the converter in a no-network, read-only, non-root sandbox with resource limits.

A wrapper skeleton (not a complete sandbox) might look like:

```python
from pathlib import Path

from safe_subprocess import run_fixed_tool


def convert_with_imagemagick(
    executable: Path,
    source: Path,
    destination: Path,
    *,
    workdir: Path,
    controlled_env: dict[str, str],
) -> None:
    if not executable.is_absolute():
        raise ValueError("executable path must be absolute")
    if source.parent != workdir / "input" or destination.parent != workdir / "output":
        raise ValueError("paths must be in the job's designated directories")
    if source.is_symlink() or not source.is_file():
        raise ValueError("source must be a regular non-symlink file")
    if destination.suffix.lower() not in {".png", ".jpg"}:
        raise ValueError("unsupported output suffix")

    # Inputs and directories must already be created and owned by the worker.
    # The fixed `png:`/`jpeg:` prefix chooses a format; it is not user input.
    output_arg = f"{ 'png' if destination.suffix.lower() == '.png' else 'jpeg' }:{destination}"
    # The shared runner enforces a combined output-byte cap and timeout.
    # Its process-group handling is POSIX-aware; Windows needs a Job Object or
    # an external supervisor for descendant cleanup.
    run_fixed_tool(
        executable,
        [str(source), "-thumbnail", "128x128", output_arg],
        cwd=workdir,
        env=controlled_env,
        timeout_seconds=10,
        output_limit=1_000_000,
    )
```

This is a **wrapper skeleton, not a production-safe implementation**. String equality of parents does not establish race-free containment; path names can be swapped in a writable directory; the shared runner does not provide a Windows Job Object, complete descendant containment, or CPU/memory/disk limits; the ImageMagick grammar/configuration differs by version; and `shell=False` does not disable dangerous delegates/protocols. The deployment must enforce the sandbox and policy, use private directories or directory-fd-relative operations, and test the exact pinned ImageMagick build. If those controls cannot be demonstrated, use Pillow or reject the fallback.

## 10. CI, containers, Kubernetes, and workflow injection

### 10.1 GitHub Actions and other CI systems

**VULNERABLE / LAB ONLY — illustrative workflow anti-pattern.**

```yaml
# Do not interpolate untrusted event text directly into a shell script.
- name: Label PR
  run: echo "PR title: ${{ github.event.pull_request.title }}"
```

A PR title or branch name is data controlled by an external contributor; direct expression substitution can turn it into shell syntax before the shell starts.

**Safer pattern:** pass the value through an environment variable and quote it as data in the shell used by the runner. Also avoid printing secrets and validate any value that controls a later operation.

```yaml
- name: Print PR title as data
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  shell: bash
  run: printf '%s\n' "$PR_TITLE"
```

Environment passing avoids textual insertion into the script, but the shell still expands the variable. Quoting is essential, and downstream tools may have their own option grammar. Do not use the value as an executable, option, `eval` input, or command template. Restrict token permissions, use read-only permissions for untrusted PRs, avoid secrets on forked PRs, pin third-party actions by immutable commit SHA, and separate privileged release workflows from untrusted build/test workflows.

### 10.2 Docker and Kubernetes

- Avoid Docker shell-form `ENTRYPOINT`/`CMD` when arguments are data; prefer exec form such as `ENTRYPOINT ["/app/server"]` and pass structured arguments.
- Never expose `/var/run/docker.sock` to an untrusted worker: access to a privileged daemon can amount to host-level control.
- Kubernetes `exec` permissions are powerful. Apply least-privilege RBAC; do not let an HTTP parameter choose namespace, pod, container, and command. Prefer a narrow job API that maps approved operations to a fixed workload.
- Use read-only root filesystems, non-root users, dropped capabilities, seccomp/AppArmor/SELinux, resource requests/limits and quotas, network policies, scoped service accounts, and short-lived credentials. These are layered controls, not a guarantee against all escapes.
- Treat container build arguments, labels, image tags, mounted configs, and environment variables as separate parsing boundaries. Do not put secrets in Docker build args or image layers.

## 11. Static analysis and exception policy

### 11.1 Bandit and Ruff

The roadmap names Bandit checks B602/B603/B604/B605/B606/B607 and Ruff's `S602`–`S607` security rules. Rule meanings and coverage can change by tool version; pin tool versions and review their current documentation. Broadly, these checks flag shell-enabled subprocess calls, subprocess APIs, shell command functions, and executable lookup patterns. A finding is a review signal, not proof of exploitability; an absence of findings is not proof of safety.

Example `pyproject.toml` configuration:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "S"]
# Do not globally ignore subprocess security rules.

[tool.bandit]
targets = ["src", "tests"]
# Pin Bandit in the lockfile/CI environment. Review any exclusions explicitly.
```

Install/run in CI, for example:

```bash
python -m pip install bandit ruff
ruff check .
bandit -r src tests -f json -o bandit-report.json
```

For a CI gate, configure the job to fail when the tools return non-zero and preserve reports as artifacts. If a specific supported Bandit version exposes a rule selection option, pin that version and use the documented option; do not rely on guessed CLI flags. Run `ruff check` with `S` rules enabled and inspect the output for the exact Ruff version.

### 11.2 Narrow, documented exceptions

If a subprocess is necessary, the exception record should include:

1. Owner and reviewer; reason a library/API cannot meet the requirement.
2. Exact executable path and pinned version/build; fixed argv template and allowed parameter types/ranges.
3. Input trust boundary, option/protocol grammar, and how `--` is used (or why unsupported).
4. Environment, cwd, descriptor/handle policy, privilege identity, secret access, and logging/redaction.
5. Timeout, descendant cleanup, output/disk/memory/CPU/process limits, network policy, sandbox profile.
6. Tests for malicious filenames, leading dashes, metacharacters, malformed Unicode/newlines, timeouts, oversized output, non-zero exits, and cleanup.
7. Expiry/review date and the specific static-analysis suppression with a comment. Never suppress an entire rule or directory to make CI green.

Use the smallest line-scoped suppression supported by the tool. Link it to a security review/test; require re-approval when the command, executable, or trust boundary changes.

## 12. Security testing matrix

Test the command boundary, not only a successful invocation.

| Input/condition | Expected control | Evidence to assert |
|---|---|---|
| Spaces and Unicode in a normal filename | argv preserves one operand; app resolves server ID | Correct output, no unexpected extra args. |
| `;`, `&`, `|`, `$()`, backticks, newline, quotes | No shell parsing; input rejected if outside domain | No marker created; expected validation error. |
| Leading `-` / `--config` / `--output` | Filename is not accepted as an option; use documented `--` or server-side ID | Target receives only approved argv. |
| Absolute path, `../`, drive path, UNC path | ID mapping/containment rejects external paths | No read/write outside job root. |
| Unsupported format/protocol (`http:`, `file:`, `concat:`) | Enum/scheme allow-list rejects | No network/file access via handler. |
| Huge file/image/dimensions/output | Byte, pixel, time, memory, and output limits | Bounded resource use and cleanup. |
| Child timeout / spawned descendants | Supervisor terminates process tree | No child remains; pipes and temp files closed. |
| Non-zero exit / invalid output | Fail closed; don't publish partial result | Stable error and no final artifact. |
| Poisoned `PATH`, cwd config, inherited descriptor | Fixed executable, minimal env, controlled cwd, closed fds | No unintended executable/config/secret access. |
| Concurrent jobs / symlink swap | Per-job private directories or capability APIs | No cross-job read/write. |
| CI PR title/branch with shell punctuation | Pass as data; no inline expression substitution | Workflow only logs the literal title. |

Use unit tests with a fake executable that records argv and environment into a private test directory; do not depend on destructive commands to prove safety. Integration tests should use temporary directories and marker files with guaranteed cleanup. Fuzz the typed input validators and argv builder; assert that every accepted input maps to a known operation and every rejected input produces no side effect.

## 13. Common mistakes

- Believing `shell=False` makes every command safe. It removes one interpreter but not option, protocol, config, or target-language injection.
- Assuming `shlex.quote` works for Windows or neutralizes a target program's options.
- Passing a user value as `bash -c`, PowerShell `-Command`, SSH remote command, `awk` program, or `sed` expression.
- Using `--` without checking the exact tool's syntax, or assuming it neutralizes every interpretation of the operand.
- Trusting `shutil.which` on each request, inheriting a large environment, or running from a writable working directory.
- Capturing unlimited stdout/stderr and checking the size only after the process exits.
- Believing `timeout=` necessarily kills grandchildren, or using `preexec_fn` in a threaded service to set limits.
- Treating a container as a complete sandbox while mounting host directories, credentials, or the Docker socket.
- Logging full argv/environment and leaking credentials or customer paths.
- Replacing a subprocess with a parser library but forgetting parser vulnerabilities and resource exhaustion.
- Suppressing static-analysis findings globally instead of recording a narrow, expiring exception.

## 14. Self-check with answers

### 1. Give two ways `subprocess.run(["tar", "xf", user_archive])` can be abused despite no shell, and mitigations.

**Answer:** A leading dash may be parsed as an option, and the archive contents can contain traversal/link members that write outside the extraction directory. Validate/select the archive through a server-side ID, use documented option termination where supported, and extract with a strict archive policy (fresh directory, member-path/link/type validation, count/size/ratio limits). Tool-specific configuration or protocol options are another risk.

### 2. How would you design a fixed-template command runner and test it?

**Answer:** Expose a small typed operation enum; map each operation to a constant executable and fixed option template; parse values into constrained types; use a server-generated path/ID; set explicit cwd/environment/timeout and resource limits; capture output with a cap; never accept arbitrary executable names or command strings. Unit-test exact argv, environment, rejection of leading dashes/metacharacters/unknown options, timeout and non-zero-exit behavior, output caps, cleanup, and absence of side effects.

### 3. How do you configure Bandit/Ruff and manage exceptions?

**Answer:** Pin versions, enable Ruff `S` rules, run Bandit on application and test code in CI, fail the job on findings, and preserve machine-readable reports. Review each finding; if a subprocess is justified, use a line-scoped suppression supported by the pinned tool with a comment linking to a reviewed exception record, tests, owner, and expiry. Do not globally disable B602/B603/B604/B605/B606/B607 or S602–S607.

### 4. Why isn't `shlex.quote` enough?

**Answer:** It targets POSIX-shell quoting. It does not quote for `cmd.exe` or PowerShell, and does not neutralize options, URLs/protocol handlers, expressions, or configuration syntax parsed by the target tool. Avoid the shell and validate the target's argument grammar.

### 5. What does a subprocess timeout guarantee?

**Answer:** It bounds the wait for the direct child as managed by Python. It does not by itself impose CPU/memory/disk/output limits or guarantee all descendants are terminated. Use process groups/sessions plus explicit cleanup on POSIX, Job Objects or a supervisor on Windows, and resource-isolated workers for hostile inputs.

## 15. Completion checklist

- [ ] I can explain argv versus shell parsing and identify every nested interpreter boundary.
- [ ] I replaced dynamic shell strings with a fixed executable and argument list wherever possible.
- [ ] I validate option values, filenames, formats, schemes, and command choices by allow-list and type.
- [ ] I checked the exact target tool's option grammar rather than assuming `--` works everywhere.
- [ ] I control executable resolution, cwd, environment, inherited handles, stdin, secrets, and logs.
- [ ] I defined time, process-tree, output, memory, CPU, disk, and network limits for external tools.
- [ ] I prefer Pillow or a suitable library for thumbnails and isolate any unavoidable converter fallback.
- [ ] I added regression tests for malicious filenames, leading dashes, unsupported formats, timeouts, oversized output, and cleanup.
- [ ] Bandit and Ruff security rules run in CI; exceptions are narrow, reviewed, tested, and expire.
- [ ] I documented the threat model, residual risks, monitoring signals, and incident-response actions.

**Incident response note:** If unexpected child processes or suspected command execution are detected, isolate the worker and restrict egress; preserve process, container, CI, and audit logs; identify the triggering input and affected credentials; rotate/revoke exposed secrets; rebuild from trusted artifacts; and review lateral movement before restoring service. Do not delete evidence before it is preserved.
