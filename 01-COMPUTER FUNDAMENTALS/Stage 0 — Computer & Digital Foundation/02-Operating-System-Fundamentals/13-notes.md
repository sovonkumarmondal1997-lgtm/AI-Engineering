# Concept 13 — Shell

**Stage 0 · Module 0.2 — Operating System Fundamentals**

A **shell** is a user-space program that accepts commands, understands what they mean, prepares their input/output, launches programs, and reports their results. It acts as the communication layer between you and the operating system.

---

## 1. Shell, Terminal and Kernel

These are different components:

- **Terminal:** The text-based interface for input and output.
- **Terminal emulator:** A graphical application, such as Windows Terminal, that provides a terminal experience.
- **Shell:** Interprets commands. Examples: Bash and PowerShell.
- **Kernel:** The privileged core of the OS that manages processes, filesystems, hardware and other resources.

The shell is an ordinary program. It asks the kernel to perform operations through system calls.

---

## 2. Bash and PowerShell

- **Bash:** Common on Linux; pipelines transfer text/byte streams between commands.
- **PowerShell:** Common on Windows; pipelines primarily transfer structured .NET objects.

Their pipeline mechanisms are fundamentally different.

---

## 3. How Command Execution Works

When you type `python app.py`:

1. Terminal receives your input.
2. Shell reads and parses the command.
3. Shell locates Python using `PATH`.
4. Prepares the process environment.
5. Configures stdin, stdout and stderr.
6. Launches the program.
7. OS creates and runs the process.
8. Program executes and exits.
9. Shell reports the result and exit code.

---

## 4. Commands and Arguments

Commands can be:

- **Executable:** Separate program that creates a process.
- **Builtin:** Implemented inside the shell.
- **Function:** Named sequence of shell commands.
- **Alias:** Shorthand for another command.

`cd` must be a builtin because it changes the shell's own working directory. An external program would only change its own directory.

**Arguments** provide values; **options** change command behaviour, such as `ls -l`.

---

## 5. PATH and Working Directory

- `PATH` contains directories searched for executable programs, in order.
- `command -v python3` identifies the executable selected.
- The first matching executable generally wins.
- The current working directory determines where relative paths are resolved.

`python app.py` depends on the current directory; `python /absolute/path/app.py` does not.

---

## 6. Quoting and Expansion

The shell transforms commands before programs receive their arguments.

- `"hello world"` and `'hello world'` preserve the phrase as one argument.
- `hello\ world` escapes the space.
- `*.txt` expands into matching filenames.
- `$(pwd)` executes `pwd` and substitutes its captured output.

Glob expansion matches filenames; regex matches text patterns.

---

## 7. Variables and I/O

- `NAME="Alice"` creates a shell variable.
- `export APP_ENV=development` makes the variable available to subsequently launched child processes.

The shell prepares file descriptors before launching programs.

| Operator | Purpose |
|---|---|
| `>` | Overwrite output file |
| `>>` | Append output |
| `<` | Read input from file |
| `2>` | Redirect stderr |
| `2>&1` | Redirect stderr to stdout's current destination |

Redirections are processed left to right, so their order matters.

---

## 8. Pipelines and Exit Codes

`A | B` connects A's stdout to B's stdin. The shell creates and configures these connections. Stderr does not automatically enter the pipeline.

- `$?` gives the latest command's exit status.
- `0` conventionally means success; non-zero indicates failure or another condition.
- Bash's `PIPESTATUS` reports individual pipeline-stage statuses.
- Without `pipefail`, pipeline `$?` normally reflects only the last stage.

---

## 9. Background Jobs and Signals

- **Foreground:** Shell waits for the command to finish.
- **Background:** `command &` returns control immediately.
- `jobs`: Lists tracked jobs.
- `fg`: Brings a job into the foreground.
- `bg`: Resumes a stopped job in the background.

Ctrl+C sends `SIGINT` to the foreground process group. Ctrl+Z sends `SIGTSTP` to request a stop. `kill` can signal a process by PID.

The shell itself is also a process, with its own PID (`echo $$`).

---

## 10. Shell Scripting

A **shell script** is a file containing commands executed together.

- **Shebang:** `#!/usr/bin/env bash` identifies the interpreter.
- `chmod +x script.sh` grants execute permission.
- `./script.sh` executes the file directly.
- `bash script.sh` asks Bash to read the script; execute permission is not required, only read permission.

Exit code `126` conventionally means found but not executable; `127` means command not found.

---

## 11. Practical Work and Production Relevance

The lesson includes 11 Linux/Ubuntu/WSL2 labs covering shell identification, builtins, PATH, directories, quoting, redirection, pipelines, exit codes, background jobs, and scripts.

It also includes 17 debugging scenarios, 18 common misconceptions, 37 exercises, review questions, and interview/architecture questions.

The mini-project builds a two-stage Python pipeline:

- Producer generates values.
- Processor validates and doubles them.
- Environment variable `THRESHOLD` controls filtering.
- stdout contains results; stderr contains diagnostics.
- Exit codes report processing outcomes.

An important lesson: setting `THRESHOLD=8` before only the producer does not configure the processor. Exporting the variable makes it available to both stages.

Shell skills support Python services, AI batch inference, evaluation pipelines, data processing, deployment commands, debugging, logging and automation.

**Final mental model:** The terminal presents input/output; the shell interprets commands and prepares execution; the kernel performs the actual OS operations.

**Next concept:** Concept 14 — Process Lifecycle. Advanced Bash internals, process-group internals, advanced scripting, shell security and PowerShell scripting are outside this lesson's scope.
