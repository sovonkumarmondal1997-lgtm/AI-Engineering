# Concept 15 — OS Tools Overview

**Main objective:** Learn how to inspect and understand what a running process is doing using Linux commands. This lesson introduces no new OS concepts; it teaches you how to observe the concepts covered in the previous 14 lessons.

---

## 1. Core mental model

Every running program becomes an OS process. The operating system maintains information about its identity, state, CPU, memory, files and I/O.

Diagnostic tools allow engineers to inspect this information.

**Important:** No single tool provides the complete picture. Engineers combine multiple tools to diagnose problems.

---

## 2. Essential OS tools

| Tool | Purpose |
|---|---|
| `ps` | Shows a one-time snapshot of running processes. |
| `top` | Continuously monitors processes and CPU/memory usage. |
| `htop` | Optional, more visual and interactive alternative to `top`. |
| `/proc` | Linux pseudo-filesystem exposing live process and kernel information. |
| `kill` | Sends signals to processes. |
| `lsof` | Optional tool for inspecting open files and resources. |
| `ulimit` | Displays resource limits of the current shell. |
| `echo $?` | Displays the previous command's exit status. |
| `id`, `ls -l`, `stat` | Inspect user identity, ownership and permissions. |

---

## 3. Understanding process information

### `ps` — Process snapshot

```bash
ps -ef
ps -o pid,ppid,user,state,stat,%cpu,%mem,etime,cmd -p <pid>
ps --forest
```

Important fields:

- **PID:** Process ID.
- **PPID:** Parent process ID.
- **USER:** Process owner.
- **STATE/STAT:** Current process state.
- **%CPU/%MEM:** CPU and memory usage.
- **ETIME:** Time since process started.
- **CMD:** Command that launched it.

Unlike `ps`, `top` provides continuously refreshed information. It helps identify CPU-heavy, memory-heavy, sleeping, running and long-lived processes.

### `/proc` — Process information

```bash
cat /proc/<pid>/status
cat /proc/<pid>/cmdline
cat /proc/<pid>/stat
cat /proc/<pid>/limits
```

- `status`: Process identity, state, threads and memory.
- `cmdline`: Command that started the process.
- `stat`: Detailed process information.
- `limits`: Resource limits currently applied to the process.

`/proc` is not an ordinary storage directory. Its information is dynamically provided by the Linux kernel.

---

## 4. File descriptors and process states

```bash
ls -l /proc/<pid>/fd
```

Shows which resources a process has open.

- **FD 0:** Standard input.
- **FD 1:** Standard output.
- **FD 2:** Standard error.

Process states can include:

- **R:** Running or runnable.
- **S:** Sleeping/waiting.
- **T:** Stopped.
- **Z:** Zombie.

A sleeping process is not dead. A zombie has already finished executing but its parent has not collected its exit status.

---

## 5. CPU, memory and termination

**CPU inspection:**

```bash
ps -o pid,%cpu,cmd -p <pid>
top
```

**Memory inspection:**

```bash
ps -o pid,%mem,rss,vsz,cmd -p <pid>
cat /proc/<pid>/status
```

- **RSS/RES/VmRSS:** Resident memory.
- **VSZ/VIRT/VmSize:** Virtual memory size.

High CPU does not automatically mean a bug. Similarly, growing memory does not automatically mean a memory leak.

**Process termination:**

```bash
kill -TERM <pid>
kill -INT <pid>
kill -KILL <pid>
```

`kill` sends signals; it does not always force termination. `SIGTERM` requests graceful termination, while `SIGKILL` prevents application cleanup.

Always verify a process's PID and command before signaling it. Never experiment on system or unrelated processes.

---

## 6. Exit codes, permissions and resource limits

```bash
echo $?
```

- `0`: Conventionally successful execution.
- Non-zero: Some failure or special condition.

**Permission inspection:**

```bash
id
whoami
groups
ls -l
stat
```

Permissions determine whether you can inspect or signal processes and access their resources.

**Resource limits:**

```bash
ulimit -a
cat /proc/<pid>/limits
```

`ulimit -a` shows limits for the current shell; `/proc/<pid>/limits` shows limits applied to a particular running process. Limits can restrict open files, stack size and process count.

---

## 7. Process trees and environment differences

```bash
ps --forest
pstree -p <pid>
```

These commands show parent-child process relationships. Thread entries may also appear in the tree.

The lesson uses Ubuntu inside WSL2. Linux commands inspect Linux processes managed by WSL2's Linux kernel, not Windows processes. PowerShell uses different commands, such as `Get-Process` and `Stop-Process`.

Check whether optional tools are installed:

```bash
command -v htop
command -v pstree
command -v lsof
```

---

## 8. Practical labs and debugging

The lesson includes a 10-part practical observation lab covering process creation, PID/PPID, process trees, CPU/memory, `/proc`, file descriptors, states, exit codes, signals and resource limits.

It also includes:

- Seven realistic debugging scenarios: high CPU, high memory, stuck process, unexpected exit, zombie, permission failure and resource-limit failure.
- 37 exercises across five levels: recognition, understanding, application, debugging and integration.
- A mini-project: Python Service OS-Level Observer, requiring a diagnostic report covering process identity, parent, state, CPU, memory, file descriptors, limits and termination.
- Review questions and interview/architecture questions.

---

## 9. Production and AI engineering relevance

These tools are directly applicable to Python API services, LLM inference services, embedding workers, document-processing workers, batch inference, evaluation processes and AI agents.

For example, when an AI inference service becomes slow, an engineer should:

1. Identify its process using `ps`.
2. Observe CPU and memory using `top`.
3. Inspect state using `ps` and `/proc`.
4. Check file descriptors and resource limits.
5. Investigate lifecycle and termination behavior.
6. Form a hypothesis, verify it and take appropriate action.

**The engineering principle:** Tools provide evidence; engineers interpret that evidence to identify the root cause. Restarting a service without collecting evidence can hide the actual problem.

---

## 10. Scope boundaries

This lesson does not cover advanced kernel debugging, scheduler internals, memory profiling, advanced security, networking, Docker/Kubernetes internals, cgroups, namespaces, distributed systems, GPU monitoring or advanced observability platforms. These belong to later roadmap stages.

---

## Final takeaway

An Applied AI Engineer should not only know how to start a Python or AI service but also understand what it is doing at the operating-system level. The essential toolkit is `ps`, `top`, `/proc`, `kill`, `echo $?`, `id` and `ulimit`.
