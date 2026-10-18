# sys, os, and Runtime Introspection

> **Target:** CPython 3.12–3.14. Most examples use public APIs and should run on these versions, but output depends on OS, build, environment, permissions, and container configuration. The lesson marks private or version-specific interfaces explicitly. No single field in a diagnostic report is a universal measure of runtime health or available resources.

## Learning outcomes

By the end of this lesson, you should be able to:

- Identify the active Python executable, version, implementation, import path, flags, streams, platform, and build configuration.
- Distinguish Python-level runtime facts from operating-system facts and CPython implementation details.
- Produce a useful, machine-readable `doctor` report without leaking environment secrets.
- Inspect environment variables, process IDs, filesystems, CPU capacity, resource limits, encodings, time zones, and installed packages.
- Explain interpreter command-line flags and important `PYTHON*` environment variables.
- Investigate runtime state using `inspect`, `gc`, `faulthandler`, `tracemalloc`, and thread diagnostics where appropriate.
- Interpret container CPU and memory limits without confusing host capacity with capacity available to the process.
- Use diagnostic tools safely in production and answer the roadmap self-checks.

## Prerequisites

You should be comfortable running Python scripts and using a shell, understand processes and virtual memory at a basic level, and know the difference between modules, packages, exceptions, environment variables, and command-line arguments. Earlier lessons on imports, garbage collection, profiling, and concurrency provide useful context.

## Mental model: a runtime doctor joins several evidence sources

A runtime diagnosis is not one magic call. It is a structured snapshot assembled from different layers:

```text
Python process
  ├── sys       → interpreter state, paths, streams, flags, limits
  ├── platform  → OS and machine identification
  ├── sysconfig → build-time configuration and installation paths
  ├── os        → environment, process IDs, filesystem, CPU visibility
  ├── locale    → text encoding preferences and locale settings
  ├── importlib.metadata → installed distribution metadata
  ├── gc / inspect / faulthandler → selected runtime state and diagnostics
  └── OS / container interfaces → affinity, cgroups, process/resource limits
```

These sources answer different questions. `sys.executable` reports the executable associated with the running interpreter; `platform.platform()` describes the platform; `os.cpu_count()` reports logical CPUs known to the OS API, not necessarily CPUs your container can consume. A reliable report preserves those distinctions and records uncertainty rather than presenting a misleading single number.

## 1. Basic runtime introspection with `sys`

### 1.1 What `sys` represents

The standard-library `sys` module exposes information and controls related to the currently running Python interpreter. Most attributes are public and documented, but some names beginning with an underscore are implementation-specific or private. Public does not mean immutable: for example, `sys.path` and `sys.argv` are mutable lists.

| Attribute or function | What it tells you | Operational use and caveat |
|---|---|---|
| `sys.version`, `sys.version_info` | Version string and structured version tuple | Record exact version; `version_info` is easier to compare programmatically. |
| `sys.implementation` | Implementation metadata, including name and cache tag | Distinguishes CPython from other implementations. |
| `sys.executable` | Executable path, often absolute | May be empty or `None` in unusual embedding/launch situations; do not assume a shell command named `python` resolves to it. |
| `sys.argv` | Arguments passed to the script | May contain sensitive command-line values; redact before reporting. |
| `sys.path` | Import search path | Order matters. It may include the current working directory or script directory and can be influenced by environment/configuration. |
| `sys.modules` | Cache of modules currently imported | Not an inventory of every installed package. Avoid mutating it casually. |
| `sys.stdin`, `sys.stdout`, `sys.stderr` | Standard streams | They may be redirected, wrapped, closed, or not attached to a terminal. |
| `sys.flags` | Effective interpreter flags | Useful for recording startup configuration. |
| `sys.byteorder` | Native byte order, `"little"` or `"big"` | Matters for binary interfaces; use explicit byte order for portable formats. |
| `sys.maxsize` | Largest value of a `Py_ssize_t`-like index type | Often signals 32/64-bit build characteristics; it is not the largest integer Python can represent. |
| `sys.getsizeof(obj)` | Shallow size reported by the implementation | Does not recursively include referenced objects and is implementation-specific. |
| `sys.getrecursionlimit()` | Current interpreter recursion limit | Not a safe target to increase without understanding C extensions and stack limits. |
| `sys.getswitchinterval()` | Ideal interpreter thread-switch interval in seconds | A scheduling hint, not a hard real-time guarantee. |
| `sys.getfilesystemencoding()` | Filesystem encoding used by Python | Distinct from terminal encoding and a file's declared text encoding. |

### 1.2 A compact runtime snapshot

```python
# runtime_basics.py
import os
import platform
import sys
import sysconfig

print("version:", sys.version.split()[0])
print("implementation:", sys.implementation.name)
print("executable:", sys.executable)
print("platform:", sys.platform, platform.platform())
print("cwd:", os.getcwd())
print("byteorder:", sys.byteorder)
print("maxsize:", sys.maxsize)
print("flags:", sys.flags)
print("venv prefix differs:", sys.prefix != sys.base_prefix)
print("Py_GIL_DISABLED build setting:", sysconfig.get_config_var("Py_GIL_DISABLED"))
```

**Expected observations:** The exact version, executable, platform, `sys.flags` representation, and build-setting value vary. On a conventional CPython build, `sys.implementation.name` is `cpython`. `sys.prefix != sys.base_prefix` is a common indicator of a virtual environment, not a universal test for every embedded or customized installation. `Py_GIL_DISABLED` may be `None`, `0`, or `1` depending on version and build configuration; do not infer all runtime behavior from this one setting.

`sysconfig.get_config_var("Py_GIL_DISABLED")` is a build-configuration clue associated with free-threaded CPython builds, not a portable language-level API. Where available, a free-threaded CPython build may expose `sys._is_gil_enabled()`; this is a private, version-sensitive diagnostic and can report whether the GIL is currently enabled, which is not the same question as whether the binary was built with free-threading support.

### 1.3 `sys.path`, `sys.modules`, and import diagnosis

`sys.path` is the ordered set of locations searched by the standard path-based import machinery. A local file named `json.py`, `typing.py`, or `logging.py` can shadow a standard-library module if its directory appears earlier in the search path. `sys.modules` caches modules that have already been imported; its keys are module names and values are module objects.

```python
import json
import sys

print("json origin:", json.__spec__.origin)
print("json cached:", "json" in sys.modules)
print("first search paths:", sys.path[:3])
```

The `json.__spec__.origin` value is platform/install-dependent. If an import behaves unexpectedly, inspect `sys.executable`, the current working directory, `sys.path`, and the module's `__file__` or `__spec__.origin` before reinstalling packages. Avoid manually deleting entries from `sys.modules` in production code: references to the old module can remain elsewhere, leading to multiple module objects and inconsistent state. Controlled tests sometimes use `unittest.mock.patch.dict(sys.modules, ...)` to inject a fake module; keep that patch scoped and restore the original mapping. Lazy loading is a separate import-system design (for example, `importlib.util.LazyLoader`) and should not be improvised by editing `sys.modules` alone.

### 1.4 Streams, buffering, and exit behavior

`print()` writes to `sys.stdout` by default. A terminal often uses line buffering, while redirected output may be block-buffered. A container log collector commonly reads redirected streams, so recent output can remain buffered until a buffer fills or the process flushes/exits.

```python
import sys

print("progress record", flush=True)
sys.stderr.write("diagnostic record\n")
sys.stderr.flush()
```

Useful options include `python -u script.py` or `PYTHONUNBUFFERED=1` for unbuffered standard streams. `flush=True` is a targeted alternative. Unbuffered output can add overhead, and it does not make a multi-step log write transactional.

`sys.exit(code)` raises `SystemExit`, allowing normal stack unwinding and cleanup handlers to run. `os._exit(code)` terminates the process immediately without normal Python cleanup and should be reserved for narrow low-level situations, such as after a carefully managed child-process fork. Daemon threads are not guaranteed to finish their work at interpreter shutdown. For services, implement explicit shutdown and flushing rather than relying on interpreter finalization.

## 2. Operating-system information with `os`

### 2.1 Environment, working directory, process identity

- `os.environ` is a mapping representing the process environment as seen by Python. Modifying it updates the environment mapping used by Python and affects children launched afterward; it does not retroactively alter the parent shell.
- `os.getcwd()` returns the current working directory; `os.chdir()` changes it for the process, affecting relative paths throughout the application.
- `os.getpid()` returns the current process ID; `os.getppid()` returns the parent process ID where supported.
- `os.name` is a coarse platform label such as `"posix"` or `"nt"`; `sys.platform` and `platform` provide more detail.
- `os.urandom(n)` returns cryptographically suitable random bytes from the OS source; use `secrets` for common token/password-generation tasks.

```python
import os

print("os.name:", os.name)
print("pid:", os.getpid())
print("cwd:", os.getcwd())
print("PATH entries:", len(os.environ.get("PATH", "").split(os.pathsep)))
```

Do not print the whole environment to a bug report. Variables can contain access tokens, database URLs, proxy credentials, cloud credentials, or internal infrastructure details.

### 2.2 Filesystem inspection

`os.listdir(path)` returns names; `os.scandir(path)` can efficiently expose directory-entry metadata; `os.walk(path)` traverses directory trees. `pathlib.Path` is often a clearer API for application code, while `os` remains useful for process-level diagnostics and lower-level filesystem behavior.

```python
import os
from pathlib import Path

root = Path.cwd()
print("directory entries:", len(os.listdir(root)))

with os.scandir(root) as entries:
    for entry in entries:
        print(entry.name, "dir=" + str(entry.is_dir(follow_symlinks=False)))
        break  # Demonstration only; do not assume any particular entry exists.
```

Directory contents vary. Filesystem metadata calls can fail because of permissions, concurrent changes, broken symlinks, or network filesystem errors. A robust doctor report should capture these failures as unavailable information rather than crash the whole report.

### 2.3 CPU count is not CPU entitlement

`os.cpu_count()` reports the number of logical CPUs in the system as seen by the OS interface. It does **not** necessarily report the number of CPUs a process can use under affinity or container CPU quotas.

- `os.process_cpu_count()` was added in Python 3.13. It reports the logical CPUs usable by the calling process, taking CPU affinity into account where supported. It may still not fully express fractional CPU quota constraints imposed by a container runtime. **Important 3.13+ caveat:** `-X cpu_count=N` and `PYTHON_CPU_COUNT=N` can override both `os.cpu_count()` and `os.process_cpu_count()`. Record whether this override is configured; these values may then reflect an intentional Python-level override rather than a fresh measurement of host or cgroup capacity.
- `len(os.sched_getaffinity(0))` on supported Unix platforms, especially Linux, reports the CPUs in the calling process's affinity mask. It is not available on every OS and does not by itself account for a fractional quota.
- Linux cgroup v2 `cpu.max` expresses quota and period; a finite quota/period ratio can imply fewer CPU-equivalents than the affinity mask. Cgroup v1 exposes related quota and period files in a different layout.
- `os.getloadavg()` is a system load measure where supported, not a CPU limit and not a process-specific utilization percentage.

A useful diagnostic reports several signals rather than pretending one is definitive:

```python
# cpu_capacity.py
import os

print("os.cpu_count:", os.cpu_count())

process_cpu_count = getattr(os, "process_cpu_count", None)
print("os.process_cpu_count:", process_cpu_count() if process_cpu_count else "unavailable before 3.13")

sched_getaffinity = getattr(os, "sched_getaffinity", None)
if sched_getaffinity is not None:
    try:
        print("affinity CPUs:", len(sched_getaffinity(0)))
    except OSError as exc:
        print("affinity CPUs: unavailable:", type(exc).__name__)
else:
    print("affinity CPUs: API unavailable on this platform")
```

**Interpretation:** If the host reports 64 logical CPUs but the process has affinity to 4 CPUs, the process may be limited to those 4 CPUs. If a container has a quota of 1.5 CPU-equivalents, an affinity mask of 4 does not mean it can sustain four full CPUs. Pool sizing should consider the deployment's cgroup limits, workload, latency targets, and observed contention. No one metric captures all scheduler and quota behavior.

### 2.4 Memory and other resource limits

There is no single portable standard-library call that returns a universal “memory available to this process” number. On Unix, `resource.getrlimit()` exposes selected resource limits such as address space or open file descriptors when the platform supports them. `resource.setrlimit()` changes a limit and can cause subsequent operations to fail; do not use it as a casual diagnostic action. It is not a general RSS measurement and some resource constants are absent on Windows.

For Linux containers, cgroup v2 commonly exposes memory limits under `/sys/fs/cgroup/memory.max` and current usage under `memory.current`; a limit string of `max` means no finite limit at that cgroup level. Real deployments may use nested cgroups, cgroup v1, a different mount layout, or additional limits. Read-only diagnostics should treat files as optional and not assume the root cgroup is the process's effective cgroup.

```python
# resource_limits.py — portable checks with optional Unix details
import os

try:
    import resource
except ImportError:
    resource = None

if resource is not None and hasattr(resource, "RLIMIT_NOFILE"):
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        print("open-file limit (soft, hard):", soft, hard)
    except (OSError, ValueError) as exc:
        print("open-file limit: unavailable:", type(exc).__name__)
else:
    print("resource.RLIMIT_NOFILE: unavailable")

for name in ("memory.max", "memory.current", "cpu.max"):
    path = os.path.join("/sys/fs/cgroup", name)
    try:
        with open(path, encoding="ascii") as f:
            print(f"{name}:", f.read().strip())
    except OSError:
        print(f"{name}: unavailable at conventional cgroup-v2 path")
```

The cgroup snippet is a **best-effort probe**, not a full cgroup discovery implementation. For production capacity planning, use the orchestrator's resource configuration and validated cgroup discovery in addition to in-process introspection. Distinguish RSS, virtual address space, Python-tracked allocations, cgroup memory usage, and host free memory; these are different measurements. If RSS is required, an optional dependency such as `psutil` can expose process RSS; Unix `resource.getrusage(resource.RUSAGE_SELF).ru_maxrss` reports a maximum-resident-set measure whose units vary by platform. Label the source and units explicitly rather than comparing raw values across operating systems.

## 3. `platform`, `sysconfig`, locale, timezone, and installed packages

### 3.1 Platform and build configuration

`platform` provides system and implementation identification. `sysconfig` exposes Python installation and build configuration values, such as installation directories, compiler-related settings, and build variables. `sysconfig.get_config_var(name)` retrieves one value; `sysconfig.get_config_vars()` returns the configuration mapping (or selected values when names are supplied). These values are useful for diagnostics but can contain local paths or deployment details that should be redacted for public reports. Do not dump the entire mapping into an externally shared report.

```python
import platform
import sys
import sysconfig

print("implementation:", platform.python_implementation())
print("platform:", platform.platform())
print("machine:", platform.machine())
print("python include:", sysconfig.get_path("include"))
print("SOABI:", sysconfig.get_config_var("SOABI"))
print("configured variable count:", len(sysconfig.get_config_vars()))
print("version:", sys.version.split()[0])
```

`SOABI` and installation paths vary by interpreter, platform, build, and free-threaded ABI. A package wheel compatible with one Python ABI is not automatically compatible with every interpreter build.

### 3.2 Encodings and locale

Three concepts must not be conflated:

1. **Filesystem encoding** (`sys.getfilesystemencoding()`): used to represent filesystem names to Python.
2. **Preferred locale encoding** (`locale.getpreferredencoding(False)`): a locale-related encoding preference; exact behavior depends on platform and Python configuration.
3. **Standard stream encoding** (`sys.stdout.encoding`): may differ because stdout is redirected, wrapped, or configured differently.

```python
import locale
import sys

print("filesystem:", sys.getfilesystemencoding())
print("preferred locale:", locale.getpreferredencoding(False))
print("stdout:", getattr(sys.stdout, "encoding", None))
```

UTF-8 mode can affect Python's text I/O defaults. Do not assume that every file is UTF-8 just because the terminal uses UTF-8; specify encodings when opening text files that have a known encoding, for example `open(path, encoding="utf-8")`.

### 3.3 Time zone

The process environment variable `TZ` can influence time-zone behavior on platforms that support it, but its presence alone does not tell you the full effective time-zone configuration. The `time` module's `tzname` and `time.tzset()` have platform differences; `tzset()` is not available on Windows. `zoneinfo` is the modern standard-library API for IANA time zones, when the required time-zone data is available.

```python
import os
import time
from datetime import datetime

print("TZ environment set:", "TZ" in os.environ)
print("time.tzname:", time.tzname)
print("local now:", datetime.now().astimezone().isoformat())
```

This is a snapshot of the local time-zone interpretation, not proof that the machine has correct wall-clock synchronization. Use UTC timestamps for logs and distributed correlation where appropriate.

### 3.4 Installed package metadata

Use `importlib.metadata` to inspect installed distributions. A distribution is not always a one-to-one match with an import package: for example, distribution names and import names can differ, and namespace packages can span multiple distributions.

```python
from importlib import metadata

for dist in sorted(metadata.distributions(), key=lambda d: (d.metadata.get("Name") or "").lower()):
    name = dist.metadata.get("Name") or "<unnamed>"
    print(name, dist.version)
```

A full package inventory can be large and may reveal internal package names. A doctor report should normally include package names/versions only when needed, optionally limit the list, and make export behavior explicit. Do not import every package just to discover it; metadata lookup avoids executing each package's top-level code.

## 4. Build a safe, machine-readable `doctor` report

A production diagnostic should be useful under failure conditions. It should:

- Emit JSON so CI, support tools, and monitoring can parse it.
- Include version, executable, implementation, virtual-environment clues, flags, import path, platform, encoding, time zone, selected package metadata, CPU signals, and selected resource limits.
- Never return raw environment variables, tokens, credentials, arbitrary command-line arguments, or unredacted URLs with embedded credentials. If environment diagnostics are needed, report allowlisted variable presence/boolean state, never arbitrary values.
- Represent import-path diagnostics with bounded metadata (entry count, empty entries, and entry kinds) by default; raw `sys.path`, executable/prefix paths, and the current working directory can reveal usernames, mount layout, or internal infrastructure.
- Tolerate unavailable OS-specific APIs and permission errors.
- Avoid mutating the process (no `chdir`, environment edits, module cache changes, or resource-limit changes).
- Keep output bounded and avoid collecting thread locals or full stack traces by default, because these may contain secrets and personal data.

### 4.1 A complete small doctor CLI

Save the following as `doctor.py`. It uses standard-library modules and is designed to be read-only. Package inventory is optional and limited to a configurable number of distributions.

```python
from __future__ import annotations

import json
import locale
import os
import platform
import sys
import sysconfig
import threading
import traceback
import gc
import time
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any


def safe_call(fn, default=None):
    """Call an optional diagnostic function without aborting the report."""
    try:
        return fn()
    except (OSError, RuntimeError, ValueError):
        return default


def cgroup_value(filename: str) -> str | None:
    """Best-effort read from the conventional Linux cgroup-v2 mount."""
    try:
        return Path("/sys/fs/cgroup", filename).read_text(encoding="ascii").strip()
    except (OSError, UnicodeError):
        return None


def package_inventory(limit: int = 100) -> dict[str, Any]:
    """Return at most ``limit`` distributions; never import packages.

    The result is intentionally bounded and may not be alphabetically ordered.
    A metadata inventory is not a list of importable modules.
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")
    packages = []
    truncated = False
    try:
        for index, dist in enumerate(metadata.distributions()):
            if index >= limit:
                truncated = True
                break
            try:
                name = dist.metadata.get("Name") or "<unnamed>"
                version = dist.version
            except (OSError, RuntimeError, metadata.PackageNotFoundError) as exc:
                packages.append({"error": type(exc).__name__})
                continue
            packages.append({"name": name, "version": version})
        return {"items": packages, "reported": len(packages), "truncated": truncated}
    except (OSError, RuntimeError, metadata.PackageNotFoundError) as exc:
        return {"error": type(exc).__name__, "items": packages, "truncated": True}


def path_metadata(value: str | None) -> dict[str, Any] | None:
    """Return useful path metadata without exporting the full path string."""
    if not value:
        return None
    return {
        "basename": os.path.basename(value.rstrip(os.sep)) or None,
        "absolute": os.path.isabs(value),
        "exists": safe_call(lambda: os.path.exists(value), None),
        "path_redacted": True,
    }


def import_path_summary() -> dict[str, Any]:
    """Describe sys.path without exporting the actual path strings."""
    entries = []
    for index, entry in enumerate(sys.path[:200]):
        if not isinstance(entry, str):
            kind = "non-string-entry"
        elif entry == "":
            kind = "empty-current-directory-entry"
        elif os.path.isabs(entry):
            kind = "absolute-path"
        else:
            kind = "relative-path"
        entries.append({"index": index, "kind": kind, "path_redacted": True})
    return {"entry_count": len(sys.path), "reported_entries": entries,
            "truncated": len(sys.path) > len(entries)}


def thread_summary(max_threads: int = 32, max_frames: int = 12) -> dict[str, Any]:
    """Return bounded Python stack summaries without locals or source lines."""
    current_frames = getattr(sys, "_current_frames", None)  # Private diagnostic API.
    if current_frames is None:
        return {"available": False, "threads": []}
    try:
        frames = current_frames()
        threads_by_ident = {t.ident: t for t in threading.enumerate()}
        summaries = []
        for ident, frame in list(frames.items())[:max_threads]:
            stack = traceback.extract_stack(frame, limit=max_frames)
            thread = threads_by_ident.get(ident)
            summaries.append({
                "thread_id": ident,
                "thread_name": thread.name if thread is not None else None,
                "daemon": thread.daemon if thread is not None else None,
                "stack": [{"file": os.path.basename(item.filename),
                           "function": item.name, "line": item.lineno}
                          for item in stack],
            })
        return {"available": True, "reported_threads": len(summaries),
                "total_threads_seen": len(frames), "truncated": len(frames) > len(summaries),
                "threads": summaries}
    except (OSError, RuntimeError, ValueError) as exc:
        return {"available": False, "error": type(exc).__name__, "threads": []}


def open_file_summary() -> dict[str, Any]:
    """Count open file descriptors on Linux without returning descriptor targets."""
    path = Path("/proc/self/fd")
    try:
        with os.scandir(path) as entries:
            count = sum(1 for _ in entries)
        return {"available": True, "count": count, "source": "/proc/self/fd"}
    except OSError as exc:
        return {"available": False, "error": type(exc).__name__}


def resource_limit_summary() -> dict[str, Any]:
    """Return selected resource limits when the Unix-only module is available."""
    try:
        import resource
    except ImportError:
        return {"available": False}
    result = {"available": True}
    for label, constant_name in (("open_files", "RLIMIT_NOFILE"), ("address_space", "RLIMIT_AS")):
        constant = getattr(resource, constant_name, None)
        if constant is None:
            result[label] = None
            continue
        try:
            soft, hard = resource.getrlimit(constant)
            result[label] = {"soft": soft, "hard": hard}
        except (OSError, ValueError) as exc:
            result[label] = {"error": type(exc).__name__}
    return result


def build_report(include_packages: bool = False) -> dict[str, Any]:
    process_cpu_count = getattr(os, "process_cpu_count", None)
    sched_getaffinity = getattr(os, "sched_getaffinity", None)

    affinity_count = None
    if sched_getaffinity is not None:
        affinity_count = safe_call(lambda: len(sched_getaffinity(0)))

    gil_check = getattr(sys, "_is_gil_enabled", None)  # Private/version-sensitive.
    report: dict[str, Any] = {
        "schema_version": 1,
        "python": {
            "version": sys.version.split()[0],
            "implementation": sys.implementation.name,
            "executable": path_metadata(sys.executable),
            "prefix": path_metadata(sys.prefix),
            "base_prefix": path_metadata(sys.base_prefix),
            "virtual_environment_hint": sys.prefix != sys.base_prefix,
            "platform_tag": sys.platform,
            "flags": {
                "debug": sys.flags.debug,
                "inspect": sys.flags.inspect,
                "interactive": sys.flags.interactive,
                "optimize": sys.flags.optimize,
                "dont_write_bytecode": sys.flags.dont_write_bytecode,
                "no_user_site": sys.flags.no_user_site,
                "no_site": sys.flags.no_site,
                "ignore_environment": sys.flags.ignore_environment,
                "isolated": sys.flags.isolated,
                "dev_mode": sys.flags.dev_mode,
                "utf8_mode": sys.flags.utf8_mode,
            },
            "byteorder": sys.byteorder,
            "maxsize": sys.maxsize,
            "recursion_limit": sys.getrecursionlimit(),
            "switch_interval_seconds": sys.getswitchinterval(),
            "filesystem_encoding": sys.getfilesystemencoding(),
            "stdout_encoding": getattr(sys.stdout, "encoding", None),
            "streams": {
                name: {
                    "closed": getattr(stream, "closed", None),
                    "encoding": getattr(stream, "encoding", None),
                    "isatty": safe_call(stream.isatty, None) if callable(getattr(stream, "isatty", None)) else None,
                }
                for name, stream in (("stdin", sys.stdin), ("stdout", sys.stdout), ("stderr", sys.stderr))
            },
            "preferred_locale_encoding": safe_call(lambda: locale.getpreferredencoding(False)),
            "import_path_summary": import_path_summary(),
            "python_environment_variable_presence": {
                name: name in os.environ for name in (
                    "PYTHONPATH", "PYTHONHOME", "PYTHONUTF8", "PYTHONUNBUFFERED",
                    "PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED", "PYTHONMALLOC",
                    "PYTHONFAULTHANDLER", "PYTHON_GIL", "PYTHON_CPU_COUNT",
                )
            },
            "gil_disabled_build_setting": sysconfig.get_config_var("Py_GIL_DISABLED"),
            "gil_enabled_now": safe_call(gil_check) if gil_check is not None else None,
        },
        "platform": {
            "description": platform.platform(),
            "python_implementation": platform.python_implementation(),
            "machine": platform.machine(),
            "os_name": os.name,
        },
        "process": {
            "pid": os.getpid(),
            "cwd": safe_call(lambda: path_metadata(os.getcwd()), None),
            "timezone_env_set": "TZ" in os.environ,
            "timezone_names": list(time.tzname),
            "local_time_iso": datetime.now().astimezone().isoformat(),
        },
        "cpu": {
            "os_cpu_count": os.cpu_count(),
            "process_cpu_count": safe_call(process_cpu_count) if process_cpu_count else None,
            "affinity_cpu_count": affinity_count,
            "cpu_count_override_indicator_present": (
                "cpu_count" in getattr(sys, "_xoptions", {}) or "PYTHON_CPU_COUNT" in os.environ
            ),
            "cgroup_v2_cpu_max": cgroup_value("cpu.max"),
        },
        "cgroup_v2": {
            "memory_max": cgroup_value("memory.max"),
            "memory_current": cgroup_value("memory.current"),
        },
        "runtime_diagnostics": {
            "resource_limits": resource_limit_summary(),
            "gc_counts": safe_call(gc.get_count),
            "gc_stats": safe_call(gc.get_stats, []),
            "thread_stacks": thread_summary(),
            "open_files": open_file_summary(),
        },
        "build": {
            "soabi": sysconfig.get_config_var("SOABI"),
            "include_path": path_metadata(sysconfig.get_path("include")),
        },
        # Intentionally omit raw os.environ values, argv, and path strings.
        "security": {
            "environment_values_included": False,
            "arbitrary_environment_variable_names_included": False,
            "allowlisted_environment_variable_presence_included": True,
            "command_line_arguments_included": False,
            "raw_path_strings_included": False,
            "thread_locals_included": False,
            "open_file_targets_included": False,
        },
    }
    if include_packages:
        report["packages"] = package_inventory()
    return report


def main() -> int:
    try:
        print(json.dumps(build_report(include_packages="--packages" in sys.argv[1:]), indent=2, sort_keys=True))
    except BrokenPipeError:
        # Common when piping output to a consumer that exits early.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Run it with:

```bash
python doctor.py
python doctor.py --packages
python doctor.py | python -m json.tool
```

The JSON is **representative**, not a fixed expected result. Some values may be `null` or unavailable on a given platform. The report includes bounded path *metadata* (including basenames) but not full path strings, arbitrary environment variable names/values, command-line arguments, thread locals, or open-file targets. It does expose the names of a fixed allowlist of `PYTHON*` variables together with presence booleans; presence does not prove a variable affected interpreter startup, because it may be ignored by flags or changed after startup. Thread stack summaries are intentionally limited to thread IDs/names, basenames, function names, and line numbers; these are still operational metadata and should be access-controlled. The `/proc/self/fd` probe is Linux-specific and reports a best-effort count only; the directory enumeration itself can transiently affect the count, and descriptors can change during enumeration. `gc.get_stats()` and thread stacks can add overhead, so make them configurable or remove them from high-frequency health checks in latency-sensitive services.

`safe_call` catches expected operational errors, not every possible exception. Broadly catching `Exception` can hide programming defects. If a diagnostic field has a well-defined additional failure mode in your deployment, add a narrow handler and a test for it.

### 4.2 Test redaction rather than trusting it by inspection

Save this as `test_doctor.py` beside `doctor.py`. It verifies the report structure and that deliberately secret-looking environment values are not emitted. It does not prove that every possible secret pattern is absent; the safer design is to omit environment values entirely.

```python
import json
import os
import unittest

import doctor


class DoctorReportTests(unittest.TestCase):
    def test_report_is_json_serializable_and_omits_environment(self):
        old = os.environ.get("DOCTOR_TEST_TOKEN")
        os.environ["DOCTOR_TEST_TOKEN"] = "super-secret-test-value"
        try:
            report = doctor.build_report()
            serialized = json.dumps(report)
            self.assertIn("python", report)
            self.assertIn("cpu", report)
            self.assertNotIn("super-secret-test-value", serialized)
            self.assertNotIn("DOCTOR_TEST_TOKEN", serialized)
            self.assertFalse(report["security"]["environment_values_included"])
            self.assertFalse(report["security"]["arbitrary_environment_variable_names_included"])
            self.assertTrue(report["security"]["allowlisted_environment_variable_presence_included"])
            self.assertFalse(report["security"]["raw_path_strings_included"])
            self.assertIn("import_path_summary", report["python"])
            self.assertIn("runtime_diagnostics", report)
        finally:
            if old is None:
                os.environ.pop("DOCTOR_TEST_TOKEN", None)
            else:
                os.environ["DOCTOR_TEST_TOKEN"] = old

    def test_report_has_a_schema_version(self):
        self.assertEqual(doctor.build_report()["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
```

Run `python -m unittest -v test_doctor.py`. The test mutates the environment only within a `try/finally` and restores the prior value. In a larger test suite, avoid running tests that mutate global environment concurrently in the same process unless synchronized.

## 5. Interpreter flags and `PYTHON*` environment variables

Command-line options and environment variables are read during interpreter startup. The precise effects and availability of `-X` options vary by Python version; check `python --help` and the documentation for the exact interpreter you deploy.

| Option | Main effect | Important caution |
|---|---|---|
| `-I` | Isolated mode; ignores Python environment variables and excludes unsafe path additions such as the script/current directory; implies `-E`, `-P`, and `-s` behavior | Useful for reducing ambient configuration, not a complete security sandbox. |
| `-E` | Ignore `PYTHON*` environment variables | Does not remove arbitrary application environment variables. |
| `-S` | Do not automatically import `site` during startup | Changes site-package and customization setup; exact virtual-environment prefix behavior changed in Python 3.14. |
| `-O` | Set optimization level 1; removes `assert` statements and sets `__debug__` false | Never use `assert` for security checks or user-input validation. |
| `-OO` | Optimization level 2; also discards docstrings | Can affect tools that depend on docstrings. |
| `-X dev` | Enable development mode, including additional runtime checks and warnings | Adds overhead; useful in tests/staging, not necessarily as a default for throughput-sensitive production. |
| `-X utf8` | Enable UTF-8 mode | Can change default text encoding behavior; explicitly set encodings for files with known formats. |
| `-X importtime` | Print import timing information | Output goes to stderr and can be noisy; use it for diagnosis, not as a benchmark with no instrumentation. |
| `-X faulthandler` | Enable fault-handler support for fatal errors | Useful for crash diagnosis; ensure diagnostic output is routed and retained safely. |
| `-W ...` | Configure warning filters | Warning policy should be tested; suppressing all warnings can hide deprecations. |
| `-u` | Force `stdout` and `stderr` to be unbuffered (including the text layer on modern Python) | It does not unbuffer `stdin`; may increase I/O overhead. |

Common environment variables include:

| Variable | Use | Caveat |
|---|---|---|
| `PYTHONPATH` | Add import search locations | Can shadow trusted modules or introduce untrusted code. |
| `PYTHONHASHSEED` | Control hash randomization seed or disable randomization with supported values | Fixed seeds can make some behavior reproducible but reduce per-process hash randomization; do not choose casually for services. |
| `PYTHONUNBUFFERED` | Similar intent to `-u` for standard streams | Set to a non-empty value to enable unbuffered mode. |
| `PYTHONDONTWRITEBYTECODE` | Avoid writing `.pyc` files | Does not stop Python from reading existing bytecode caches. |
| `PYTHONUTF8` | Enable/disable UTF-8 mode where supported | Startup behavior and precedence are version-dependent. |
| `PYTHONMALLOC` | Select supported allocator/debug options in CPython | Values and effects depend on build/version; debug allocator modes are for diagnosis and can affect performance. |
| `PYTHONFAULTHANDLER` | Enable fault-handler behavior | Check the exact version's documented accepted values and command-line precedence. |
| `PYTHON_GIL` | Configure GIL behavior for supported free-threaded CPython builds | Relevant to free-threaded builds and version-specific; not a general GIL switch for conventional builds. |
| `PYTHON_CPU_COUNT` (3.13+) | Override CPU-count API results, alongside `-X cpu_count` | This is a Python-level override, not evidence of actual host, affinity, or cgroup capacity. |
| `PYTHONWARNINGS` | Configure warning filters | Same policy concerns as `-W`. |
| `PYTHONBREAKPOINT` | Configure the `breakpoint()` hook | A customized hook can execute code; consider it in controlled environments. |

Inspect effective flags with `sys.flags`, but remember not every `-X` option appears as a named `sys.flags` field. `sys._xoptions` exposes `-X` options in a dictionary, but its details should be treated as interpreter-specific diagnostic state.

### 5.1 Reproducible startup experiments

Create `startup_probe.py`:

```python
import json
import sys

print(json.dumps({
    "flags": {
        "isolated": sys.flags.isolated,
        "ignore_environment": sys.flags.ignore_environment,
        "no_site": sys.flags.no_site,
        "optimize": sys.flags.optimize,
        "utf8_mode": sys.flags.utf8_mode,
        "dev_mode": sys.flags.dev_mode,
    },
    "path_head": sys.path[:2],
    "xoptions": getattr(sys, "_xoptions", {}),
}, indent=2, default=str))
```

Compare:

```bash
python startup_probe.py
python -E startup_probe.py
python -S startup_probe.py
python -I startup_probe.py
python -X dev -X utf8 startup_probe.py
```

**Expected observations:** Flags differ; path entries may differ; `-I` ignores `PYTHONPATH` and avoids unsafe path prepending. Do not expect identical path layouts across operating systems, virtual environments, launch modes, or Python versions. This experiment shows startup configuration differences; it does not prove an application is secure merely because it uses `-I`.

## 6. Deeper runtime diagnostics

### 6.1 `inspect`: examine live Python objects

`inspect` can report signatures, source locations (when source is available), members, and whether an object is a coroutine, generator, or class. Introspection can fail for built-ins, dynamically generated functions, frozen modules, optimized code, or objects whose source is unavailable.

```python
import inspect


def transform(value: str, *, strip: bool = True) -> str:
    return value.strip() if strip else value

print(inspect.signature(transform))
print(inspect.isfunction(transform))
print(inspect.getsourcefile(transform))
```

Do not expose function locals, frame locals, or full source text in public diagnostics by default. Locals can contain passwords, customer records, tokens, and personal data.

### 6.2 Garbage collection and allocation tracing

`gc` exposes the cyclic garbage collector for container cycles and related runtime statistics. CPython also uses reference counting, but reference counting and cyclic GC are different mechanisms. `gc.get_count()` returns collection-generation counters; `gc.get_stats()` returns per-generation statistics on supported implementations. `gc.get_objects()` can be expensive and may expose sensitive object graphs; it is not a lightweight health metric for every request.

`tracemalloc` records Python memory allocations made after tracing starts. It helps attribute Python-tracked allocations to source locations, but it is not a complete process RSS profiler and does not necessarily account for native allocations made by extensions or all allocator overhead.

```python
import gc
import tracemalloc

tracemalloc.start(10)
items = [{"id": i, "value": str(i)} for i in range(10_000)]
current, peak = tracemalloc.get_traced_memory()
print("traced current bytes:", current)
print("traced peak bytes:", peak)
print("GC counts:", gc.get_count())
print("GC stats:", gc.get_stats())
tracemalloc.stop()
del items
```

The byte counts depend on the workload and interpreter. Start tracing before the allocations you want to measure. The example does not prove that every byte allocated by the process is traced, nor does deleting `items` guarantee an immediate drop in RSS.

### 6.3 `faulthandler` and thread snapshots

`faulthandler` can dump Python tracebacks on fatal faults and, on supported platforms, after a timeout or in response to a signal. It is especially useful when a process is hung or crashes inside native code. Its output is diagnostic evidence, not a complete native stack trace or root-cause proof. Version/build caveat: CPython 3.14 free-threaded builds may dump only the current thread when the GIL is disabled, even if `all_threads=True`; consult the documentation for the exact build.

```python
import faulthandler
import sys

faulthandler.enable(file=sys.stderr, all_threads=True)
# For a temporary hang investigation, a controlled program may use:
# faulthandler.dump_traceback_later(30, repeat=False, file=sys.stderr)
```

Cancel a scheduled dump with `faulthandler.cancel_dump_traceback_later()` when it is no longer needed. On Unix systems that define `SIGUSR1`, a process may register that signal for on-demand stack dumps, but the file must remain open while registered and the signal may already be owned by the application or supervisor:

```python
import faulthandler
import signal

if hasattr(signal, "SIGUSR1"):
    stack_log = open("python-stacks.log", "a", buffering=1, encoding="utf-8")
    try:
        faulthandler.register(signal.SIGUSR1, file=stack_log, all_threads=True)
        # Keep stack_log open while the registration is active.
        # During shutdown, unregister the signal before closing the file.
    except (OSError, RuntimeError, ValueError):
        stack_log.close()
        raise
```

In a real service, retain `stack_log` in the component that owns the registration and call `faulthandler.unregister(signal.SIGUSR1)` before closing it. Signal registration APIs are platform-specific and require careful handling in services; do not install a signal handler without coordinating with the application's signal/shutdown design.

`sys._current_frames()` is a private diagnostic API that returns current top frames for threads, useful for deadlock investigation. `sys._current_exceptions()` is also private and version-sensitive: in Python 3.12+, each dictionary value is an exception instance; older versions returned the three-item tuple shape from `sys.exc_info()`. Prefer a supported profiler/debugger or a carefully controlled diagnostic path; frame snapshots can expose sensitive locals and retaining frames can keep objects alive.

### 6.4 Trace hooks and monitoring

`sys.settrace()` and `sys.setprofile()` support debuggers and profilers but can impose substantial overhead. `sys.monitoring`, introduced in Python 3.12 by PEP 669, offers a lower-impact event API for tools. It is a separate subject in Lesson 10. Do not leave high-overhead tracing enabled in production without measuring its effect, and do not assume that a profiler sees exactly the same execution costs as an uninstrumented run.

### 6.5 Audit hooks: useful visibility, not a sandbox

`sys.addaudithook()` can observe documented audit events such as `open`, `exec`, `import`, `socket.connect`, `subprocess.Popen`, and `os.system` (event availability and arguments are documented per event). A hook can implement a policy logger or reject selected operations by raising an exception, but it is not a general sandbox: native code and other execution paths can bypass Python-level assumptions, and audit events are not guaranteed to describe every relevant OS action. Hooks cannot be removed through the public API, so install them deliberately and avoid treating a logging hook as a complete security boundary. Do not rely on an audit hook alone to run untrusted code safely.

### 6.6 Process hooks, signals, limits, and less-common `sys` details

A few APIs are especially useful when a process is failing or being shut down:

- `sys.excepthook` is called for an uncaught exception at the top level of the main thread. `threading.excepthook` handles uncaught exceptions from `threading.Thread.run()`. `sys.unraisablehook` handles exceptions that cannot be propagated normally (for example, some failures in finalizers). Custom hooks should preserve the default reporting behavior when possible, avoid leaking exception locals, and must not raise secondary exceptions that obscure the original failure.
- `signal.signal()` configures signal handlers where supported. Python signal handlers are generally executed in the main thread of the main interpreter; they are not a general-purpose inter-thread messaging API. `signal.alarm()` is Unix-specific. Use `SIGTERM` for graceful service shutdown and coordinate signal handling with the application's event loop and worker lifecycle. Do not replace existing handlers without understanding the host framework.
- `atexit.register()` runs callbacks during normal interpreter shutdown, but not after every termination mode (for example, `os._exit()` or a fatal process crash). It is not a substitute for explicit resource ownership and shutdown sequencing.
- `resource.getrlimit()` reports selected OS resource limits where the module exists. The returned soft limit is the current enforced limit and the hard limit is the ceiling for unprivileged changes; values can include `resource.RLIM_INFINITY`. Inspect limits before changing them. Increasing a limit can move the failure elsewhere rather than solve resource exhaustion.
- `sys.getrefcount(obj)` is a CPython-specific diagnostic and the call itself temporarily adds a reference; the value is not a stable count of all conceptual owners. `sys.intern(text)` interns a string, but interning should not be used as a general-purpose memory optimization without evidence.
- `sys.orig_argv` (available in modern CPython versions) preserves the original interpreter command-line arguments, including interpreter options, whereas `sys.argv` is the application argument vector. Both can contain secrets if operators pass credentials on the command line; do not dump either wholesale.
- `runpy` can run modules or scripts in a Python namespace (`runpy.run_module()` and `runpy.run_path()`). It is useful for tooling and `python -m`-like behavior, but running code is still code execution: it is not a safe way to inspect an untrusted module without executing it.

For load and disk signals, `os.getloadavg()` (where available) describes system load averages and `shutil.disk_usage(path)` reports filesystem capacity for the path. Neither is a direct measurement of a Python process's CPU utilization or memory headroom. Open-file counts can be inspected through OS-specific mechanisms such as `/proc/self/fd` on Linux, but `/proc` is not portable and file descriptors may change while being counted. Optional metrics should be labelled with their source and timestamp.

```python
import os
import shutil
import sys

print("original argv available:", hasattr(sys, "orig_argv"))
print("load average API available:", hasattr(os, "getloadavg"))
print("disk usage:", shutil.disk_usage("."))
```

This snippet deliberately prints whether an API exists rather than assuming every OS supports it. `shutil.disk_usage(".")` reports the filesystem containing the current directory, not the entire machine's storage capacity.

## 7. Interpreter startup and deployment safety

Python startup can be affected by `PYTHONPATH`, `.pth` files, `sitecustomize`, `usercustomize`, `PYTHONSTARTUP` in interactive contexts, the current working directory, and installed import hooks. `.pth` files can contain executable import lines, so writable or untrusted site-package locations are a code-execution risk. Isolated mode (`-I`) reduces several ambient influences, but it does not replace OS permissions, dependency integrity, container isolation, or application security controls.

Platform-specific interpretation matters. On Windows, `os.name == "nt"`; Unix-only facilities such as `resource`, `os.sched_getaffinity`, `time.tzset`, and `signal.alarm` may be absent, `fork` is not available through `multiprocessing`, and console encoding behavior differs from redirected streams. On macOS, `spawn` is the default `multiprocessing` start method in the target versions; process creation and code-signing/runtime policy can differ from Linux, and Linux `/proc` or cgroup paths should not be assumed to exist. On POSIX, CPython 3.14 changes the default start method away from `fork` to `forkserver` where supported, so inspect `multiprocessing.get_start_method()` in the actual deployment. Linux distributions may use glibc or musl, which matters for native extension compatibility; WSL2 adds a Linux environment behind a Windows host and does not make all host and container resource signals interchangeable.

Practical safe practices:

1. Record `sys.executable` and the exact version in incident reports so the diagnosis refers to the interpreter actually running the process.
2. Avoid printing `os.environ`, command-line arguments, credentials, frame locals, or full filesystem paths without an explicit data-handling policy.
3. Make diagnostic endpoints authenticated, access-controlled, and disabled unless needed; bound output size and avoid expensive heap walks on request paths.
4. Prefer read-only probes. Changing limits, signal handlers, working directories, environment variables, `sys.path`, or `sys.modules` can alter application behavior.
5. Use `python -X dev` and warning checks in CI/staging; capture faulthandler output for hangs/crashes where operationally appropriate.
6. Treat platform-specific metrics as optional. A doctor report should degrade gracefully, not fail because an API or cgroup file is unavailable.
7. In containers, size worker pools against actual CPU and memory constraints rather than host-level values alone.

## 8. Experiments and exercises

### Experiment A — Compare normal, isolated, and no-site startup

**Question:** Which startup settings change interpreter flags and import paths?

**Setup:** Save `startup_probe.py` from Section 5.1. Optionally set `PYTHONPATH` to a harmless temporary directory containing a small test module.

**Procedure:** Run the five commands listed in Section 5.1. Compare `isolated`, `ignore_environment`, `no_site`, `utf8_mode`, `optimize`, and the first two `sys.path` entries.

**Expected observations:** Flags reflect the options; `-I` ignores Python environment variables and removes unsafe path additions; `-S` skips `site` startup processing. Exact paths vary by installation and version.

**Interpretation:** Startup flags are part of the process configuration and can explain “works in my shell but not in production” import behavior.

**Does not prove:** That isolated mode is a complete sandbox, that all environment variables are ignored, or that startup paths are identical on all machines.

### Experiment B — Host CPU count versus process/container constraints

**Question:** Does the OS-wide CPU count equal the CPUs this process can use?

**Setup:** Run `python cpu_capacity.py` from Section 2.3 on a host and, if available, inside a container with an explicit CPU limit.

**Procedure:** Record `os.cpu_count()`, `os.process_cpu_count()` when present, affinity count when supported, and cgroup `cpu.max` if visible. Repeat under different container limits.

**Expected observations:** Host CPU count may remain high while process affinity or quota constrains execution. On older Python versions, `os.process_cpu_count()` is absent.

**Interpretation:** Capacity decisions require deployment context; a fractional quota may be lower than the count of CPUs in the affinity mask.

**Does not prove:** Exact throughput, scheduler latency, or a universal usable-CPU count. Quotas, nested cgroups, and orchestration settings must be understood.

### Exercise C — Build and test the doctor report

**Task:** Implement `doctor.py` and `test_doctor.py` as shown above, then extend them with a versioned JSON schema and one or two carefully selected runtime facts relevant to your service.

**Requirements:**

1. `python doctor.py | python -m json.tool` parses successfully.
2. `python -m unittest -v test_doctor.py` passes.
3. The report never includes raw environment values or `sys.argv`.
4. Optional APIs and platform-specific probes return `null`/an availability marker when absent or inaccessible.
5. Document which fields are public APIs and which are private/version-sensitive.

**Expected observations:** The report is valid JSON and tests verify key safety properties. Field values vary by environment.

**Interpretation:** Diagnostics become maintainable when their schema and redaction behavior are tested, not just manually inspected.

**Does not prove:** That every possible secret is absent from all fields, that every OS/cgroup layout is discovered, or that a JSON report is safe to expose publicly. Perform a separate data review before exporting it.

### Exercise D — Diagnose delayed container logs

**Question:** Why might `print()` output appear late in a container?

**Procedure:** Run a program that prints a progress marker and waits, once with normal buffering and once with `python -u` or `PYTHONUNBUFFERED=1`. Observe the logs from the parent terminal or container runtime. Use `flush=True` for a targeted marker.

**Expected observations:** Redirected output may be buffered; unbuffered mode or explicit flush makes the marker visible sooner.

**Interpretation:** Output visibility depends on buffering in Python and potentially downstream log collectors.

**Does not prove:** That all log delay is Python buffering. Runtime collection, network transport, aggregation, and viewer refresh can also add latency.

## 9. Common mistakes and troubleshooting

| Symptom or mistaken assumption | Better diagnostic approach |
|---|---|
| “`os.cpu_count()` tells me the worker count for a Kubernetes pod.” | Compare `os.process_cpu_count()` on 3.13+, CPU affinity, cgroup quota/period, and orchestrator limits. Check whether `-X cpu_count` / `PYTHON_CPU_COUNT` overrides the API result, then measure workload behavior. |
| “`sys.maxsize` is Python's maximum integer.” | Python integers have arbitrary precision; `sys.maxsize` is a platform-sized index bound. |
| “`sys.getsizeof()` is total memory usage.” | It is shallow and implementation-specific. Use `tracemalloc` for Python-tracked allocation attribution and OS metrics for process/cgroup memory. |
| “A package is installed because its name appears in `sys.modules`.” | `sys.modules` lists imported modules, not all installed distributions. Use `importlib.metadata` for installed distribution metadata. |
| “The filesystem encoding is the encoding of every text file.” | Specify the file encoding based on the file format; inspect stream and locale encodings separately. |
| “The `TZ` variable proves the time zone is correct.” | Inspect actual local-time behavior and deployment configuration; clock synchronization is a separate issue. |
| “Print all environment variables in a support bundle.” | Report allowlisted names or presence/boolean indicators, not raw values. Redact credentials in URLs and command-line arguments too. |
| “`-I` makes arbitrary Python code safe.” | It reduces startup environment/path influence; it is not a sandbox. Use OS-level isolation and permissions for untrusted code. |
| “`faulthandler` always gives a complete native stack.” | It primarily dumps Python tracebacks. Use native debuggers/profilers when native frames are required. |
| “A failed optional probe should abort the whole doctor report.” | Catch expected OS/permission/API errors narrowly and emit an unavailable value. Do not suppress arbitrary bugs silently. |
| “A diagnostic endpoint can return all frame locals.” | Locals may contain secrets and large object graphs; restrict access, minimize fields, and retain only when needed. |

### A practical incident sequence

1. Confirm executable/version: `python -c "import sys; print(sys.version); print(sys.executable)"` using the same launcher/container as the service.
2. Record interpreter flags and platform: run the compact snapshot or doctor CLI in the actual deployment environment.
3. Confirm import resolution: inspect `sys.path` and module `__spec__.origin` for the failing import; do not dump all environment values.
4. Compare CPU signals and deployment limits before tuning thread/process pools.
5. For a hang, capture thread stacks with an approved tool or `faulthandler`; for memory growth, compare `tracemalloc` snapshots with RSS/cgroup usage.
6. Preserve exact commands, versions, timestamps, redacted JSON output, and the environment in which the observation was made.
7. Change one configuration at a time and verify the behavior using the same workload. Avoid changing limits or interpreter startup flags in production without a rollback plan.

## 10. Concept map and summary

```text
Runtime question
  ├── Which Python? ── sys.version / sys.executable / sys.implementation
  ├── How did it start? ── sys.flags / sys.path / sys._xoptions / env policy
  ├── Where is it running? ── platform / sysconfig / os.name
  ├── What can it use? ── CPU count + affinity + cgroups + resource limits
  ├── What is it doing? ── inspect / faulthandler / thread snapshots
  ├── Where is memory going? ── tracemalloc + gc + OS RSS/cgroup metrics
  └── How do we report safely? ── JSON schema + redaction + bounded optional probes
```

Key takeaways:

- `sys` describes the active interpreter; `os` exposes process and operating-system interfaces; `platform` and `sysconfig` describe the platform and build.
- A good doctor report combines evidence from these layers and preserves uncertainty.
- Host CPU count, process affinity, cgroup CPU quota, RSS, Python-tracked allocations, and cgroup memory usage are different facts.
- Interpreter flags and `PYTHON*` variables can change startup, imports, buffering, encodings, diagnostics, and allocator behavior.
- Private APIs such as `sys._current_frames()`, `sys._current_exceptions()`, `sys._xoptions`, and `sys._is_gil_enabled()` are version-sensitive; guard their use and do not treat them as language guarantees.
- Diagnostics themselves can leak secrets, retain objects, consume resources, or perturb timing. Make them bounded, read-only where possible, and access-controlled.

## 11. Self-check questions with answers

### 1. How do you reliably find usable CPUs in a Kubernetes pod from Python?

There is no single universally reliable number from one API. Start with `os.cpu_count()` for OS-visible logical CPUs. On Python 3.13+, inspect `os.process_cpu_count()`; on supported Linux systems, inspect `len(os.sched_getaffinity(0))`. Check whether `-X cpu_count` or `PYTHON_CPU_COUNT` is configured at interpreter startup; a current environment-variable presence check alone cannot prove it was applied. Then check the effective cgroup CPU quota/period (`cpu.max` on cgroup v2, or the corresponding v1 files) and the pod's configured CPU limits. A quota of 1.5 CPU-equivalents can constrain sustained CPU use even if affinity exposes several CPUs. Use the combined evidence and verify with workload measurements.

### 2. Why do prints from a containerised Python job show up late, and how do you fix it?

When stdout is redirected rather than attached to an interactive terminal, output may be block-buffered. Use `python -u script.py`, set `PYTHONUNBUFFERED=1`, or call `print(..., flush=True)` for selected records. Also inspect the container runtime and log aggregation path: buffering may occur downstream too. Unbuffered output is not a guarantee of end-to-end immediate delivery.

### 3. Implement `doctor` with redaction and a unit test that asserts no secret-like values appear.

Use the `build_report()` example above and test it with a sentinel environment variable containing a fake token. The safest strategy is not to include arbitrary environment values at all; a denylist or regex-only redaction can miss new secret formats. The example test checks that both the sentinel value and its variable name are absent from the serialized report. Extend tests for any additional fields your service adds, and review path, package, command-line, and frame data separately before sharing reports externally.

## References

Official documentation and specifications are the source of truth for exact versions and platform support. Check the documentation matching the interpreter you actually deploy.

- Python `sys` documentation: https://docs.python.org/3/library/sys.html
- Python `os` documentation: https://docs.python.org/3/library/os.html
- Python `platform` documentation: https://docs.python.org/3/library/platform.html
- Python `sysconfig` documentation: https://docs.python.org/3/library/sysconfig.html
- Python `locale` documentation: https://docs.python.org/3/library/locale.html
- Python `inspect` documentation: https://docs.python.org/3/library/inspect.html
- Python `gc` documentation: https://docs.python.org/3/library/gc.html
- Python `faulthandler` documentation: https://docs.python.org/3/library/faulthandler.html
- Python `tracemalloc` documentation: https://docs.python.org/3/library/tracemalloc.html
- Python command-line and environment variables: https://docs.python.org/3/using/cmdline.html
- Python 3.13 `os` CPU-count API and override semantics: https://docs.python.org/3.13/library/os.html#os.process_cpu_count
- Python 3.13 command-line and environment changes: https://docs.python.org/3.13/using/cmdline.html
- Python virtual environments (PEP 405): https://peps.python.org/pep-0405/
- Python `importlib.metadata`: https://docs.python.org/3/library/importlib.metadata.html
- Python `sys.monitoring` and PEP 669: https://peps.python.org/pep-0669/
- CPython source tree for version-specific implementation details: https://github.com/python/cpython

For version-specific claims, consult the “What’s New” documentation for Python 3.12, 3.13, and 3.14, especially changes to virtual-environment prefix initialization, process CPU introspection, and free-threaded builds. Do not assume that private APIs or OS-specific paths behave identically across all builds.
