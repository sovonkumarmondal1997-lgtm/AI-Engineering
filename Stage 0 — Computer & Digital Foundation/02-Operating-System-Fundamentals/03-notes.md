# Processes — Simple Summary

**Stage 0 · Module 0.2 · Operating System Fundamentals**

---

## 1. What is a process?

A **program** is a set of instructions stored on disk. A **process** is an active instance of that program being managed by the operating system.

For example:

- `app.py` sitting in a folder is a program.
- Running `python app.py` creates a process.

One program can create multiple independent processes. Each normally has its own memory, identity and resources.

---

## 2. Why do processes exist?

The OS needs processes to:

- Track which programs are running.
- Allocate and monitor CPU and memory.
- Isolate programs so one crash does not automatically affect others.
- Run multiple instances of the same program.
- Manage starting, stopping and cleaning up programs.

---

## 3. Why AI engineers need this

FastAPI services, model-serving applications, background workers and ETL jobs all run as processes. Understanding processes helps diagnose high CPU usage, memory growth, unresponsive services and crashes.

---

## 4. Beginner analogy

A recipe card is the program; someone actively cooking from it is the process. Multiple cooks can follow the same recipe independently—just as multiple processes can run the same program.

---

## 5. What does a process contain?

A process includes:

- **PID:** its unique process identifier.
- **PPID:** its parent's process ID.
- **State:** running, waiting, stopped, etc.
- **Code and data:** loaded program instructions and data.
- **Virtual address space:** its private view of memory.
- **Stack and heap:** memory used for function calls and dynamic allocation.
- **File descriptors:** references to open files and network connections.
- **Environment:** environment variables and working directory.
- **Security identity and scheduling information:** details the kernel manages.

A process contains one or more threads. CPU execution details such as registers and instruction position belong to individual threads.

---

## 6. How processes work internally

The general lifecycle is:

1. An existing process requests process creation through a system call.
2. The kernel assigns a PID and records the PPID.
3. Memory, code, environment and resources are prepared.
4. The process becomes ready to run.
5. The scheduler gives it CPU time.
6. It switches between running and waiting states.
7. It accesses files, networks and memory through system calls.
8. It finishes, is stopped or crashes.
9. The kernel cleans up most resources and records its exit status.

**Concurrency vs. parallelism:**

- **Concurrency:** multiple processes make progress during overlapping periods by taking turns.
- **Parallelism:** multiple processes execute at exactly the same time on different CPU cores.

More processes do not automatically mean more parallelism or four-times the performance.

**Process isolation** protects processes from directly accessing or corrupting each other's memory under normal conditions. It provides fault isolation, resource accounting and security boundaries, but is not an absolute security guarantee.

---

## 7. Real-world examples

Processes include Python scripts, web/API services, multiple workers, ETL jobs, AI inference services and background tasks. A process waiting for network or file I/O still exists, even if its CPU usage is near zero. High CPU or memory usage can indicate a problem, but does not automatically explain its cause.

---

## 8. Related concepts

Processes connect to kernel/user space, system calls, threads, scheduling, virtual memory, filesystems, permissions, environment variables, signals, standard I/O, pipes, shells and process lifecycle.

---

## 9. Practical Linux commands

| Command | Purpose |
|---|---|
| `ps` | Inspect processes, PID, PPID, state and resource usage |
| `top` | Monitor processes continuously |
| `htop` | Interactive alternative to `top`, if installed |
| `/proc/<PID>/status` | Inspect process details |
| `/proc/<PID>/cmdline` | View its command and arguments |
| `/proc/<PID>/cwd` | View its working directory |
| `/proc/<PID>/fd` | Inspect open file descriptors |
| `kill <PID>` | Send a termination signal (default: SIGTERM) |
| `echo $?` | Display the previous command's exit status |

Exit status `0` conventionally means success; non-zero usually indicates failure or another condition. Exact non-zero meanings depend on the application.

The file includes a safe WSL2 lab: start an idle background process, capture its PID, inspect it using `ps` and `/proc`, terminate it with `kill`, and verify cleanup. Its sample environment did not have `htop` installed, and installation was not required.

---

## 10. Misconceptions and troubleshooting

The lesson corrects 18 misconceptions, including:

- A program is not the same as a process.
- A process does not always use CPU.
- A PID is not a permanent application identifier.
- Multiple processes do not guarantee parallelism.
- A thread is not a process.
- `kill` does not delete the program or necessarily destroy a process immediately.
- A process showing 0% CPU is not necessarily broken.

It also covers six debugging scenarios: an unresponsive service, excessive CPU, growing memory, accidentally targeting the wrong PID, a process disappearing, and editing a program file without restarting its running process.

---

## 11. Exercises and expected results

The file provides 37 exercises across five levels: recognition, understanding, practical application, debugging and integration. It also includes review questions covering program/process differences, identity, states, resources, isolation, concurrency, commands and production debugging.

You should be able to explain process concepts, inspect processes, understand their resource usage and distinguish concurrency from parallelism. Actual PIDs, process lists, resource figures and installed tools will vary by machine.

---

## 12. Production relevance and next topics

Process knowledge is essential for API services, LLM inference, background workers, ETL pipelines, CPU/memory monitoring, I/O troubleshooting, reliability and security.

The next lessons cover threads, scheduling, virtual memory, filesystems, permissions, environment variables, signals, standard I/O, pipes, shells and process lifecycle. Containers and distributed systems build on this foundation.

---

## Most important takeaway

A program is passive instructions; a process is the OS-managed, active execution instance with its own identity, memory, state and resources.
