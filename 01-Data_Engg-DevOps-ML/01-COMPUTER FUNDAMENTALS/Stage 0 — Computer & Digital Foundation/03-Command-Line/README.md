# Module 0.3 — Command Line

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.3 — "Command
Line"

This README is a **roadmap and navigation document only**. It defines what this module covers, in
what order, and why — it does not contain the lessons themselves. Lesson content is written later,
inside each numbered concept file, during the actual teaching phase.

---

## 1. Module purpose

Module 0.3 builds practical, hands-on fluency with the command line — turning the OS concepts from
[`../02-Operating-System-Fundamentals/`](../02-Operating-System-Fundamentals/README.md) (processes,
filesystems, permissions, standard streams) into everyday, muscle-memory skills. This module is
heavily hands-on: most of the learning happens by running commands, not reading about them.

Every later project in the roadmap — Python scripts, backend services, database work, model
training, and agent tooling — is started, inspected, and debugged from a terminal. Without this
module, basic tasks like finding a file, reading a log, or checking why a script failed become slow
and error-prone.

## 2. Prerequisites

Module 0.2 — Operating System Fundamentals, specifically filesystems, permissions, standard
streams, and the shell. A computer running Linux, Ubuntu, or WSL2 (Windows Subsystem for Linux) is
required for hands-on practice, alongside familiarity with Windows PowerShell for cross-platform
comparison.

## 3. Learning objectives

By the end of Module 0.3, the learner should be able to:

- Navigate the filesystem confidently using absolute and relative paths, and always know their
  current directory before changing anything.
- Create, copy, move, and delete files and directories safely — inspecting before any destructive
  command, and never running a recursive delete without naming the exact target.
- View and inspect file contents without opening an editor, including large files.
- Search file contents and the filesystem itself for specific text or files.
- Filter, count, and transform text output using small, composable tools.
- Chain commands together with pipes, and redirect output and errors to files independently.
- Read and set environment variables from the shell.
- Write a small, repeatable shell script instead of retyping the same commands.
- Read, understand, and change file permissions, and explain what each permission bit controls.
- Recognize the same workflow in both Bash (Linux/WSL2/Git Bash) and PowerShell, without confusing
  their commands or path conventions.

## 4. Learning sequence

Work through the numbered concept files in order. Navigation and file operations come first because
every other command-line skill assumes you can already move around and inspect the filesystem
safely.

| # | File | Concept(s) covered |
|---|---|---|
| 1 | [`01-navigation.md`](./01-navigation.md) | navigation (`pwd`, `ls`, `cd`) |
| 2 | [`02-file-operations.md`](./02-file-operations.md) | file operations (`cp`, `mv`, `rm`, `mkdir`) |
| 3 | [`03-viewing-files.md`](./03-viewing-files.md) | viewing files (`cat`, `less`, `head`, `tail`) |
| 4 | [`04-searching.md`](./04-searching.md) | searching (`grep`, `find`) |
| 5 | [`05-text-processing.md`](./05-text-processing.md) | text processing (`sort`, `uniq`, `cut`, `xargs`) |
| 6 | [`06-pipes-and-redirection.md`](./06-pipes-and-redirection.md) | pipes and redirection (`\|`, `>`, `>>`, `2>`) |
| 7 | [`07-environment-variables.md`](./07-environment-variables.md) | environment variables |
| 8 | [`08-shell-scripts.md`](./08-shell-scripts.md) | shell scripts |
| 9 | [`09-permissions.md`](./09-permissions.md) | permissions (`chmod`, ownership) |
| 10 | [`10-command-line-tools-overview.md`](./10-command-line-tools-overview.md) | command-line tools overview (Bash, Git Bash, WSL2, PowerShell) |
| 11 | [`11-safe-terminal-and-filesystem-literacy.md`](./11-safe-terminal-and-filesystem-literacy.md) | safe terminal and filesystem literacy (paths, permissions, symlinks, safe deletion) |
| 12 | [`12-shell-quoting-and-standard-streams.md`](./12-shell-quoting-and-standard-streams.md) | shell quoting and standard streams (`stdin`, `stdout`, `stderr`) |

## 5. Why this module matters for AI engineering

The command line is how every later AI and backend system is actually operated day to day.
Concretely:

- **Safe navigation and file operations** are the habit that prevents a wrong-directory mistake
  from deleting or overwriting the wrong project, dataset, or model checkpoint.
- **Viewing files, searching, and text processing** (`grep`, `find`, `sort`, `uniq`, `cut`) are the
  first tools used to investigate an application log, a stack trace, or a model evaluation output —
  before any dedicated log-analysis or observability tool is available.
- **Pipes and redirection** are exactly how logs and traces from a running service get captured,
  filtered, and turned into evidence during debugging — the same mechanism used later for chaining
  data-processing and evaluation commands.
- **Environment variables** set from the shell are how local secrets (API keys, database URLs)
  reach a script or service without being written into code — directly supporting the secrets
  hygiene every AI project needs.
- **Shell scripts** turn a manual debugging or setup sequence into something repeatable and
  shareable — the same discipline behind setup scripts, CI steps, and small automation later in the
  roadmap.
- **Permissions** explain why a script "permission denied" error happens and how to fix it safely,
  instead of guessing or reaching for `chmod 777`.

Together, these are the skills used to debug a failing AI application or service when something
goes wrong: reading its logs, filtering for the relevant lines, checking file and environment
configuration, and reproducing the failure with the smallest possible command — not by rerunning
the whole system and hoping.

## 6. Practical verification and projects

This module no longer keeps its own local `labs/`, `exercises/`, `examples/`, or `project/`
folders — the practical, verifiable work for all of Stage 0, including this module, is now
consolidated in the Stage 0 roadmap. See
[`../00-Stage-0-Overview/learning-plan.md`](../00-Stage-0-Overview/learning-plan.md) for:

- the audit evidence used to verify Module 0.3 is operational, not just read — completing a
  log-investigation task using commands you understand, not copied commands (Section 2 — "Audit of
  the original four modules");
- **Project 0.2 — Shell File-and-Stream Investigation Lab**, which is this module's main hands-on
  proof: using `grep`, `sort`, `uniq -c`, and redirection to investigate a synthetic set of log
  files and write up the findings (Section 5 — "Practical projects"); and
- the Stage 0 completion gate that this module feeds into, including "I can safely navigate,
  inspect, search, redirect, and permission files from the terminal" (Section 8 — "Stage 0
  completion gate").

## 7. Projects

This module has one local, hands-on project: a practical investigation lab that practises safe
file handling, log investigation, pipes, streams, and redirection end to end. See
[`Projects/README.md`](./Projects/README.md) for the index, and
[`Projects/01-shell-file-and-stream-investigation.md`](./Projects/01-shell-file-and-stream-investigation.md)
to investigate a synthetic set of log files with `grep`, `sort`, `uniq -c`, and redirection, and
write up the findings as evidence.

---

_This README defines structure and sequence only. No lesson content has been written. Each
numbered concept file is a scaffold — see the file itself for its current status._
