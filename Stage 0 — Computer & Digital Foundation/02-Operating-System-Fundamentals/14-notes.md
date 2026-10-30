# Concept 14 — Process Lifecycle

**Stage 0 · Module 0.2 — Operating System Fundamentals**

A **process lifecycle** describes the complete life of a process: how it is created, runs, waits, communicates, terminates, and how its parent collects its final result.

---

## 1. Process Lifecycle Overview

A process generally follows this sequence:

Creation → Initial setup → Ready → Running → Waiting → Running again → Termination → Exit-status collection → Resource cleanup.

A process may repeatedly move between running and waiting before it terminates. Exact state names differ between operating systems.

---

## 2. Creating Processes: `fork()` and `exec()`

- `fork()` creates a new child process by duplicating the calling process. Parent and child receive separate PIDs and execute independently. The parent receives the child's PID; the child receives 0.
- `exec()` replaces the current process's program with another program. It does not create a new process; the PID remains the same.

**Remember:** `fork()` creates; `exec()` replaces.

Shells commonly use this create-then-execute pattern when launching commands.

---

## 3. Process States

| State | Meaning |
|---|---|
| New | Process is being created |
| Runnable | Waiting for CPU time |
| Running | Executing on CPU |
| Waiting/Blocked | Waiting for I/O, event or timer |
| Stopped | Paused, usually by a signal |
| Terminated | Execution has ended |
| Zombie (Z) | Terminated, but exit status not collected |

**Lifecycle vs scheduling:** Lifecycle describes the process's complete existence. Scheduling decides when it gets CPU time.

---

## 4. Parent and Child Processes

- **PID:** Process's own identifier.
- **PPID:** Parent's PID.
- **Parent:** Process that creates another process.
- **Child:** Newly created process.
- **Process tree:** Hierarchy of parent-child relationships.

Useful commands: `pstree -p $$`, `ps -f`, `ps --forest -o pid,ppid,stat,cmd`.

---

## 5. Waiting and Termination

Processes can wait for keyboard input, files, pipes, timers or other processes. Waiting is normal and generally consumes little CPU.

A parent uses:

- `wait()` to collect any child that finishes.
- `waitpid()` to collect a particular child.

Processes terminate through normal completion, errors, signals or forced termination. `SIGKILL` prevents application cleanup.

---

## 6. Exit Status

**Exit status** is an integer describing the process's outcome.

- `0`: Conventionally successful.
- Non-zero: Failure or another application-defined condition.
- Python `sys.exit(0)` and `sys.exit(1)` explicitly set status.
- Unhandled Python exceptions normally produce a non-zero status.

The parent or shell collects this result after termination.

---

## 7. Zombies and Orphans

**Zombie:** A child has finished executing, but its parent has not collected its exit status using `wait()`/`waitpid()`. It consumes no CPU and retains only minimal bookkeeping.

**Orphan:** A child is still running, but its original parent has terminated. The OS assigns it a new parent, commonly `init` or a child subreaper.

| Zombie | Orphan |
|---|---|
| Already terminated | Still running |
| Exit status not collected | Original parent has disappeared |
| Needs reaping | Reparented to another process |

---

## 8. Process Groups, Sessions and Signals

- **Process group:** Related processes that can receive signals together, such as pipeline stages.
- **Session:** Contains multiple process groups, commonly associated with a terminal session.
- **Controlling terminal:** Delivers signals such as Ctrl+C and Ctrl+Z to the foreground process group.

Signals can stop a process (`SIGSTOP`), resume it (`SIGCONT`), request termination (`SIGTERM`) or force termination (`SIGKILL`).

---

## 9. Shell, Pipes and Python

- Shell creates child processes, waits for foreground commands and collects their exit statuses.
- Pipelines connect one process's stdout to another's stdin.
- When a producer exits and all write descriptors close, its consumer can receive EOF.
- Unexpected termination can cause broken-pipe failures.
- Python exposes lifecycle operations through `os.getpid()`, `os.getppid()`, `os.fork()`, `os.waitpid()`, `sys.exit()`, `subprocess` and `multiprocessing`.

---

## 10. Practical Work and Production Relevance

The lesson includes six Linux/WSL2 labs, a Python Process Lifecycle Observer mini-project, 14 debugging scenarios, 18 misconceptions, 37 exercises, review questions and interview/architecture questions.

Production failure modes include zombie accumulation, child-process leaks, orphaned workers, repeated crashes, ignored exit codes, stuck processes, excessive CPU/memory consumption, and failed graceful shutdown.

For AI engineering, Python APIs, model-serving services, batch inference, embedding workers, ETL jobs, evaluation processes and AI agents all follow this lifecycle. Reliable systems must monitor processes, collect exit statuses, manage resources and implement graceful shutdown.

**Final mental model:** A process is an OS-managed execution instance with an identity, memory, resources and a lifecycle. Understanding that lifecycle is foundational to reliable AI services, deployment, observability and scaling.

**Scope boundary:** Advanced scheduling, synchronization, async programming, Docker/Kubernetes/systemd internals, containers, namespaces, cgroups and distributed systems are reserved for later topics.
