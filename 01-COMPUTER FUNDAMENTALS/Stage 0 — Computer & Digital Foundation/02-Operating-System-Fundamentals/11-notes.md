# Concept 11 — Standard Input / Output (I/O)

**Module:** Stage 0 → Module 0.2 — Operating System Fundamentals

---

## 1. What is Input and Output?

- **Input:** Information a program receives, such as keyboard data, file contents, or data from another program.
- **Output:** Information a program sends outward, such as results, logs, or error messages.
- **Computation:** The actual work performed by the program, such as calculations or running an AI model.

Together, these are called **I/O** (Input/Output).

---

## 2. Why Standard Streams Exist

Unix/Linux provides three conventional communication channels so programs can receive input and produce output consistently. This allows different programs to work together without needing custom communication mechanisms.

---

## 3. stdin, stdout and stderr

| Stream | File descriptor | Purpose |
|---|---|---|
| `stdin` | 0 | Receives input |
| `stdout` | 1 | Produces normal results |
| `stderr` | 2 | Produces warnings, errors and diagnostics |

**Important:** `stdin` does not always mean keyboard, and `stdout` does not always mean screen. Their actual destinations depend on how the process is started.

---

## 4. File Descriptors

A **file descriptor (FD)** is a small integer that a process uses to identify an open I/O resource.

A descriptor can refer to:

- A terminal
- A regular file
- A pipe
- A network socket

Each process has its own file descriptor table. It normally starts with descriptors 0, 1, and 2, but can open additional descriptors.

---

## 5. Terminal and Standard I/O

In an interactive terminal:

- Keyboard → terminal → stdin → process.
- Process → stdout → terminal → screen.
- Process → stderr → terminal → screen.

However, stdin, stdout and stderr can instead connect to files, pipes or other resources.

---

## 6. stdout vs stderr

- **stdout:** Actual program results.
- **stderr:** Diagnostic messages, warnings, progress updates and errors.

Keeping them separate allows automation to consume clean results while operators inspect diagnostic information independently.

---

## 7. Standard I/O and System Calls

Python uses higher-level interfaces, but I/O ultimately involves kernel-mediated operations:

- **`open`:** Opens a file and returns a descriptor.
- **`read`:** Retrieves data.
- **`write`:** Sends data.
- **`close`:** Releases a descriptor.

---

## 8–10. Standard I/O in Python

- `input()` reads from `sys.stdin`.
- `print()` writes to `sys.stdout` by default.
- `print(..., file=sys.stderr)` writes to stderr.

`input()` displays its prompt without a newline, reads one line and removes its trailing newline.

---

## 11–12. Shell Redirection

| Command | Meaning |
|---|---|
| `>` | Redirect stdout; overwrite file |
| `>>` | Redirect stdout; append |
| `<` | Read stdin from a file |
| `2>` | Redirect stderr; overwrite |
| `2>>` | Redirect stderr; append |
| `2>&1` | Redirect stderr to stdout's current destination |

The shell configures descriptors before starting the process. The program's code remains unchanged, even when its output goes to a file instead of the terminal.

---

## 13–16. Related Process Concepts

- **Pipes:** Connect Process A's stdout to Process B's stdin.
- **Process lifecycle:** Standard streams are normally established before execution, inherited or configured by the parent, and closed when the process exits.
- **Exit code:** A separate final status value. A process can print results but still fail.
- **Environment variables:** Configure process behaviour; standard streams carry data and diagnostics.
- **Signals:** Control or notify processes; standard I/O communicates content.

---

## 17–18. Practical Labs and PowerShell

The Linux/Ubuntu/WSL2 lab demonstrates inspecting descriptors through `/proc/self/fd`, redirecting streams, reading piped input, separating Python output and inspecting a disposable process. It uses a temporary directory and requires no `sudo`.

PowerShell has a different, object-oriented pipeline and stream model. Its behaviour should not be assumed identical to Unix file descriptors.

---

## 19–21. AI Engineering, Debugging and Misconceptions

Standard I/O is important for AI scripts, inference jobs, batch processing, workers, subprocesses and service logs.

Common problems include:

- Programs waiting because stdin has no data.
- Output appearing in an unexpected stream or file.
- Errors missing because only stdout was redirected.
- Accidentally overwriting files with `>`.
- `EOFError` when redirected input runs out.
- Subprocesses behaving differently when streams are captured.

Always inspect the actual streams, redirection command and exit code before diagnosing a failure.

---

## 22–26. Mini-Project, Exercises and Production

The Python mini-project reads numbers from stdin, calculates count, sum and average, writes results to stdout, and sends invalid-input warnings to stderr.

Its exit codes are:

- `0`: All input valid.
- `1`: No valid numbers.
- `2`: Valid numbers found, but invalid lines were skipped.

The lesson includes 37 exercises, review questions, interview/architecture questions and production applications. Production concerns include buffering, excessive diagnostic output, accidental sensitive-data logging, hung processes and observability.

---

## 27–29. Roadmap and Final Mental Model

The lesson builds on kernel, system calls, processes, filesystems, permissions, environment variables and signals.

It deliberately excludes advanced asynchronous I/O, TTY/PTY internals, buffering internals, advanced descriptor operations, sockets and advanced subprocess internals.

Remember the central concept:

- FD 0 → input.
- FD 1 → normal output.
- FD 2 → diagnostics.

Their destinations can change without changing the program's code. This is the foundation of redirection, pipes and production logging.
