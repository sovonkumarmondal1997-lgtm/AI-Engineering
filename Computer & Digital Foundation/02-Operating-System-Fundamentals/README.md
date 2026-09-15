# Module 0.2 — Operating System Fundamentals

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.2 — "Operating
System Fundamentals"

This README is a **roadmap and navigation document only**. It defines what this module covers, in
what order, and why — it does not contain the lessons themselves. Lesson content is written later,
inside each numbered concept file, during the actual teaching phase.

---

## 1. Module purpose

Module 0.2 builds an accurate mental model of how an operating system manages programs and
resources — how a running program actually gets CPU time, memory, files, and signals from the
machine described in Module 0.1. It assumes the hardware and execution concepts from
[`../01-How-Computers-Work/`](../01-How-Computers-Work/README.md) are already understood.

Every later backend, database, model-serving, and agent process is, mechanically, just another
operating-system process. Without this module, a hung process, a memory leak, a permission error,
or a service that won't stop cleanly has no mechanical explanation.

## 2. Prerequisites

Module 0.1 — How Computers Work, specifically processes, files, and I/O at a conceptual level. A
computer running Linux, Ubuntu, or WSL2 (Windows Subsystem for Linux) is required for the hands-on
practice described in Section 6.

## 3. Learning objectives

By the end of Module 0.2, the learner should be able to:

- Explain the difference between kernel space and user space, and why that boundary exists.
- Explain what a system call is and why user programs cannot access hardware directly.
- Explain the difference between a process and a thread, and when each is used.
- Explain, at a basic level, how a scheduler decides which process runs next.
- Explain virtual memory: why a process sees its own private address space.
- Explain filesystems and permissions: how files are organized, owned, and protected.
- Explain environment variables and why they configure a process without hardcoding values.
- Explain signals: how a process is asked to stop, and the difference between a graceful and a
  forced termination.
- Explain the standard streams (`stdin`, `stdout`, `stderr`) and how pipes connect them between
  processes.
- Explain the shell's role in starting, connecting, and controlling processes.
- Narrate a process's full lifecycle: creation, running, waiting, termination, and exit code.
- Identify a running process, inspect its resource use, and stop it safely using OS tools.

## 4. Learning sequence

Work through the numbered concept files in order. Each concept builds on the one before it: the
kernel/user-space boundary and system calls come first because processes, threads, memory, and
signals are all mechanisms the kernel exposes through that boundary.

| # | File | Concept(s) covered |
|---|---|---|
| 1 | [`01-kernel-and-user-space.md`](./01-kernel-and-user-space.md) | kernel space, user space |
| 2 | [`02-system-calls.md`](./02-system-calls.md) | system calls |
| 3 | [`03-processes.md`](./03-processes.md) | processes |
| 4 | [`04-threads.md`](./04-threads.md) | threads |
| 5 | [`05-scheduling.md`](./05-scheduling.md) | scheduling |
| 6 | [`06-virtual-memory.md`](./06-virtual-memory.md) | virtual memory |
| 7 | [`07-filesystems.md`](./07-filesystems.md) | filesystems |
| 8 | [`08-permissions.md`](./08-permissions.md) | permissions, file ownership |
| 9 | [`09-environment-variables.md`](./09-environment-variables.md) | environment variables |
| 10 | [`10-signals.md`](./10-signals.md) | signals |
| 11 | [`11-standard-input-output.md`](./11-standard-input-output.md) | standard input/output/error |
| 12 | [`12-pipes.md`](./12-pipes.md) | pipes |
| 13 | [`13-shell.md`](./13-shell.md) | the shell |
| 14 | [`14-process-lifecycle.md`](./14-process-lifecycle.md) | process lifecycle, exit codes |
| 15 | [`15-os-tools-overview.md`](./15-os-tools-overview.md) | OS tools overview (Linux, Ubuntu, WSL2, Bash, PowerShell) |
| 16 | [`16-local-networking-for-development.md`](./16-local-networking-for-development.md) | local networking for development (`localhost`, ports, DNS, `curl`, `ss -ltnp`) |

## 5. Why this module matters for AI engineering

Every backend API, database, vector store, model server, and agent worker later in the roadmap is,
underneath, just an OS process using the mechanisms this module introduces. Concretely:

- **Processes and threads** explain why a Python web server can handle multiple requests, and why
  CPU-bound work (like embedding generation) can still block a single-threaded process.
- **Virtual memory** explains why one process running out of memory doesn't necessarily crash
  another, and gives the mental model behind out-of-memory errors when loading large models.
- **Filesystems and permissions** explain why a service can fail to read a model checkpoint, write
  a log file, or load a `.env` file — a permissions or ownership problem, not a code bug.
- **Environment variables** are how API keys, database URLs, and model configuration reach a
  running service without being hardcoded — this is the mechanical basis for the secrets hygiene
  every later AI project depends on.
- **Signals and process lifecycle** explain how to stop a model server or worker gracefully (so it
  finishes in-flight requests) versus killing it forcibly, and what an exit code actually tells you
  about why a process ended.
- **Standard streams, pipes, and the shell** explain how logs are produced and captured, and how
  one program's output becomes another program's input — the same mechanism behind log
  aggregation, evaluation pipelines, and command-line tool chains used throughout backend and AI
  work.
- **OS diagnosis skills** — finding a process by PID, inspecting its CPU/memory use, and confirming
  it has actually stopped — are exactly what is needed later to debug a hung model server, a
  runaway training job, or an agent worker that won't release a port.

Without this module, a stuck server, a memory leak, or a service that "just won't die" has no
mechanical explanation — you would be restarting things and hoping, instead of diagnosing them.

## 6. Practical verification and projects

This module no longer keeps its own local `labs/`, `exercises/`, `examples/`, or `project/`
folders — the practical, verifiable work for all of Stage 0, including this module, is now
consolidated in the Stage 0 roadmap. See
[`../00-Stage-0-Overview/learning-plan.md`](../00-Stage-0-Overview/learning-plan.md) for:

- the audit evidence used to verify Module 0.2 is operational, not just read — finding a running
  process, inspecting its PID and resource use, stopping it safely, and explaining exit code `0`
  versus non-zero (Section 2 — "Audit of the original four modules");
- **Project 0.3 — Process, Resource, and Port Diagnosis Lab**, which is this module's main hands-on
  proof: identifying a process by PID, observing its CPU/memory use, discovering a listening port,
  and stopping the process safely with a written incident report (Section 5 — "Practical
  projects"); and
- the Stage 0 completion gate that this module feeds into, including "I can identify a process,
  inspect a local port, stop a harmless process safely, and verify the result" (Section 8 —
  "Stage 0 completion gate").

## 7. Projects

This module has one local, hands-on project: a practical diagnosis lab that practises process,
resource, port, and local-service diagnosis end to end. See
[`Projects/README.md`](./Projects/README.md) for the index, and
[`Projects/01-process-resource-and-port-diagnosis.md`](./Projects/01-process-resource-and-port-diagnosis.md)
to safely start, identify, observe, and stop a test process — and, building on Topic 16, find and
verify a listening local port — with a written incident report as evidence.

---

_This README defines structure and sequence only. No lesson content has been written. Each
numbered concept file is a scaffold — see the file itself for its current status._
