# Testing CLI and Subprocess Programs

> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 16 — Advanced Testing and Test Architecture  
> **Lesson:** 06 of 09  
> **Target:** Python 3.12+, pytest 8+  
> **Prerequisites:** pytest fixtures and monkeypatching; CLI argument parsing and exit codes; `subprocess`, `tempfile`, and file handling; test doubles and captured output.

## Learning outcomes

By the end of this lesson, you should be able to:

- Design a command-line interface (CLI) with a testable `main(argv: list[str] | None = None) -> int` function and a correct module entry point.
- Test command behavior in-process with `capsys`, `capfd`, and `pytest.raises(SystemExit)`.
- Test the real executable path with `subprocess.run`, argument lists, `sys.executable`, captured output, timeouts, controlled environment variables, and explicit working directories.
- Verify module execution, installed console scripts, package entry points, standard input, exit codes, signals, and long-running behavior.
- Test help/version/verbosity, logging, idempotency, dry-run behavior, and external commands through a fake `PATH`.
- Recognize when Click/Typer helpers or a pseudo-terminal are appropriate.
- Test automation-facing contracts, including JSON output, stdout/stderr conventions, broken pipes, permissions, disk failures, large inputs, and resumable jobs.
- Collect subprocess coverage, account for cross-platform differences, and build a sensible CLI test pyramid.

---

## 1. The CLI is a public API

A command-line program is not just a Python function. It is an interface consumed by people, shell scripts, schedulers, CI jobs, containers, and other programs. Its contract includes:

- Accepted arguments, options, defaults, and validation.
- Standard output (`stdout`) for primary output and standard error (`stderr`) for diagnostics.
- Exit status, including distinctions between success, usage errors, and operational failures.
- Input/output encoding and line format.
- Filesystem effects, environment-variable behavior, and working-directory assumptions.
- Signal handling, interruption, and cleanup behavior.
- Compatibility expectations for machine-readable formats.

Changing a message, output stream, exit code, or option can break downstream automation even if the core Python function still works. Tests should assert the intended public contract rather than internal implementation details.

## 2. Design for testability: `main(argv)`

### 2.1 Keep import-time behavior boring

Avoid parsing arguments, reading files, printing, or starting work at module import time. Imports happen during test collection, IDE indexing, documentation builds, and other contexts where the command should not run.

Use this structure:

```python
# ledger_cli.py (project root; adapt import/install setup for a src/ layout)
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize a ledger JSON file.")
    parser.add_argument("input", type=Path, help="path to a JSON array of records")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--verbose", action="store_true", help="log progress to stderr")
    parser.add_argument("--version", action="version", version="ledger-cli 1.0.0")
    return parser


def run_report(input_path: Path) -> dict[str, int]:
    """Core logic: load and summarize data; no CLI printing or sys.exit."""
    with input_path.open(encoding="utf-8") as handle:
        records = json.load(handle)

    if not isinstance(records, list):
        raise ValueError("input must be a JSON array")

    total = 0
    for index, record in enumerate(records):
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("amount"), int)
            or isinstance(record.get("amount"), bool)
        ):
            raise ValueError(f"record {index} must contain an integer amount")
        total += record["amount"]

    return {"count": len(records), "total": total}


def main(argv: list[str] | None = None) -> int:
    """Return an exit code; use argv=None to read the real process arguments."""
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = logging.getLogger("ledger_cli")
    if args.verbose:
        logger.debug("processing input %s", args.input)

    try:
        report = run_report(args.input)
    except FileNotFoundError:
        print(f"ledger-cli: input file not found: {args.input}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ledger-cli: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(f"Records: {report['count']}")
        print(f"Total: {report['total']}")
    return 0


def cli() -> None:
    """Process-boundary wrapper used by both `python -m` and console scripts."""
    if "--verbose" in sys.argv[1:]:
        logging.basicConfig(
            level=logging.DEBUG,
            stream=sys.stderr,
            format="%(levelname)s: %(message)s",
        )
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
```

The core computation is separate from CLI parsing and output. `main(argv)` is straightforward to call in a unit test, and the `if __name__ == "__main__"` guard makes `python -m ledger_cli` execute the CLI without triggering it during import. When launched as a process with `--verbose`, the `cli()` process-boundary wrapper configures logging to stderr before calling `main`. Point both `python -m ledger_cli` and the installed console script at this wrapper so verbosity behaves the same in both launch modes. An in-process test can call `main([...])` and capture the named logger with `caplog` without reconfiguring global logging. Keeping logger configuration outside `main()` makes repeated in-process calls easier to test.

**Why return an integer?** It makes the result explicit and testable. `raise SystemExit(main())` is reserved for the process boundary. Calling `sys.exit()` deep inside core logic makes ordinary unit tests harder and couples the logic to process termination.

`argparse` itself handles syntax errors and `--help`/`--version` by raising `SystemExit`. A valid invocation reaches the return statements. This distinction matters in tests: success and application errors can be asserted through the return code, while parser exits need `pytest.raises(SystemExit)` or a real subprocess test.

### 2.2 The process contract

A common convention is:

| Outcome | Typical status | Output stream |
|---|---:|---|
| Successful operation | `0` | Result on stdout |
| Operational failure, such as missing input | `1` | Diagnostic on stderr |
| Invalid command-line syntax/option | `2` with `argparse` | Parser diagnostic on stderr |
| Interrupted by Ctrl+C | Often `130` in shell conventions | Optional interruption diagnostic on stderr |

These are conventions, not universal laws. A CLI should document its status codes and test the documented contract. `argparse` normally exits with status `2` for invalid arguments. A Python exception that escapes uncaught usually produces a traceback and status `1`. On POSIX, a process terminated by a signal can be represented by a negative `returncode` in `subprocess`; a shell often reports signal termination as `128 + signal_number` (for `SIGINT`, commonly `130`). Windows signal behavior differs.

### 2.3 Installable console-script entry points

A packaged project may expose the CLI as a console script. For example, in `pyproject.toml`:

```toml
[project]
name = "ledger-cli"
version = "1.0.0"
requires-python = ">=3.12"

[project.scripts]
ledger-cli = "ledger_cli:cli"
```

For this simple layout, `ledger_cli.py` must be importable as a top-level module in the installed package. The `cli()` wrapper performs process-level logging setup and raises `SystemExit(main())`; configure the console script to call that wrapper. In a real package, use an importable package module and configure package discovery/building correctly. The conventional generated console-script launcher wraps its target's return value in `sys.exit`, but a wrapper is useful when the process boundary must configure logging or other process-level behavior consistently. Verify the installed executable end to end.

For `python -m package_name`, add a `package_name/__main__.py`:

```python
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

The import path used by `python -m package_name` is different from executing an arbitrary file path. Test the exact form users are expected to run.

---

## 3. In-process tests: fast feedback

In-process tests invoke `main()` directly. They are fast and useful for arguments, output, environment behavior, and core contracts, but they do **not** verify a generated console-script launcher, a fresh interpreter, installed-package metadata, or OS-level signal behavior.

Assume the example above is available as `ledger_cli.py` and importable in the test environment.

### 3.1 Success, stdout, stderr, and return code

```python
import json

from ledger_cli import main


def test_success_json_output(tmp_path, capsys):
    source = tmp_path / "records.json"
    source.write_text(json.dumps([{"amount": 10}, {"amount": 5}]), encoding="utf-8")

    code = main([str(source), "--json"])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out == '{"count": 2, "total": 15}\n'
    assert captured.err == ""
```

Expected contract: return code `0`, one JSON object on stdout followed by a newline, and no diagnostic on stderr. The input file lives under pytest's isolated `tmp_path`; no test depends on the repository's current directory.

A human-readable output test:

```python
def test_human_output(tmp_path, capsys):
    source = tmp_path / "records.json"
    source.write_text('[{"amount": 4}]', encoding="utf-8")

    code = main([str(source)])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out == "Records: 1\nTotal: 4\n"
    assert captured.err == ""
```

### 3.2 Operational errors

```python
def test_missing_file_is_a_clean_error(tmp_path, capsys):
    missing = tmp_path / "missing.json"

    code = main([str(missing)])
    captured = capsys.readouterr()

    assert code == 1
    assert captured.out == ""
    assert captured.err == f"ledger-cli: input file not found: {missing}\n"
```

This test checks the behavior implemented in `main`. It intentionally does not assert the exact wording of operating-system exception messages, which vary by platform.

### 3.3 `capsys` versus `capfd`

- `capsys` captures writes made through Python's `sys.stdout` and `sys.stderr`.
- `capfd` captures writes to the underlying file descriptors 1 and 2. It is useful when code or a native library writes directly to file descriptors, or a child process inherits those descriptors.
- Both provide `readouterr()` to retrieve captured output so far; subsequent writes can be captured separately.

Example of Python-level output:

```python
def test_python_print(capsys):
    print("ready")
    captured = capsys.readouterr()
    assert captured.out == "ready\n"
    assert captured.err == ""
```

Example of file-descriptor output on platforms with `os.write` support:

```python
import os

def test_fd_output(capfd):
    os.write(1, b"native-style output\n")
    captured = capfd.readouterr()
    assert captured.out == "native-style output\n"
    assert captured.err == ""
```

Use the narrowest fixture that captures the behavior you need. Do not mix `capsys` and `capfd` in the same test without a clear reason.

### 3.4 `SystemExit`, `--help`, bad flags, and `--version`

`argparse` prints help and exits by raising `SystemExit(0)`. Invalid flags normally raise `SystemExit(2)` and print a diagnostic to stderr.

```python
import pytest
from ledger_cli import main


def test_help_exits_successfully(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])

    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "usage:" in captured.out.lower()
    assert "Summarize a ledger JSON file" in captured.out
    assert captured.err == ""


def test_bad_flag_exits_with_usage_error(tmp_path, capsys):
    source = tmp_path / "records.json"
    source.write_text("[]", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        main([str(source), "--unknown-option"])

    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert captured.out == ""
    assert "unrecognized arguments" in captured.err
```

`--version` is also handled by `argparse` in the example:

```python
def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    captured = capsys.readouterr()

    assert exc.value.code == 0
    assert captured.out == "ledger-cli 1.0.0\n"
    assert captured.err == ""
```

Avoid asserting every character of help output unless exact formatting is a deliberate compatibility contract. Test stable essentials—usage, important option names, exit code—and use a reviewed snapshot if exact help output is intentionally versioned.

### 3.5 Standard input, environment, and working directory

For an application that reads from `sys.stdin`, patch it with `monkeypatch`:

```python
import io
import sys

def read_name() -> str:
    print("Name?", file=sys.stderr)
    return sys.stdin.readline().strip()

def test_reads_standard_input(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("Ada\n"))

    name = read_name()
    captured = capsys.readouterr()

    assert name == "Ada"
    assert captured.out == ""
    assert captured.err == "Name?\n"
```

For environment variables and working directory, use `monkeypatch` and `tmp_path`:

```python
import os

def read_mode() -> str:
    return os.environ.get("APP_MODE", "development")

def test_environment_and_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_MODE", "test")
    (tmp_path / "config.txt").write_text("enabled", encoding="utf-8")

    assert read_mode() == "test"
    assert (tmp_path / "config.txt").read_text(encoding="utf-8") == "enabled"
```

Pytest restores changes made through `monkeypatch` after the test. It cannot undo external effects such as remote API calls or files written outside the isolated directory. For subprocess tests, pass an explicit `cwd` and `env` because monkeypatching the parent process environment alone does not make the child environment contract obvious.

### 3.6 Testing logging and verbosity

Decide whether the CLI's public contract is the emitted text or a structured logging record. Use `caplog` to assert logging levels/messages when testing logger behavior; use `capsys`/`capfd` to test what users see on the terminal.

```python
import logging

def test_verbose_flag_emits_debug_record(tmp_path, caplog):
    source = tmp_path / "records.json"
    source.write_text("[]", encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger="ledger_cli"):
        code = main([str(source), "--verbose"])

    assert code == 0
    assert any("processing input" in record.message for record in caplog.records)
```

The CLI example defines `--verbose` and emits a debug record through the named logger. `caplog` verifies the logging contract without depending on terminal formatting. For an end-to-end stream contract, test the real process entry point:

```python
import subprocess
import sys

def test_verbose_log_goes_to_stderr(tmp_path, child_env):
    source = tmp_path / "records.json"
    source.write_text("[]", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "ledger_cli", str(source), "--verbose"],
        cwd=tmp_path,
        env=child_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    assert result.returncode == 0
    assert result.stdout == "Records: 0\nTotal: 0\n"
    assert "DEBUG: processing input" in result.stderr
```

Avoid calling `logging.basicConfig(force=True)` in a reusable `main()` function: it can replace pytest's capture handlers and interfere with unrelated tests.

---

## 4. Real subprocess tests: exercise the process boundary

A subprocess test verifies more than `main()`: interpreter startup, argument parsing through the actual entry point, imports, process exit status, standard streams, environment, and filesystem behavior.

For a source-tree test with `cwd=tmp_path`, the child must still be able to import the module. Either install the project into the test environment (preferred for package smoke tests) or explicitly pass the source import path. The helper below is for a simple repository where `ledger_cli.py` lives at the project root; adjust `source_root` to `project_root / "src"` for a `src/` layout. Do not rely on the child accidentally inheriting the repository as its current directory.

```python
import os
from pathlib import Path
import pytest

@pytest.fixture
def child_env():
    project_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    source_root = project_root  # use project_root / "src" for src-layout packages
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(source_root), existing) if part
    )
    env["PYTHONUTF8"] = "1"
    return env
```

For a packaged project, an editable or regular install is preferable to relying on `PYTHONPATH`; use the explicit helper only when intentionally testing the source-tree module.

### 4.1 The safe default pattern

```python
import json
import subprocess
import sys


def test_module_entry_point(tmp_path, child_env):
    source = tmp_path / "records.json"
    source.write_text(json.dumps([{"amount": 10}, {"amount": 5}]), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "ledger_cli", str(source), "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        cwd=tmp_path,
        env=child_env,
    )

    assert result.returncode == 0
    assert result.stdout == '{"count": 2, "total": 15}\n'
    assert result.stderr == ""
```

Important details:
- Pass a **list of arguments**, not a shell command string.
- Use `sys.executable` so the child uses the same Python interpreter/virtual environment as the test process.
- `capture_output=True` captures stdout and stderr separately.
- `text=True` (or `text` with `encoding`) decodes output; explicit UTF-8 avoids relying on the host locale.
- `timeout` bounds a hung process.
- `cwd` makes path resolution deliberate.

This assumes `ledger_cli` is importable in the child interpreter. For an installed package, test the installed package/module. For source-tree execution, make sure the test setup intentionally installs the project or sets `PYTHONPATH`; do not depend on a lucky current directory.

### 4.2 Missing input and parser errors

```python
def test_subprocess_missing_file(tmp_path, child_env):
    missing = tmp_path / "missing.json"
    result = subprocess.run(
        [sys.executable, "-m", "ledger_cli", str(missing)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        cwd=tmp_path,
        env=child_env,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "input file not found" in result.stderr


def test_subprocess_bad_flag(tmp_path, child_env):
    source = tmp_path / "records.json"
    source.write_text("[]", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "ledger_cli", str(source), "--not-an-option"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        cwd=tmp_path,
        env=child_env,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "unrecognized arguments" in result.stderr
```

The expected codes follow the example implementation: missing input is handled as an operational error and returns `1`; an invalid `argparse` option exits `2`. If the application uses a different documented convention, update both implementation and tests together.

### 4.3 `cwd` and `env` are part of the test contract

Do not let subprocess tests accidentally depend on the repository root. Use a temporary working directory and an explicit environment. Preserve only the variables the child actually needs, plus a small set of platform essentials.

```python
import os
import subprocess
import sys


def test_child_environment_is_controlled(tmp_path):
    # Start from the runner environment so Python and Windows retain required
    # platform variables (for example SystemRoot); override only what this test needs.
    env = os.environ.copy()
    env["APP_MODE"] = "test"
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", "import os; print(os.environ['APP_MODE'])"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    assert result.stdout == "test\n"
    assert result.stderr == ""
```

An aggressively minimal environment can break Python startup or platform-specific commands; do not blindly discard `PATH`, required locale settings, or Windows system variables such as `SystemRoot`. The example preserves the runner environment and explicitly controls the variables relevant to this test. If the purpose is to test absence of a particular variable, start from a copy and remove only that key:

```python
env = os.environ.copy()
env.pop("APP_TOKEN", None)
```

Never pass production secrets to test subprocesses unless absolutely necessary; use fake credentials and redact logs.

### 4.4 Feed standard input through a pipe

```python
def test_cli_reads_stdin(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; data = sys.stdin.read(); print(data.upper(), end='')"],
        input="hello\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert result.stdout == "HELLO\n"
    assert result.stderr == ""
```

For binary input, pass bytes and leave `text=False`. Avoid manually opening a pipe and forgetting to close it; `subprocess.run(input=...)` handles the common one-shot case. For a long-running interactive process that requires incremental reads and writes, use `Popen` and manage pipes carefully or use a pseudo-terminal tool.

### 4.5 `subprocess.run` versus `Popen`

Use `subprocess.run` for bounded, one-shot commands. Use `subprocess.Popen` only when the test must interact while the process is running, stream output, send signals, or control lifecycle. With `Popen`, always arrange for:
- A timeout or explicit deadline.
- Pipe draining (otherwise a child can block when its output pipe fills).
- Process termination and `wait()`/`communicate()` in cleanup.
- Cleanup of child processes if the command spawns grandchildren.
- Preservation of stdout/stderr evidence on failure.

A common safe shape:

```python
import subprocess
import sys

def test_long_running_child_stops():
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate(timeout=3)
        assert proc.returncode is not None
    finally:
        if proc.poll() is None:
            try:
                proc.kill()
            except ProcessLookupError:
                pass  # It exited between poll() and kill().
        if proc.poll() is None:
            proc.communicate(timeout=3)
```

The immediate termination here is a lifecycle smoke test, not a timing-sensitive assertion about how quickly a particular OS handles signals. A test that needs to verify graceful shutdown should use a child that announces readiness and handles a shutdown request, then assert a documented result and bounded exit.

### 4.6 Signals and interruption

On POSIX, `Popen.send_signal(signal.SIGTERM)` or `.terminate()` can request termination; `.kill()` is forceful. `SIGINT` often corresponds to Ctrl+C. Python's `KeyboardInterrupt` and shell exit conventions mean the observed status depends on how the application handles interruption.

Test signal behavior only where supported, and mark platform-specific expectations accordingly. A portable test should not assume Windows and POSIX report signals identically. Prefer testing the CLI's own graceful-shutdown function in-process, plus a small POSIX-only integration test if signal behavior is part of the product contract.

If a CLI handles `KeyboardInterrupt` and returns `130`, test that explicit code path separately. A real child killed by SIGINT may instead appear as a negative return code on POSIX depending on how it is launched; do not assert `130` universally for every subprocess signal test.

---

## 5. Testing installed scripts and package entry points

A module test does not prove that the package is installed correctly. Build/install smoke tests should verify the user-facing command in an environment that resembles deployment.

### 5.1 Editable install during development

For a project using `uv`, a common local workflow is:

```bash
uv sync --dev
uv run pytest
uv run ledger-cli --help
```

This assumes the project's `pyproject.toml` declares the `ledger-cli` entry point and the package has been installed into the managed environment. If the executable is missing, inspect package discovery, the `[project.scripts]` mapping, and the active environment rather than changing the test's current directory to hide the issue.

### 5.2 Test the installed console script

A test can locate the generated command with `shutil.which`, but only if the test environment actually installed the package and exposes its script directory on `PATH`. The following test is intended to run in that installed-package environment (not in an arbitrary uninstalled source checkout):

```python
import shutil
import subprocess


def test_installed_console_script_help():
    executable = shutil.which("ledger-cli")
    assert executable is not None, "ledger-cli is not installed in this test environment"

    result = subprocess.run(
        [executable, "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert result.stderr == ""
```

This test is appropriate in an installed-package job, not necessarily every unit-test invocation. It must fail clearly if the script was not installed; silently skipping it can let packaging regressions go unnoticed.

If `--verbose` is part of the installed command's contract, test the console-script path too (not only `python -m`):

```python
import shutil
import subprocess


def test_installed_console_script_verbose(tmp_path):
    executable = shutil.which("ledger-cli")
    assert executable is not None, "ledger-cli is not installed in this test environment"
    source = tmp_path / "records.json"
    source.write_text("[]", encoding="utf-8")

    result = subprocess.run(
        [executable, str(source), "--verbose"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )

    assert result.returncode == 0
    assert result.stdout == "Records: 0\nTotal: 0\n"
    assert "DEBUG: processing input" in result.stderr
```

This assumes the installed entry point maps to `ledger_cli:cli`, as shown above. The test must run in an environment where the project has actually been installed.

### 5.3 Test `python -m package`

If the intended public interface is `python -m ledger_cli`, test exactly that form using `sys.executable -m ledger_cli`. If the package is `ledger`, test `sys.executable -m ledger`. Do not substitute `python path/to/cli.py` unless direct-file execution is itself a supported contract; relative imports may behave differently.

### 5.4 Fake executables on `PATH`

If the CLI invokes a helper such as `gzip`, `git`, or a vendor command, tests should not accidentally invoke the developer's real executable. Create a tiny stub executable in a temporary directory and put that directory first on the child `PATH`.

On POSIX, a stub can be a script with a shebang and executable permission. This example exercises actual `PATH` lookup and is intentionally POSIX-specific:

```python
import os
import subprocess
import sys
import pytest

@pytest.mark.skipif(os.name == "nt", reason="POSIX shebang executable fixture")
def test_path_uses_fake_helper(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    marker = tmp_path / "called.txt"
    helper = bin_dir / "fake-helper"
    helper.write_text(
        "#!/usr/bin/env python3\n"
        "import os, pathlib, sys\n"
        "pathlib.Path(os.environ['HELPER_MARKER']).write_text('\\n'.join(sys.argv[1:]), encoding='utf-8')\n"
        "print('fake helper ran')\n",
        encoding="utf-8",
    )
    helper.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    env["HELPER_MARKER"] = str(marker)

    result = subprocess.run(
        ["fake-helper", "argument with spaces", "second"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )

    assert result.returncode == 0
    assert result.stdout == "fake helper ran\n"
    assert marker.read_text(encoding="utf-8").splitlines() == ["argument with spaces", "second"]
```

On Windows, executable resolution differs (`.exe`, `.bat`, and `PATHEXT`); use a platform-appropriate executable fixture or test a wrapper that invokes a Python stub through `sys.executable`. Do not assume `/bin/sh` exists on Windows. For the most portable unit tests, inject the helper path or mock the command invocation; reserve real `PATH` resolution for platform-specific integration tests.

---

## 6. Click and Typer awareness

Click and Typer provide CLI-oriented testing helpers. Their `CliRunner` can invoke a command in-process, capture output, inspect exit status, and simulate isolated filesystem behavior. This is useful for fast command-contract tests, but it does not replace a subprocess smoke test for installed entry points or OS-level behavior.

Example Click pattern:

```python
from click.testing import CliRunner

def test_click_command_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
```

Here `cli` must be the actual Click command object defined by the application. `result.output` combines output according to Click's testing API, so if the contract distinguishes stdout and stderr, check the version's result fields and write a targeted test. `CliRunner` may alter process-global state while isolating filesystem operations; avoid invoking it concurrently from multiple threads unless the framework explicitly supports that use.

Typer uses Click underneath and has compatible testing patterns. Keep business logic separate from command decorators so it can be tested without a CLI framework.

---

## 7. Machine-readable contracts and automation

### 7.1 stdout versus stderr

A useful convention:
- stdout: the successful result, suitable for piping or parsing.
- stderr: diagnostics, warnings, progress, and logging.
- exit code: whether the operation succeeded.

A command that prints “Done!” to stdout before JSON output can corrupt a downstream parser. Tests should assert that `--json` emits valid JSON only on stdout and that diagnostics stay on stderr.

```python
import json
import subprocess
import sys

def test_json_output_is_parseable(tmp_path, child_env):
    source = tmp_path / "input.json"
    source.write_text('[{"amount": 3}]', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "ledger_cli", str(source), "--json"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        env=child_env,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload == {"count": 1, "total": 3}
    assert result.stderr == ""
```

Prefer parsing machine-readable output and asserting fields over brittle string comparisons when whitespace/key order is not part of the contract. If exact formatting is part of the API, test that separately.

### 7.2 Idempotency

For a command that rewrites a deterministic output file, run it twice and compare the results. Use a fresh `tmp_path` and make the expected idempotency contract explicit.

```python
import subprocess
import sys

def test_cli_output_is_deterministic_across_runs(tmp_path, child_env):
    source = tmp_path / "input.json"
    output = tmp_path / "output.json"
    source.write_text('[{"amount": 8}]', encoding="utf-8")

    command = [sys.executable, "-m", "ledger_cli", str(source), "--json"]
    first = subprocess.run(command, cwd=tmp_path, env=child_env, capture_output=True,
                           text=True, encoding="utf-8", timeout=10)
    second = subprocess.run(command, cwd=tmp_path, env=child_env, capture_output=True,
                            text=True, encoding="utf-8", timeout=10)

    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    assert first.stderr == second.stderr == ""
```

This subprocess example verifies deterministic output across runs; it does not by itself prove file-writing idempotency. For file-writing behavior, test the export operation twice against the same output path and assert that the final content and intended side effects are stable. Do not require byte-identical output if the contract intentionally includes timestamps or generated IDs; inject or normalize those values.

### 7.3 Dry-run behavior

A `--dry-run` contract should make no persistent changes. This small, runnable example tests the behavior at the file-operation boundary; a real CLI test should additionally invoke the command and verify its exit code and plan output.

```python
from pathlib import Path

def export_text(source: Path, output: Path, *, dry_run: bool = False) -> str:
    payload = source.read_text(encoding="utf-8")
    if dry_run:
        return f"Would write {len(payload)} characters to {output}"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")
    return f"Wrote {output}"

def test_dry_run_does_not_create_output(tmp_path):
    source = tmp_path / "input.txt"
    output = tmp_path / "nested" / "out.txt"
    source.write_text("records\n", encoding="utf-8")

    message = export_text(source, output, dry_run=True)

    assert message == f"Would write 8 characters to {output}"
    assert not output.exists()

def test_real_export_is_idempotent(tmp_path):
    source = tmp_path / "input.txt"
    output = tmp_path / "nested" / "out.txt"
    source.write_text("records\n", encoding="utf-8")

    first_message = export_text(source, output)
    first_bytes = output.read_bytes()
    second_message = export_text(source, output)

    assert first_message == second_message == f"Wrote {output}"
    assert output.read_bytes() == first_bytes == b"records\n"
```

Dry-run should not mutate databases, send messages, or call external write APIs either; inject those boundaries and assert they were not invoked.

---

## 8. Interactive programs and pseudo-terminals

For simple prompts, patch `sys.stdin` with `io.StringIO` in-process. For real terminal behavior—password prompts, terminal echo, line buffering, colors, interactive confirmations, and signal behavior—a pipe is not equivalent to a terminal.

A **pseudo-terminal (PTY)** provides a terminal-like pair of endpoints. On Unix-like systems, Python's `pty` module can be used; `pexpect` provides a higher-level expect/send API. These tools are platform-specific or have platform-specific constraints, so keep PTY tests in a dedicated integration layer.

Use PTY tests when the program's behavior depends on `isatty()`, terminal echo, or interactive prompt sequencing. Do not use a PTY for ordinary argument parsing or file input. For `getpass`, prefer an appropriate test double for unit-level logic and use a PTY only if verifying the actual terminal prompt is essential.

A robust interactive test should:
1. Start the process with a bounded timeout.
2. Wait for a specific prompt rather than sleeping.
3. Send the expected response.
4. Assert the visible result and exit status.
5. Terminate the process and collect output in cleanup if the interaction stalls.

Do not print real secrets into test logs, and avoid tests that rely on terminal color or exact cursor-control sequences unless those are the explicit contract.

---

## 9. Cross-platform correctness

### 9.1 Paths and quoting

Pass arguments as a list so Python handles argument boundaries. Avoid building a shell string with interpolated paths. A path containing spaces should be one argument:

```python
import subprocess
import sys

def test_path_with_spaces_is_one_argument(tmp_path, child_env):
    source = tmp_path / "records with spaces.json"
    source.write_text("[]", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "ledger_cli", str(source), "--json"],
        cwd=tmp_path,
        env=child_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    assert result.returncode == 0
    assert result.stdout == '{"count": 0, "total": 0}\n'
    assert result.stderr == ""
```

On Windows, executable resolution, path separators, environment variable names, signal behavior, and script extensions differ from POSIX. `pathlib.Path` avoids many manual separator mistakes. Do not assert raw absolute paths if a relative or normalized path assertion suffices.

### 9.2 Encoding and line endings

Use UTF-8 explicitly for test files and subprocess text decoding when UTF-8 is the CLI contract. Consider setting `PYTHONUTF8=1` in the test child environment if the application promises UTF-8 behavior independent of locale. `PYTHONIOENCODING` can also control Python standard-stream encoding in the child, but it is not a substitute for specifying file encodings in application code.

Text-mode output may translate newline conventions by platform. Prefer semantic assertions or normalized line endings unless exact bytes are part of the contract. When testing binary output, use `text=False` and compare bytes.

### 9.3 Platform-specific tests

Use `pytest.mark.skipif` or a platform marker when a behavior genuinely only exists on one platform (for example, POSIX signal return codes or PTY behavior). Keep the portable contract tested everywhere, and add a focused platform-specific test where necessary. Do not mark a whole CLI suite platform-specific just because one signal test is not portable.

---

## 10. Failure injection and edge conditions

Happy-path tests are necessary but not sufficient. CLI users need predictable failure behavior.

### 10.1 Permissions

Permission tests can behave differently when run as an administrator/root user, on Windows, or on filesystems that ignore POSIX permission bits. A read-only mode bit may not reliably produce a write failure in privileged CI. Prefer testing error handling with an injected filesystem abstraction or monkeypatched operation for unit tests, then add a platform-appropriate integration test where the environment can enforce the permission.

```python
import sys
from pathlib import Path

def safe_write(path: Path, text: str) -> int:
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        print(f"exporter: cannot write output: {exc}", file=sys.stderr)
        return 1
    return 0

def test_write_error_is_reported(monkeypatch, capsys, tmp_path):
    def fail_write(self, data, *args, **kwargs):
        raise PermissionError("permission denied")

    monkeypatch.setattr(Path, "write_text", fail_write)
    code = safe_write(tmp_path / "out.txt", "data")
    captured = capsys.readouterr()

    assert code == 1
    assert captured.out == ""
    assert captured.err == "exporter: cannot write output: permission denied\n"
```

This deterministic unit test verifies the error-handling contract without depending on administrator privileges or filesystem-specific permission semantics. An integration test may additionally use a restricted directory where the runner can enforce permissions.

### 10.2 Disk-full and huge inputs

A true disk-full test can be dangerous or impossible on a shared CI worker. Use a fake writer that raises `OSError` to test cleanup and diagnostics, and a dedicated constrained filesystem/container only for a controlled integration test. For large inputs, generate data in `tmp_path` or stream it incrementally; do not commit a multi-gigabyte fixture. Test boundary sizes and memory behavior with coarse resource constraints in a dedicated job.

### 10.3 Broken pipes

A command may receive `BrokenPipeError` when a downstream consumer exits early, such as `cli | head -n 1`. Test the internal error-handling function deterministically, then add a POSIX subprocess integration case only if pipeline behavior is part of the CLI contract.

```python
def emit_lines(stream, lines: list[str]) -> int:
    try:
        for line in lines:
            print(line, file=stream)
    except BrokenPipeError:
        # This application deliberately treats an early-closed downstream pipe
        # as a successful early stop. Another CLI may document a nonzero status.
        return 0
    return 0

class ClosedPipe:
    def write(self, text: str) -> int:
        raise BrokenPipeError("pipe closed")

    def flush(self) -> None:
        raise BrokenPipeError("pipe closed")

def test_emit_lines_handles_closed_pipe():
    assert emit_lines(ClosedPipe(), ["first"]) == 0
```

For the real subprocess case, prefer Python pipes over a shell pipeline when possible. Example strategy:
1. Start the CLI with `stdout=subprocess.PIPE`.
2. Arrange for the parent to close the read end before the child finishes writing.
3. Ensure the child gets a chance to write enough data to observe the broken pipe.
4. Bound the process lifetime and collect stderr/status.
5. Assert the documented contract—quiet exit or a diagnostic—rather than assuming every OS maps it to the same status.

This case is inherently scheduling-sensitive if implemented by racing a large writer against an immediately closed pipe. Keep it as a focused integration test and use a controlled writer/handshake when possible. A unit test can deterministically exercise a function that catches `BrokenPipeError` by providing a stream whose `write()` raises that exception.

### 10.4 Exit code `130`, cancellation, and long-running jobs

A command should clean up temporary outputs and leave durable checkpoints consistent when interrupted. Do not assume every OS or process-launch method reports Ctrl+C as `130`; test the CLI's explicit interruption handler separately, then add platform-specific signal tests where supported.

For a long-running process, use `Popen`, wait for a readiness message/event, send a graceful stop request, then use a bounded wait and forceful cleanup only as a last resort. Always collect output. Avoid `sleep()` as a readiness signal.

### 10.5 Checkpointing, resume, and partial output cleanup

For a small deterministic example, store the committed output as one JSON state file and replace it atomically after each record. The same-file state avoids the inconsistent two-file ordering problem that occurs when output and checkpoint are updated independently. This is an illustrative local-file pattern, not a substitute for a database transaction or a durable distributed checkpoint protocol.

```python
import json
import os
import tempfile
from pathlib import Path
import pytest


def atomic_json_write(path: Path, value: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)  # same directory/filesystem
    finally:
        temporary.unlink(missing_ok=True)


def process_with_resume(records: list[str], state_path: Path, *, fail_after: int | None = None) -> list[str]:
    completed = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else []
    if completed != records[:len(completed)]:
        raise ValueError("checkpoint does not match the input prefix")
    for record in records[len(completed):]:
        completed.append(record)
        atomic_json_write(state_path, completed)
        if fail_after is not None and len(completed) == fail_after:
            raise RuntimeError("injected failure after checkpoint")
    return completed


def test_resume_matches_clean_run(tmp_path):
    records = ["a", "b", "c", "d"]
    state = tmp_path / "state.json"
    with pytest.raises(RuntimeError, match="injected failure"):
        process_with_resume(records, state, fail_after=2)

    resumed = process_with_resume(records, state)
    assert resumed == records
    assert json.loads(state.read_text(encoding="utf-8")) == records
    assert not list(tmp_path.glob(".state.json.*"))
```

The test injects a failure after a known committed record count, resumes in a second call, and verifies that the final state matches the clean run without duplicates. The temporary file is removed in `finally`, including when serialization or replacement fails. On filesystems with unusual durability semantics, stronger crash guarantees may require syncing the containing directory after `os.replace`; test the actual storage contract.

For batch CLIs:
- Write intermediate results to a temporary path and atomically replace the final output where the filesystem supports it.
- Store checkpoints only after a unit of work is durably complete.
- Make resume semantics explicit: whether already completed records are skipped, verified, or recomputed.
- On failure, remove temporary artifacts or preserve them intentionally with a clear recovery contract.
- Test interruption after a controlled checkpoint, then resume in a second invocation and compare with a clean full run.

Use failure injection at a known record/step, not a timing guess. Verify no duplicate records and no corrupted final output. If output files must be atomic, note that atomic rename guarantees and semantics vary by filesystem and across volumes; keep the temporary file in the same target filesystem.

### 10.6 Coarse performance guards

A CLI smoke test may assert that a small input completes within a generous timeout to catch accidental infinite loops or severe regressions. Do not use a tight wall-clock threshold in ordinary unit tests; CI hardware and load vary. Use dedicated benchmark jobs for performance analysis, and keep timeouts as hang guards rather than precise performance claims.

---

## 11. Coverage for subprocess-launched code

Coverage in the parent pytest process does not automatically include every child Python process. To measure subprocess-launched Python code, configure `coverage.py` for subprocess data collection and ensure child processes use the same environment/configuration. With modern coverage.py, use the documented subprocess/parallel-data configuration for the installed version; older examples may use `COVERAGE_PROCESS_START` with a `.coveragerc` file and a startup hook.

A typical pytest coverage run for in-process code is:

```bash
coverage run -m pytest
coverage report -m
coverage html
```

For coverage.py versions that support subprocess patching (coverage.py 7.10+), configure it in `.coveragerc`:

```ini
[run]
branch = True
patch = subprocess
parallel = True
source = ledger_cli
```

Then run the tests under `coverage run -m pytest` and combine parallel data files after the run:

```bash
coverage combine
coverage report -m
```

Check the installed coverage.py version and its documentation before using `patch = subprocess`; older versions may need the documented `COVERAGE_PROCESS_START` startup-hook approach. Do not assume `pytest --cov` alone measures an arbitrary child interpreter. Validate the setup with a line executed only in the child and confirm that it appears in the report. Keep configuration under version control so local and CI behavior match.

---

## 12. The CLI test pyramid

Use the cheapest test level that can verify the contract.

1. **Many in-process unit tests:** argument-to-function behavior, validation, output formatting helpers, business logic, failure handling with fakes.
2. **A smaller number of subprocess tests:** real `python -m` invocation, streams, exit codes, stdin, working directory, environment, and process lifecycle.
3. **A small installed-package smoke layer:** build/install artifact, console script, package imports, and entry-point metadata.
4. **A few specialized integration tests:** PTY interactions, signals, actual filesystem permissions, broken pipes, and controlled external services.

This pyramid is a guide, not a quota. Keep each layer focused. A subprocess test should exist because process-boundary behavior matters, not because every unit test is easier to write as a subprocess. Conversely, in-process tests alone cannot prove packaging or process behavior.

---

## 13. Common mistakes and corrections

### Mistake 1: Test only the happy path

**Problem:** invalid flags, missing files, parser errors, and I/O failures can break automation.

**Correction:** assert success and failure exit codes, stdout/stderr separation, and no unintended side effects.

### Mistake 2: Use `os.system`, `shell=True`, or interpolated shell strings by default

**Problem:** quoting differs across platforms, paths with spaces break, and untrusted input can become shell injection.

**Correction:** use `subprocess.run([executable, arg1, arg2], ...)`. Use a shell only when shell syntax itself is the behavior under test, and then keep commands static and inputs controlled.

### Mistake 3: Rely on the current working directory

**Problem:** tests pass from the repository root but fail from an installed package or another directory.

**Correction:** pass `cwd=tmp_path` for isolation, use absolute input/output paths where appropriate, and deliberately test the supported invocation mode.

### Mistake 4: Forget the timeout

**Problem:** a hung child can stall CI indefinitely.

**Correction:** set a reasonable timeout for `run()` and manage `Popen` lifecycle with bounded waits and cleanup.

### Mistake 5: Assert every character of help output

**Problem:** harmless formatting changes break tests.

**Correction:** assert stable public essentials, or use a reviewed snapshot only if exact output is a compatibility requirement.

### Mistake 6: Assume all status codes are universal

**Problem:** `argparse`, uncaught exceptions, signal termination, and shell conventions differ.

**Correction:** document your CLI's status table and test it on supported platforms. Distinguish the application's status from the shell's representation of signal termination.

### Mistake 7: Assume parent monkeypatches configure the child

**Problem:** a subprocess has its own environment and process state.

**Correction:** pass an explicit `env`, `cwd`, input, and arguments to the child. Patch the child executable or inject a fake where needed.

### Mistake 8: Test a console script only by importing `main`

**Problem:** broken package metadata or launcher generation goes unnoticed.

**Correction:** add an installed-package smoke test that invokes the generated command in the environment where it was installed.

### Mistake 9: Use real services for every failure case

**Problem:** tests become slow, costly, and dependent on credentials and network availability.

**Correction:** use fakes for deterministic failure paths and reserve a small integration layer for real protocol behavior.

### Mistake 10: Ignore partial output after failure

**Problem:** restart can duplicate or corrupt results.

**Correction:** inject failures at known checkpoints and assert the documented cleanup/resume contract.

---

## 14. Hands-on exercises

### Exercise 1 — testable entry point

Refactor a script that parses `sys.argv` and calls `sys.exit()` at module top level into:
- `build_parser()`,
- a core function with no printing,
- `main(argv: list[str] | None = None) -> int`,
- a guarded `__main__` entry point.

Write tests for success, missing input, and malformed arguments. State the expected exit codes and output streams.

### Exercise 2 — four required CLI contracts

Write tests for:
1. `--help` exits `0`.
2. A missing file exits with the documented operational error code.
3. An invalid flag exits `2` under `argparse`.
4. A successful run exits `0`, emits the expected result on stdout, and leaves stderr empty.

Include both an in-process test and at least one subprocess test. Explain which contract cannot be verified by calling `main()` alone.

### Exercise 3 — subprocess with controlled cwd and environment

Run a module using `sys.executable`, `cwd=tmp_path`, `env=...`, `capture_output=True`, and a timeout. Demonstrate that the test still works when launched from a different repository directory. Do not modify the parent's global environment.

### Exercise 4 — standard input and pipe behavior

Test a command that reads from stdin. Then write a deterministic unit test for a stream writer that raises `BrokenPipeError`. If the CLI promises POSIX pipeline behavior, add a platform-specific integration test and document its limits.

### Exercise 5 — dry run and idempotency

Create a file-export CLI. Assert that `--dry-run` does not create or alter the output. Run the normal command twice and verify the documented idempotency behavior. Ensure generated timestamps/IDs do not make the test nondeterministic.

### Exercise 6 — fake executable on `PATH`

Create a stub helper executable that records its arguments to a file. Configure the CLI subprocess environment so the stub is selected before any real helper. Assert argument boundaries, exit code, and captured output. Document how the fixture differs on Windows and POSIX.

### Exercise 7 — interrupted long-running job

Design a worker with a deterministic checkpoint. Inject a failure or stop request after a known batch, then restart it. Assert that the final output matches a clean run and no duplicate records remain. Avoid arbitrary sleeps.

### Exercise 8 — installed-package smoke test

Build/install the project in an isolated environment, invoke its generated console script with `--help`, and verify the entry-point target and package imports. Ensure the test fails clearly if the script is missing.

---

## 15. Self-check with model answers

### 1. Why is `main(argv)` easier to test than code at module top level?

It accepts explicit arguments rather than reading `sys.argv` implicitly, returns an exit code instead of terminating the process, and avoids running the CLI on import. Tests can call it repeatedly with different inputs and capture output. A guarded `__main__` entry point preserves real process behavior while keeping imports safe.

### 2. How do you test `--help`, a missing file, a bad flag (exit code 2), and a successful run?

- `--help`: in-process, assert `SystemExit.code == 0`, usage text on stdout, and no stderr; also optionally invoke the real module in a subprocess.
- Missing file: assert the documented operational code (the example returns `1`), empty stdout, and a stable diagnostic on stderr.
- Bad flag: with `argparse`, assert `SystemExit.code == 2`, empty stdout, and parser diagnostics on stderr.
- Successful run: assert return code `0`, the result on stdout, empty stderr, and expected filesystem effects.
- Subprocess smoke tests should use argument lists, `sys.executable`, explicit `cwd`/`env`, captured output, and a timeout.

### 3. How do you test behavior when stdout is a closed pipe?

At unit level, pass a controlled stream whose `write()` raises `BrokenPipeError` to the function responsible for output and assert the intended handling. For process-level behavior, launch the CLI with a pipe, close the parent's read end deliberately, bound the process lifetime, and collect its status/stderr. Keep OS-specific expectations isolated; do not assume every platform reports a broken pipe identically. A shell pipeline such as `cli | head -n 1` can be a useful manual reproduction but is less portable as a unit test.

### 4. Why use argument lists instead of shell strings?

Argument lists preserve argument boundaries, avoid platform-specific quoting rules, and reduce shell-injection risk. `shell=True` should be reserved for cases where shell parsing is specifically part of the behavior being tested.

### 5. Why use a subprocess test if `main()` is already covered?

The subprocess test verifies interpreter startup, import paths, the `__main__` guard, actual process exit status, stream behavior, environment and working-directory assumptions. An installed console-script test additionally verifies packaging metadata and launcher generation.

---

## 16. Completion checklist

- [ ] I can structure a CLI with `main(argv)` and a proper entry point.
- [ ] I test success, usage errors, operational errors, exit codes, stdout, and stderr.
- [ ] I use `capsys`, `capfd`, and `pytest.raises(SystemExit)` intentionally.
- [ ] I use `tmp_path`, `monkeypatch`, stdin fixtures, and explicit cwd/environment.
- [ ] I invoke subprocesses with argument lists, `sys.executable`, captured output, and timeouts.
- [ ] I test the intended module, installed console script, and package entry point.
- [ ] I understand status codes `0`, `1`, `2`, and interruption conventions such as `130`.
- [ ] I can test input pipes, long-running processes, and platform-specific signal behavior safely.
- [ ] I know when Click/Typer helpers and PTYs are appropriate.
- [ ] I test `--help`, `--version`, logging, verbosity, dry-run, and idempotency.
- [ ] I can isolate fake executables on `PATH` and avoid accidentally invoking real tools.
- [ ] I understand subprocess coverage configuration and verify that child code is measured.
- [ ] I account for path, quoting, encoding, line-ending, permission, disk, and broken-pipe differences.
- [ ] I test checkpoint/resume and partial-output cleanup through deterministic failure injection.
- [ ] I use a CLI test pyramid: many in-process tests, fewer subprocess tests, and a small installed-package layer.

**Next lesson:** `07-testing-time-randomness-and-concurrency.md`.
