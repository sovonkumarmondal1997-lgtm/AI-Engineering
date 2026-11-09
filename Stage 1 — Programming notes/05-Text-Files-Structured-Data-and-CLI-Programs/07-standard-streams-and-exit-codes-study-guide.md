# 07 — Standard Streams and Exit Codes
## Complete Lesson Summary, Stage 1 Roadmap Review, Exercises, Debugging, and Revision

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 05 — Text Files, Structured Data, and CLI Programs  
**Lesson:** 07 — Standard Streams and Exit Codes

---

# Part A — Complete lesson summary

## 1. What is a stream?

A **stream** is a channel through which data flows over time. A program can read or write a piece at a time without knowing the total size in advance.

- **Input:** data flowing into a program.
- **Output:** data flowing out.
- A file can be connected to a stream, but a stream is not necessarily a file. It can be connected to a keyboard, terminal, pipe, or another process.
- A string is already a complete in-memory value; a stream is a channel that can be consumed incrementally.
- A stream can carry decoded text (`str`) or raw bytes (`bytes`).

Streaming is valuable because a program can start processing before all input arrives and can process gigabytes without loading everything into memory.

## 2. The three standard streams

Every normal command-line process conventionally starts with three streams:

| Stream | Direction | Python object | Typical purpose |
|---|---|---|---|
| stdin (standard input) | into program | `sys.stdin` | Input data |
| stdout (standard output) | out of program | `sys.stdout` | Intended result |
| stderr (standard error) | out of program | `sys.stderr` | Diagnostics, warnings, errors |

They are not inherently the keyboard or screen. Their actual destinations depend on how the shell or parent process launches the program. They may be connected to a terminal, file, pipe, or another resource.

On Unix/Linux/macOS, the conventional file descriptors are:
- `0` → stdin
- `1` → stdout
- `2` → stderr

These numbers are a POSIX convention. Windows uses handles internally, but Python exposes the same portable `sys.stdin`, `sys.stdout`, and `sys.stderr` interface.

A **process** is a running instance of a program. The operating system establishes the process's standard input/output channels before the Python application code starts.

## 3. Python's stream objects

```python
import sys

print(type(sys.stdin))
print(type(sys.stdout))
print(type(sys.stderr))
```

They are normally text-mode file-like objects, similar to objects returned by `open(..., "r")` or `open(..., "w")`.

Useful methods:

| Method/property | Meaning |
|---|---|
| `read(size=-1)` | Read up to `size` characters, or all remaining input |
| `readline()` | Read one line; newline is included when present; `""` at EOF |
| `readlines()` | Read all remaining lines into a list |
| `write(text)` | Write exactly the supplied string; returns character count |
| `writelines(lines)` | Write strings consecutively; adds no newlines |
| `flush()` | Push buffered output onward now |
| `isatty()` | Check whether this stream is connected to a terminal |
| `fileno()` | Get the underlying OS descriptor, if available |
| `readable()` / `writable()` / `seekable()` | Check supported operations |
| `.buffer` | Underlying binary stream, normally available on standard streams |

stdin is normally readable; stdout/stderr normally writable; standard streams are usually not seekable. Actual capabilities can vary with redirection or replacement objects, so check rather than assume.

`print()` is a convenient wrapper around stdout. It adds a newline by default, supports multiple values and separators, and can target another stream:

```python
print("hello")                    # writes hello plus newline to stdout
sys.stdout.write("hello\n")       # writes exactly the supplied string
print("a", "b", "c", sep=",")     # a,b,c
print("progress", end="")         # no trailing newline
```

`write()` does not add a newline. `writelines()` also does not add separators or newlines.

## 4. Reading stdin and EOF

Common input approaches:

```python
name = input("Name: ")             # one line, newline stripped
line = sys.stdin.readline()        # one line; newline retained if present
all_lines = sys.stdin.readlines()  # all remaining lines as list
all_text = sys.stdin.read()        # all remaining input as one string

for line in sys.stdin:             # stream line by line
    process(line.rstrip("\n"))
```

Choose:
- `input()` for a simple interactive prompt.
- `readline()` for one line with explicit EOF handling.
- `read()` when the whole input is one logical document and is known to be manageable.
- `readlines()` only when all lines are needed in memory and input is small.
- `for line in sys.stdin` for line-oriented input of any size.

**EOF** means End Of File, but it is a condition of a stream, not necessarily a physical disk file. It means no more data is available and none is coming.
- Redirected file: EOF occurs after the file is consumed.
- Pipe: EOF occurs when the producer closes its output.
- Interactive terminal: the user must signal EOF. In Bash on Linux/WSL2, Ctrl+D at the start of a line is the common convention.

`read()` and `readlines()` wait until EOF. Therefore a script reading all stdin can appear to hang when launched interactively; it is waiting for more input or EOF, not necessarily frozen. Iterating over stdin ends automatically at EOF.

## 5. stdout versus stderr: the most important CLI rule

**stdout contains the program's actual result. stderr contains diagnostics about the program.**

Bad:

```python
print("Loading...")
print("ERROR: invalid input")
print("result data")
```

Good:

```python
import sys

print("result data")                         # stdout
print("Loading...", file=sys.stderr)         # stderr
print("ERROR: invalid input", file=sys.stderr)
```

Both streams may appear on the same terminal screen in an ordinary interactive run, but they remain independently redirectable.

Why this matters: in `program_a | program_b`, a plain pipe connects only `program_a`'s stdout to `program_b`'s stdin. If progress messages or errors are printed to stdout, the next program receives them as if they were data and may fail to parse the input. stderr remains separate unless explicitly redirected.

For JSON/CSV pipelines, stdout must contain only valid machine-readable output. Warnings, progress, and errors go to stderr.

## 6. Shell redirection

The **shell** configures streams before Python starts. Python reads/writes the streams it receives; argparse does not perform redirection.

| Bash syntax | Meaning |
|---|---|
| `command > file` | stdout to file, overwrite |
| `command >> file` | stdout to file, append |
| `command < file` | stdin from file |
| `command 2> file` | stderr to file, overwrite |
| `command 2>> file` | stderr to file, append |
| `command > file 2>&1` | stdout to file, then stderr to same destination |
| `command &> file` | Bash shorthand for both stdout and stderr |

Examples:

```bash
python app.py > output.txt
python app.py 2> errors.txt
python app.py > output.txt 2> errors.txt
python app.py < input.txt
```

`>` means descriptor 1; `2>` means descriptor 2; `<` means descriptor 0. `&>` is Bash-specific, so do not assume every shell supports identical syntax.

## 7. Pipes and pipeline design

A **pipe** connects one process's stdout to another process's stdin without an intermediate file:

```bash
python producer.py | python consumer.py
```

Only stdout is piped by default. The producer's stderr remains connected to its previous destination (often the terminal).

A well-behaved pipeline stage should:
1. Read from stdin when appropriate.
2. Write intended results to stdout.
3. Write diagnostics to stderr.
4. Return a meaningful exit status.

Example multi-stage pipeline:

```bash
cat data.txt | python filter.py | python transform.py | python aggregate.py
```

`cat` is an external utility that writes a file to stdout; it is not a Python feature. Each stage can be developed and tested independently.

## 8. Text and binary streams

By default, standard streams are text streams: reads return `str`, writes expect `str`. Their `.buffer` exposes the underlying binary stream:

```python
data = sys.stdin.buffer.read()       # raw bytes
sys.stdout.buffer.write(data)        # raw bytes
```

Use binary streams for images, compressed files, binary formats, protocols, or exact byte-preserving filters. Do not decode arbitrary binary data as text. For ordinary CSV, JSON, and text CLI work, use the default text streams.

A replacement stream such as `io.StringIO` may not have `.buffer`, so do not assume every file-like object exposes it.

## 9. Buffering and flushing

**Buffering** temporarily collects small writes and sends them onward in batches. This reduces expensive OS-level write operations.

The trade-off is visibility timing:
- stdout connected to an interactive terminal is commonly line-buffered.
- stdout redirected to a file or pipe is commonly block-buffered.
- Therefore output may not appear immediately when redirected.

Use flushing when real-time visibility matters:

```python
print("Starting...", flush=True)
sys.stdout.flush()
```

A short program normally flushes buffered output on normal termination. Do not flush every line without reason: excessive flushing defeats buffering and can reduce throughput.

## 10. TTY and terminal formatting

A **TTY** is a terminal device. `isatty()` checks whether a particular stream is connected to one:

```python
if sys.stdout.isatty():
    print("Interactive terminal")
else:
    print("Redirected or piped output")
```

Check streams independently: stdin may be a terminal while stdout is redirected.

Production uses:
- Show progress bars/spinners only when appropriate for an interactive terminal.
- Emit color only when the destination can render it.
- Avoid interactive prompts when stdin is a pipe/file.
- Prefer plain machine-readable output when another program consumes stdout.

ANSI escape sequences control terminal formatting:

```python
print("\033[31mRed text\033[0m")
```

The terminal interprets these sequences. A file or downstream parser sees the raw escape characters, so do not emit them unconditionally.

## 11. Exit codes and `sys.exit()`

An **exit code/status** is the integer a process reports when it terminates:
- `0` conventionally means success.
- Non-zero conventionally means some failure or abnormal condition.
- There is no universal meaning for every non-zero number; each application should document its own convention.

`sys.exit()` raises `SystemExit`; it does not directly kill the process at the Python-language level:

```python
sys.exit()       # status 0
sys.exit(0)      # success
sys.exit(1)      # generic failure
sys.exit(2)      # argparse convention for usage error
```

It can be caught:

```python
try:
    sys.exit(1)
except SystemExit as exc:
    print(exc.code)   # 1; execution continues because it was caught
```

Do not catch `SystemExit` broadly in normal application code. It is intended to propagate to the interpreter and terminate the process.

A non-integer argument behaves differently:

```python
sys.exit("something went wrong")
```

Python prints the message to stderr and exits with status 1. Prefer explicit output plus a chosen status when the code needs control over both:

```python
print("something went wrong", file=sys.stderr)
sys.exit(3)
```

## 12. The `main() -> int` pattern

Keep process termination at the CLI boundary:

```python
def main() -> int:
    # perform work
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

`main()` is an ordinary testable function returning an integer. Only the script entry point converts that integer into process termination. This lets tests call `main([...])` and inspect its return value without terminating the test runner.

A robust application catches anticipated exceptions, prints a clean message to stderr, and returns a meaningful status:

```python
import sys
from pathlib import Path

def main() -> int:
    try:
        data = Path("input.csv").read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(data)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Catch specific expected exceptions, not every exception indiscriminately. A traceback from an uncaught exception normally results in status 1, but is often unsuitable as a user-facing error.

## 13. Exit codes in shells, automation, and CI/CD

In Bash, `$?` contains the previous command's status:

```bash
python app.py
echo $?
```

Shell conditional operators:
- `command && next_command`: run the next command only if the first succeeds (0).
- `command || recovery_command`: run recovery only if the first fails (non-zero).

Automation cannot safely infer success by reading a printed word such as `"ERROR"`. It checks the process status. A script that prints an error but returns 0 will be treated as successful by systems that rely on exit codes.

A possible application convention (example only):

| Status | Meaning |
|---:|---|
| 0 | Success |
| 2 | Invalid CLI usage |
| 3 | Input/data problem |
| 4 | Configuration problem |
| 5 | External dependency failure |

Keep statuses intentional, documented, and stable. CI tools such as test runners, linters, type checkers, build tools, and deployment commands each have their own documented non-zero meanings; the common convention is 0 for success and non-zero for failure. Whether one failure stops the entire pipeline depends on the shell/CI configuration.

## 14. `argparse` error behavior

`argparse` already uses the standard-stream convention:
- Invalid syntax, missing required argument, unknown option, invalid choice: usage/error to stderr, exit 2.
- `--help` and `--version`: text to stdout, exit 0.
- `parser.error("message")`: usage plus message to stderr, exit 2.

CLI syntax errors are different from domain errors. Argparse validates the command shape; application code validates the actual data, file contents, and business rules.

## 15. Human-readable versus machine-readable output

Human output might be:

```text
Processing 100 files...
Done!
```

Machine output might be:

```json
{"status": "success", "files_processed": 100}
```

For a machine-readable invocation, stdout must contain only the complete result:

```python
import json
import sys

result = {"status": "success", "files_processed": 100}
print(json.dumps(result))  # stdout
print("warning: skipped 2 files", file=sys.stderr)
```

A downstream process can parse stdout as JSON while a human or log collector receives diagnostics separately.

## 16. Streaming large data and backpressure

Loading all input first:

```python
lines = sys.stdin.readlines()
for line in lines:
    process(line)
```

Streaming:

```python
for line in sys.stdin:
    process(line)
```

The first stores the entire input in memory; the second holds only the current line plus application state. Streaming reduces memory and latency: downstream stages can begin before upstream input finishes.

**Backpressure** occurs when a downstream pipe consumer is slower than the producer. OS pipe buffers fill and naturally slow the producer, pacing the pipeline without requiring an unbounded application-level buffer.

For binary data, read fixed-size byte chunks instead of lines when the format is not line-oriented.

## 17. File-or-stdin input and the `"-"` convention

A useful CLI accepts either a named file or stdin:

```python
import sys
from pathlib import Path

def get_input_lines(input_path: str | None):
    if input_path:
        with Path(input_path).open("r", encoding="utf-8") as handle:
            yield from handle
    else:
        yield from sys.stdin
```

The widely used `"-"` convention means stdin for input or stdout for output, but the program must implement it explicitly:

```python
def open_input(path: str):
    if path == "-":
        return sys.stdin
    return Path(path).open("r", encoding="utf-8")
```

Do not close stdin as if your program owned a file it opened.

## 18. Subprocess communication

`subprocess.run()` starts a child process, waits for it, and returns a `CompletedProcess`:

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "--version"],
    capture_output=True,
    text=True,
)
print(result.returncode)
print(result.stdout)
print(result.stderr)
```

Important options:
- `capture_output=True`: capture child's stdout and stderr.
- `text=True`: decode captured bytes to strings.
- `input=`: send data to child's stdin.
- `check=True`: raise `subprocess.CalledProcessError` if the child exits non-zero.

Without `check=True`, a non-zero child status is stored in `.returncode`; it does not automatically raise:

```python
result = subprocess.run(["python", "validate.py", "data.csv"])
if result.returncode != 0:
    print("validation failed", file=sys.stderr)
```

With `check=True`:

```python
try:
    subprocess.run(["python", "validate.py"], check=True)
except subprocess.CalledProcessError as exc:
    print(f"child failed: {exc.returncode}", file=sys.stderr)
```

Use an argument list, not a shell command string. For ordinary run-and-wait jobs, `subprocess.run()` is usually sufficient. `Popen` is for more involved in-progress communication; careless bidirectional pipe handling can deadlock if both sides wait while buffers fill. Parent and child each have independent buffering behavior.

By default, a child inherits the parent's standard streams. `capture_output=True` instead creates pipes back to the parent.

## 19. File descriptors and low-level access

A **file descriptor** is a raw OS-level integer handle to an open resource. Python's `sys.stdout` is a richer object built on top of the underlying resource, adding text encoding, buffering, and file-like methods.

```python
print(sys.stdin.fileno())   # conventionally 0
print(sys.stdout.fileno())  # conventionally 1
print(sys.stderr.fileno())  # conventionally 2
```

Low-level APIs:

```python
import os
data = os.read(0, 1024)      # raw bytes from fd 0
os.write(1, b"hello\n")      # raw bytes to fd 1
```

`os.dup()` duplicates a descriptor. `os.dup2(fd, fd2)` makes `fd2` refer to the same resource as `fd`; shells use this kind of operation to implement redirection. These APIs bypass Python's text/buffering conveniences and are rarely needed in ordinary CLI programs.

## 20. Python-level versus OS-level redirection

Python-level reassignment:

```python
import io
import sys

old = sys.stdout
sys.stdout = io.StringIO()
print("captured")
captured = sys.stdout.getvalue()
sys.stdout = old
```

Safer context-manager form:

```python
import io
from contextlib import redirect_stdout

buffer = io.StringIO()
with redirect_stdout(buffer):
    print("captured")
print(buffer.getvalue())
```

`redirect_stderr()` works the same way. These change Python's stream objects only. They do not redirect raw OS descriptor writes or automatically redirect subprocesses.

The shell's `>` changes the OS-level descriptor before the process starts. It affects the process and inherited child descriptors. Do not confuse these two layers.

## 21. Testing streams and exit status

Use `capsys` for normal Python-level `print()`/`sys.stdout`/`sys.stderr` writes:

```python
def test_cli(capsys):
    status = main(["--input", "data.csv"])
    captured = capsys.readouterr()
    assert status == 0
    assert "result" in captured.out
    assert captured.err == ""
```

Use `capfd` when code writes directly to OS descriptors, uses C extensions, or launches subprocesses. `capsys` captures Python-level streams; `capfd` captures descriptors 1 and 2.

Test the whole CLI contract:
- valid input: expected stdout, usually empty stderr, status 0;
- empty input: documented behavior;
- malformed input: clean stderr, no corrupted stdout, non-zero;
- missing file/permission error: diagnostic and non-zero;
- invalid CLI syntax: argparse stderr and status 2;
- unexpected error: controlled diagnostic and non-zero;
- redirected/piped execution, not just interactive execution.

## 22. Debugging, common mistakes, and good design

Debugging checklist:
1. Record the exact command.
2. Check shell quoting and redirection.
3. Inspect `repr(sys.argv)` when arguments are involved.
4. Inspect stdout and stderr separately by redirecting each to a file.
5. Check whether stdin is waiting for EOF.
6. Check `isatty()` and buffering when output is delayed or formatting is wrong.
7. Check the actual exit status (`echo $?` in Bash).
8. Inspect child `.returncode` or use `check=True`.
9. Reproduce with explicit `argv` and pytest capture.

Common mistakes include:
- Mixing diagnostics into stdout.
- Assuming stdin is always a keyboard or stdout always a screen.
- Calling `read()` and misdiagnosing its wait for EOF as a hang.
- Printing an error but returning 0.
- Returning 1 for every failure without a documented scheme.
- Calling `sys.exit()` deep inside business logic.
- Swallowing all exceptions with `except: pass`.
- Using low-level descriptors unnecessarily.
- Flushing every write or never flushing when real-time output matters.
- Assuming `isatty()` is always true.
- Treating shell syntax as Python/argparse syntax.
- Assuming Python-level redirection affects subprocesses.
- Testing only interactive runs, never pipes/redirection.

Good design keeps `process()` independent of the CLI:

```python
def process():
    raise ValueError("invalid record")

def main() -> int:
    try:
        process()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## 23. Production CLI architecture

Separate three concerns:

1. **CLI layer:** argparse, `main()`, stream I/O, diagnostics, exit-status translation. This is the layer that knows about `sys`.
2. **Domain/application layer:** validation, transformation, calculations. Uses normal return values and exceptions; should not call `sys.exit()`.
3. **I/O layer:** file and external-service operations.

Recommended flow:

```text
parse arguments
    ↓
validate CLI/data inputs
    ↓
build typed configuration
    ↓
run domain logic
    ↓
result → stdout
diagnostics → stderr
    ↓
return status
    ↓
raise SystemExit(main())
```

`print(..., file=sys.stderr)` is adequate for simple diagnostics. The next lesson's `logging` module adds severity levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`), timestamps, configurable formatting, and multiple destinations. This lesson introduces that connection but does not teach logging itself.

## 24. Security, performance, and portability

Security:
- Never print passwords, API keys, or tokens to stdout/stderr; logs and redirected files may persist.
- CLI arguments can be visible in process listings.
- Treat redirected/piped output as potentially persistent.
- Sanitize user-facing errors; do not expose stack traces, internal paths, or connection strings unnecessarily.
- Child processes inherit environment and streams by default; pass only what they need.

Performance:
- Buffering reduces system calls.
- Streaming avoids loading huge inputs into memory.
- Excessive flushing defeats buffering.
- Per-line processing has overhead, but is generally the best simple CLI default.
- Excessive diagnostics can become a throughput and storage bottleneck.
- Tune chunk sizes only when measurements justify it.

Portability:
- Python's `sys` and `subprocess` abstractions are portable.
- fd 0/1/2 and Bash syntax are POSIX conventions.
- Bash uses `$?`; PowerShell uses `$LASTEXITCODE` for native commands; `cmd.exe` uses `%ERRORLEVEL%`.
- Terminal/ANSI behavior differs by environment; test on the platforms you support.

## 25. Real-world and AI engineering applications

The chapter's patterns apply to:
- Data ingestion and CSV validation.
- JSON transformation and ETL stages.
- Log processing and reliability tools.
- ML dataset preprocessing.
- Model evaluation and batch inference.
- Deployment validation and health checks.
- CI/CD and scheduled jobs.
- Agent/tool workflows that invoke a command and need a reliable success/failure signal.

A robust dataset validator can read a file or stdin, stream records, write a machine-readable summary to stdout, warnings to stderr, and return 0/non-zero. An orchestrator or agent can then decide whether to continue, retry, or alert by checking the status instead of parsing a human message.

Containers use the same process model. Container runtimes commonly collect stdout/stderr as logs, and orchestration systems inspect the process exit status. The generic orchestration loop is: run process → capture streams → inspect status → continue/retry/alert.

A process may also be terminated by an external signal (for example Ctrl+C). This differs from a program choosing an exit code. POSIX shells commonly report signal termination as `128 + signal number`, but this is a shell/platform convention, not a universal Python rule.

## 26. API reference coverage

| API | Purpose |
|---|---|
| `sys.stdin`, `sys.stdout`, `sys.stderr` | Standard text streams |
| `sys.exit(status)` / `SystemExit` | Request process termination |
| `read`, `readline`, `readlines` | Read stream data |
| `write`, `writelines` | Write stream data |
| `flush`, `isatty`, `fileno` | Buffering, terminal check, OS descriptor |
| `readable`, `writable`, `seekable` | Inspect stream capabilities |
| `.buffer` | Access binary stream |
| `print(file=, end=, sep=, flush=)` | Control output destination and formatting |
| `redirect_stdout`, `redirect_stderr` | Temporary Python-level redirection |
| `subprocess.run` | Run child process and wait |
| `capture_output`, `text`, `input`, `check` | Configure child communication |
| `CompletedProcess.returncode/stdout/stderr` | Inspect child result |
| `CalledProcessError` | Raised by `check=True` on non-zero |
| `os.read`, `os.write`, `os.dup`, `os.dup2` | Low-level descriptor operations |
| pytest `capsys`, `capfd` | Capture Python streams or OS descriptors |

---

# Part B — Stage 1 roadmap and current-level analysis

## 1. Stage 1 structure

The roadmap defines Stage 1 — **Programming & Computational Thinking** — as 24 modules, 212 numbered lessons, and 282 files. The 24 modules are:

1. Computational Thinking and Program Design.
2. Python Core Language and Data Types.
3. Control Flow, Functions, Scope, and Errors.
4. Problem-Solving, Collections, and Algorithmic Habits.
5. Text Files, Structured Data, and CLI Programs.
6. Modules, Packages, Dependencies, and Code Quality.
7. Testing and Systematic Debugging.
8. Object-Oriented Design, Data Modelling, and Functional Style.
9. Advanced Production-Oriented Python Foundations.
10. Production Habits for Python Programs.
11. Advanced Python Data Model and Object Design.
12. Metaprogramming and Dynamic Python.
13. Standard Library Toolkit.
14. Bytes, Binary Data, and Advanced Text Processing.
15. Modern Python Language Features.
16. Advanced Testing and Test Architecture.
17. Profiling, Memory, and Runtime Performance.
18. Packaging, Distribution, and Publishing.
19. CPython Internals and Runtime Behaviour.
20. Design Patterns and Library API Design.
21. Data Visualization and Notebook Workflows.
22. Secure Python Coding.
23. Code Reading, Refactoring, and Code Review.
24. Functions and OOP Gap Lessons.

The full tree begins with the Stage 1 overview and then modules 01–24. Module 05's sequence is:
1. Reading and Writing Text Files — completed.
2. `pathlib` and Portable Paths — completed.
3. CSV Files — completed.
4. JSON and Serialization — completed.
5. Encodings and Newlines — completed.
6. Command-Line Arguments with `argparse` — completed.
7. **Standard Streams and Exit Codes — current lesson.**
8. Logging versus Print — next.
9. Environment Configuration and Input Validation.
10. Module README and practice questions.

## 2. Four Stage 1 projects

- **Personal Expense Ledger CLI:** command-line expense tracking and reporting.
- **Log Investigation and Reliability CLI:** stream and inspect operational logs.
- **Data Quality and Transformation Pipeline:** `orders.csv`, `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, configuration, and a data contract.
- **Rule-Based Risk Review Engine:** `transactions.csv`, `rules.toml`, `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden decision data.

## 3. Current learning level and scope

Your recorded level is **beginner progressing toward intermediate**. You have completed/covered:
- Python fundamentals, variables, strings, lists, tuples, dictionaries, sets, conversion, mutability.
- Conditionals, loops, functions, parameters, return values, defaults, docstrings.
- Scope/global state, pure functions/side effects, exceptions and validation.
- Collection processing, algorithmic habits, Big-O, parsing and regex.
- Text files, `pathlib`, CSV, JSON, encodings/newlines, and `argparse`.

This lesson is the natural next step after argparse. It uses familiar functions, `Path`, JSON/CSV, exceptions, `main(argv)`, and basic pytest capture patterns. The solutions below stay within these topics and the current Module 05 scope. The source lesson introduces subprocesses and `capfd`; these are explained only to the depth required by this lesson, not expanded into a full subprocess or advanced testing course.

The most relevant projects are the Log Investigation CLI, Data Quality Pipeline, and Risk Review Engine: each needs clean machine-readable output, separate diagnostics, reliable status codes, and streaming behavior.

---

# Part C — All 15 coding exercises solved

Each solution includes a command, expected behavior, and the main code lines.

## Level 1 — Beginner

### 1. Write stdout and stderr separately

```python
# hello.py
print("hello")

# warning.py
import sys
print("warning", file=sys.stderr)
```

Run `python hello.py > out.txt`; `out.txt` contains `hello`. Run `python warning.py 2> err.txt`; `err.txt` contains `warning`. Both exit 0. `print()` defaults to stdout; `file=sys.stderr` selects stderr.

### 2. Read one line and echo it

```python
name = input()
print(name)
```

Run `python echo.py`, type `Sovon`, press Enter. stdout: `Sovon`; stderr empty; exit 0. `input()` reads one line from stdin and strips its newline; `print()` writes the value plus a newline.

### 3. Read all stdin and count characters

```python
import sys
text = sys.stdin.read()
print(len(text))
```

Run `python count.py < input.txt`. stdout is the number of characters; stderr empty; exit 0. `read()` waits until EOF. Interactive test: type text, then signal EOF (Ctrl+D at the start of a line in Bash/WSL2).

### 4. Detect a terminal

```python
import sys
if sys.stdout.isatty():
    print("terminal")
else:
    print("redirected")
```

Run `python tty.py`: normally stdout is `terminal`. Run `python tty.py > out.txt`: `out.txt` contains `redirected`. stderr empty; exit 0. `isatty()` checks the current stdout connection, not whether a human is definitely watching.

### 5. Return success or failure

```python
import sys
def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "fail":
        print("failed", file=sys.stderr)
        return 1
    print("success")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `python status.py`: stdout `success`, status 0. Run `python status.py fail`: stderr `failed`, status 1. `main()` returns a normal integer; `SystemExit` converts it into the process status.

## Level 2 — Intermediate

### 6. Stream stdin and count lines

```python
import sys
def main() -> int:
    count = sum(1 for _ in sys.stdin)
    print(count)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `cat data.txt | python linecount.py`. stdout is the line count; stderr empty; exit 0. The generator expression counts each line as it arrives and does not store the whole file.

### 7. Optional file path, otherwise stdin

```python
import argparse
import sys
from pathlib import Path

def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    args = parser.parse_args(argv)

    if args.path is None:
        handle = sys.stdin
        for line in handle:
            print(line, end="")
    else:
        with args.path.open(encoding="utf-8") as handle:
            for line in handle:
                print(line, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `python copy.py data.txt` or `cat data.txt | python copy.py`. stdout reproduces input; stderr empty; exit 0. `nargs="?"` makes the path optional. Do not close stdin; the `with` block is used only for a file opened by this program.

### 8. Separate result and diagnostic

```python
import sys
print("42")
print("warning: one row skipped", file=sys.stderr)
```

Run `python report.py > result.txt 2> warnings.txt`. `result.txt` contains only `42`; `warnings.txt` contains the warning; exit 0. Run `python report.py 2>/dev/null` to suppress diagnostics, or `python report.py >/dev/null` to suppress the result. The two streams are independently redirectable.

### 9. Three distinct failure statuses

```python
import sys
from pathlib import Path

def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("error: missing path", file=sys.stderr)
        return 2
    path = Path(args[0])
    if not path.exists():
        print("error: file not found", file=sys.stderr)
        return 3
    if not path.is_file():
        print("error: path is not a file", file=sys.stderr)
        return 4
    print(path.read_text(encoding="utf-8"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run with no argument → stderr message, status 2. Run with missing path → status 3. Run with a directory → status 4. Run with a file → file text on stdout, status 0. The status values are this CLI's documented convention, not universal meanings.

### 10. `main(argv)` with three pytest tests

```python
import sys

def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("error: missing value", file=sys.stderr)
        return 2
    print(args[0].upper())
    return 0
```

```python
def test_success(capsys):
    assert main(["hello"]) == 0
    captured = capsys.readouterr()
    assert captured.out == "HELLO\n"
    assert captured.err == ""

def test_missing(capsys):
    assert main([]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "missing value" in captured.err

def test_multiple_values_uses_first(capsys):
    assert main(["one", "two"]) == 0
    assert capsys.readouterr().out == "ONE\n"
```

Run `pytest -q`. `main(argv)` accepts a supplied list, so tests do not modify global `sys.argv`. `capsys` captures Python-level output. The tests independently verify result, diagnostic, and exit status.

## Level 3 — Advanced

### 11. Pipe-safe JSON Lines transformation

```python
import json
import sys

def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        record = json.loads(line)
        record["processed"] = True
        print(json.dumps(record))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `cat input.jsonl | python transform.py | python transform.py`. Each input JSON object is parsed, marked, and emitted as one JSON line. stdout contains only JSON; stderr is empty on valid input; exit 0. For malformed input, a production version should catch `JSONDecodeError`, write a line-numbered diagnostic to stderr, and return a non-zero status rather than emitting a traceback.

### 12. Capture child return code, stdout, and stderr

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-c",
     "import sys; print('child output'); print('child warning', file=sys.stderr); sys.exit(3)"],
    capture_output=True,
    text=True,
)
print(result.returncode)
print(result.stdout, end="")
print(result.stderr, end="", file=sys.stderr)
```

Run `python parent.py`. Parent stdout: `3` then `child output`; parent stderr: `child warning`; parent exit 0. `capture_output=True` captures both child streams; `text=True` returns strings; `.returncode` contains 3. The parent chooses its own status.

### 13. Use `check=True` and map child failure

```python
import subprocess
import sys

def main() -> int:
    try:
        subprocess.run(
            [sys.executable, "-c", "raise SystemExit(7)"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"child failed with {exc.returncode}", file=sys.stderr)
        return 5
    print("child succeeded")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `python parent.py`. stderr: `child failed with 7`; stdout empty; parent exit 5. `check=True` raises `CalledProcessError`; `exc.returncode` retains the child's status. The parent maps it to its own documented status 5.

### 14. Use `capfd` for subprocess output

```python
import subprocess
import sys

def test_child_output(capfd):
    subprocess.run(
        [sys.executable, "-c",
         "import sys; print('child out'); print('child err', file=sys.stderr)"]
    )
    captured = capfd.readouterr()
    assert "child out" in captured.out
    assert "child err" in captured.err
```

Run `pytest -q`. `capfd` captures OS file descriptors 1 and 2, including subprocess output. `capsys` alone captures Python-level `sys.stdout`/`sys.stderr` and may not capture child-process writes.

### 15. Verify pipe safety

Use this implementation:

```python
import sys

def main() -> int:
    for line in sys.stdin:
        cleaned = line.strip()
        if cleaned:
            print(cleaned.upper())
    print("processed input", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run interactively with typed lines, then EOF; also run `printf 'a\nb\n' | python safe.py > out.txt 2> err.txt`. In the redirected test, `out.txt` contains `A` and `B`, `err.txt` contains `processed input`, status is 0. Pipe safety means: no prompt is required, input is streamed, stdout contains only transformed records, diagnostics use stderr, and status reflects success. Also test empty input and a downstream parser.

---

# Part D — All 8 debugging exercises

1. **Diagnostics contaminate stdout:** keep only `result: 42` on stdout; send `Loading...` and error details to `print(..., file=sys.stderr)`. This protects downstream parsers.
2. **Output appears late:** redirected stdout is commonly block-buffered. Use `print("starting...", end="", flush=True)` when immediate visibility is required.
3. **Failure returns 0:** the error branch must `return 1` (or another documented non-zero status). Printing an error does not change the process status.
4. **Swallowed exception:** replace bare `except: pass` with a specific expected exception handler, report to stderr, and return/raise a failure status. Do not hide unexpected bugs.
5. **stdin appears to hang:** `sys.stdin.read()` waits for EOF. Redirect a file, pipe input, or type data and signal EOF.
6. **Child failure ignored:** inspect `result.returncode`, or use `check=True` and catch `CalledProcessError`; do not print success unconditionally.
7. **Test cannot inspect subprocess output:** use `capture_output=True, text=True` and assert on the returned object, or use pytest `capfd` to capture descriptor-level output. `capsys` alone is insufficient for many subprocess writes.
8. **`sys.exit()` inside validation helper:** return `True`/`False` or raise a normal domain exception. Let `main()` decide whether to continue, count failures, print diagnostics, and choose the final status.

---

# Part E — Interview questions with answers

1. **What is stdin?** The process's standard input channel; it may be connected to a terminal, file, or pipe.
2. **What is stdout?** The standard output channel; it should contain the intended result only.
3. **What is stderr?** The standard diagnostic channel for warnings, progress, and errors.
4. **Why separate stdout and stderr?** So downstream tools can consume result data without parsing diagnostics.
5. **What is a pipe?** An OS communication channel connecting one process's stdout to another's stdin.
6. **What is an exit code?** The integer status a process reports when it terminates.
7. **Why is 0 success?** It is the widely adopted convention, allowing automation to distinguish success from non-zero outcomes.
8. **What does `sys.exit()` do?** Raises `SystemExit` with the requested status.
9. **What is `SystemExit`?** The exception the interpreter recognizes as a process-termination request.
10. **Why `main() -> int`?** It keeps work testable and centralizes process termination at the entry point.
11. **Why stderr for diagnostics?** Diagnostics should not contaminate data being piped or parsed.
12. **What is a file descriptor?** A low-level OS integer handle for an open I/O resource.
13. **What are fd 0, 1, 2?** Conventionally stdin, stdout, stderr on POSIX systems.
14. **What does `isatty()` check?** Whether that stream is connected to a terminal device.
15. **What is buffering?** Temporarily collecting writes to reduce expensive output operations.
16. **Why output timing changes under pipes?** The stream may switch from line buffering to block buffering.
17. **Python vs OS redirection?** Python redirection changes stream objects inside one process; shell redirection changes OS descriptors before process startup and affects inherited descriptors.
18. **`capsys` vs `capfd`?** `capsys` captures Python-level writes; `capfd` captures OS descriptor writes, including many subprocess/C-level writes.
19. **How does `subprocess.run()` expose child results?** Through `CompletedProcess.returncode`, and captured `.stdout`/`.stderr`.
20. **Why does CI use exit codes?** They are structured signals; CI should not parse arbitrary human-readable text to infer success.
21. **How make a CLI pipe-safe?** Read stdin, write only results to stdout, diagnostics to stderr, and return meaningful status.
22. **How process huge input?** Stream line by line or in fixed-size binary chunks.
23. **Why keep JSON stdout clean?** Extra text makes the output invalid or unparseable JSON.
24. **How report an error to human and automation?** Clear stderr diagnostic plus a documented non-zero exit code.
25. **What happens when a child exits non-zero?** `subprocess.run()` returns the status for inspection; with `check=True`, it raises `CalledProcessError`.

---

# Part F — Architecture questions with answers

1. **Support file and stdin:** accept an optional path; open it if present, otherwise iterate over `sys.stdin`. Do not close stdin.
2. **Compose into pipelines:** stream records in, emit only transformed records to stdout, diagnostics to stderr, and return a meaningful status.
3. **Protect JSON output:** reserve stdout for the JSON document/JSONL records; put all warnings and progress on stderr; test stdout independently.
4. **How does CI determine success?** It inspects the process exit status; 0 passes and non-zero indicates failure, subject to runner configuration.
5. **Test all CLI outputs:** call `main(argv)`, capture with `capsys` or `capfd`, and assert stdout, stderr, and status independently.
6. **Process huge input:** iterate stdin one record at a time, or read fixed-size chunks for binary data.
7. **Subprocess pipeline:** invoke each stage with `subprocess.run`, inspect `.returncode` or use `check=True`, and capture streams when diagnostics must be attributed to a stage.
8. **Expose errors:** human-readable stderr plus a specific documented non-zero status.
9. **Streams in containers:** same process streams; runtimes commonly collect stdout/stderr as logs and use exit status to determine task success.
10. **Production data validator:** support file/stdin, stream records, emit clean JSON output, report per-record issues on stderr, define stable exit codes, and test success, partial failure, and total failure.

---

# Part G — Knowledge check answers

1. `sys.stdin.readline()` at EOF returns `""`.
2. stderr is conventionally descriptor `2`.
3. `subprocess.run(..., check=True)` raises `CalledProcessError` for non-zero child status.
4. False: `print()` writes to stdout, not necessarily a physical screen.
5. True: a plain pipe connects stdout to the next process's stdin; stderr remains separate.
6. True: `sys.exit()` raises catchable `SystemExit`.
7. False: `capsys` and `capfd` capture at different layers.
8. stdout carries results; stderr carries diagnostics so pipelines remain parseable.
9. `isatty()` checks whether the stream is connected to a terminal device.
10. `"a"` goes to stdout; `"b"` goes to stderr.
11. `sys.exit("oops")` prints `oops` to stderr and exits 1.
12. Most likely it is waiting for stdin EOF; redirected input reaches EOF automatically.
13. A helper should not terminate the entire process; return a result or raise a normal exception and let `main()` choose the process status.

---

# Part H — End-to-end mini-project: Streaming Data Quality CLI

## 1. Requirements

Build `dq_check.py` that:
- Accepts an optional JSONL file path; if omitted, reads stdin.
- Reads one JSON record per line, streaming rather than loading all records.
- Ignores blank lines and does not count them.
- Passes valid records through unchanged to stdout.
- Sends malformed or schema-invalid record messages to stderr and continues.
- Returns 0 if all records pass, or 3 if any record fails.
- Supports `--json-summary`, which emits only a final JSON summary on stdout instead of passing records through.
- Uses `main(argv) -> int` and is testable.

## 2. Complete implementation

```python
import argparse
import json
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

_MALFORMED = object()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate JSON Lines input record by record."
    )
    parser.add_argument("path", nargs="?", default=None)
    parser.add_argument("--json-summary", action="store_true")
    return parser


def open_input(path: str | None):
    if path is None:
        return sys.stdin
    return Path(path).open("r", encoding="utf-8")


def validate_record(record: object) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    errors = []
    if "id" not in record:
        errors.append("missing 'id'")
    if "value" not in record:
        errors.append("missing 'value'")
    return errors


def iter_records(handle) -> Iterator[tuple[int, object, str]]:
    for line_number, raw_line in enumerate(handle, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError:
            yield line_number, _MALFORMED, raw_line
        else:
            yield line_number, record, raw_line


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handle = open_input(args.path)
    total = 0
    failed = 0

    try:
        for line_number, record, raw_line in iter_records(handle):
            total += 1

            if record is _MALFORMED:
                print(f"line {line_number}: not valid JSON", file=sys.stderr)
                failed += 1
                continue

            errors = validate_record(record)
            if errors:
                print(
                    f"line {line_number}: {'; '.join(errors)}",
                    file=sys.stderr,
                )
                failed += 1
                continue

            if not args.json_summary:
                sys.stdout.write(raw_line)
    finally:
        if handle is not sys.stdin:
            handle.close()

    if args.json_summary:
        print(json.dumps({"total": total, "failed": failed}))

    return 0 if failed == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

## 3. Line-by-line design explanation

- `_MALFORMED = object()` creates a unique sentinel. JSON `null` becomes Python `None`, so `None` cannot safely mean malformed JSON.
- `build_parser()` declares an optional path and boolean summary flag.
- `open_input()` returns stdin when no path is supplied; otherwise it opens a UTF-8 text file.
- `validate_record()` checks that the parsed JSON value is a dictionary and that both required keys exist. It returns error strings instead of printing or exiting.
- `iter_records()` enumerates physical line numbers, skips blank lines, parses one line at a time, and yields the line number, parsed value/sentinel, and original text.
- `main()` parses arguments, opens input, and tracks total/failed records.
- Malformed JSON and schema-invalid JSON each generate stderr diagnostics, increment failures, and continue.
- Valid records are written as their original text to stdout unless summary mode is enabled.
- `finally` closes only a file opened by the program; it does not close process-owned stdin.
- Summary mode prints exactly one JSON object to stdout.
- The return value is 0 for no failures and 3 if any record failed.
- The entry point converts the returned status to a process exit.

## 4. Example

Input:

```json
{"id": 1, "value": "a"}
{"id": 2}
not json at all
{"id": 3, "value": "c"}
```

Run:

```bash
python dq_check.py data.jsonl
```

stdout:

```json
{"id": 1, "value": "a"}
{"id": 3, "value": "c"}
```

stderr:

```text
line 2: missing 'value'
line 3: not valid JSON
```

Exit status: `3`.

With summary:

```bash
python dq_check.py data.jsonl --json-summary
```

stdout:

```json
{"total": 4, "failed": 2}
```

The two record warnings still go to stderr; exit status remains 3.

Pipeline:

```bash
cat data.jsonl | python dq_check.py 2> problems.log | python next_stage.py
```

Only valid records reach the next stage. In Bash, `$?` normally reports the last pipeline command's status. Use `set -o pipefail` to make the pipeline return a non-zero status if an earlier stage failed, or inspect `${PIPESTATUS[1]}` immediately to obtain the validator's individual status.

## 5. Tests

```python
import json

def test_validate_record():
    assert validate_record({}) == ["missing 'id'", "missing 'value'"]
    assert validate_record({"id": 1, "value": "x"}) == []


def test_valid_record_passes(tmp_path, capsys):
    path = tmp_path / "data.jsonl"
    path.write_text('{"id": 1, "value": "a"}\n', encoding="utf-8")
    status = main([str(path)])
    captured = capsys.readouterr()
    assert status == 0
    assert json.loads(captured.out) == {"id": 1, "value": "a"}
    assert captured.err == ""


def test_invalid_record_goes_to_stderr(tmp_path, capsys):
    path = tmp_path / "data.jsonl"
    path.write_text('{"id": 1}\n', encoding="utf-8")
    status = main([str(path)])
    captured = capsys.readouterr()
    assert status == 3
    assert captured.out == ""
    assert "missing 'value'" in captured.err


def test_summary_mode(tmp_path, capsys):
    path = tmp_path / "data.jsonl"
    path.write_text('{"id": 1, "value": "a"}\n{"id": 2}\n', encoding="utf-8")
    status = main([str(path), "--json-summary"])
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"total": 2, "failed": 1}
    assert status == 3


def test_null_is_schema_error_not_json_syntax_error(tmp_path, capsys):
    path = tmp_path / "data.jsonl"
    path.write_text("null\nnot json\n", encoding="utf-8")
    status = main([str(path)])
    captured = capsys.readouterr()
    assert status == 3
    assert "record must be a JSON object" in captured.err
    assert "not valid JSON" in captured.err


def test_valid_lines_are_passed_through_unchanged(tmp_path, capsys):
    original = '  {"id": 1,  "value": "a"}  \n{"id": 2, "value": "b"}'
    path = tmp_path / "data.jsonl"
    path.write_text(original, encoding="utf-8")
    main([str(path)])
    assert capsys.readouterr().out == original
```

**Important technical detail:** “unchanged” here means the original text line is written back, not re-serialized JSON. Text-mode universal-newline translation may normalize physical line endings, so it is not a byte-for-byte guarantee. For exact byte preservation, the implementation would need binary streams and byte-level parsing/handling.

**Production hardening not required by this lesson:** catch file-opening/reading `OSError` at the CLI boundary and return a documented I/O status; consider `--fail-fast`; document exit codes in help; and test flag interactions. Do not put `sys.exit()` into `validate_record()`.

---

# Part I — Revision and mastery checklist

- [ ] Explain streams without equating them to files or terminals.
- [ ] Distinguish stdin, stdout, and stderr.
- [ ] Know the POSIX fd 0/1/2 convention.
- [ ] Read stdin using `input`, `readline`, `read`, and iteration.
- [ ] Explain EOF and why `read()` may wait.
- [ ] Write results to stdout and diagnostics to stderr.
- [ ] Use shell redirection and pipes correctly.
- [ ] Distinguish text and binary standard streams.
- [ ] Explain buffering and use flushing deliberately.
- [ ] Use `isatty()` before terminal-specific output.
- [ ] Explain exit codes and `SystemExit`.
- [ ] Use `main() -> int` and `raise SystemExit(main())`.
- [ ] Distinguish argparse syntax errors from domain/data errors.
- [ ] Design stable application-specific exit codes.
- [ ] Use `subprocess.run()` and inspect child output/status.
- [ ] Distinguish Python-level and OS-level redirection.
- [ ] Know when to use pytest `capsys` versus `capfd`.
- [ ] Stream large input rather than loading it all into memory.
- [ ] Keep domain logic independent of CLI termination.
- [ ] Test redirected and piped runs, not just terminal runs.
- [ ] Protect secrets and sanitize diagnostics.
- [ ] Explain how containers and orchestrators use streams and statuses.

**Next roadmap lesson:** `08-logging-versus-print.md`. Do not advance until you can build and test a small CLI that reads from stdin or a file, writes clean results to stdout, sends diagnostics to stderr, and returns the correct status.
