# Concept 12 — Pipes

**Module:** Stage 0 → Module 0.2 — Operating System Fundamentals

---

## 1. What Is a Pipe?

A **pipe** is an operating-system-managed communication channel that transfers bytes from one process to another.

Think of it as a conveyor belt:

- Process A puts data onto the belt.
- Process B receives that data.
- The OS manages the transfer.

A pipe is not a regular file stored on disk. It temporarily holds data in a kernel-managed buffer.

---

## 2. Why Pipes Exist

Without pipes, programs may need temporary files to exchange data. Pipes provide:

- Direct data streaming.
- Processing data without waiting for the entire output.
- Less unnecessary disk usage.
- No temporary-file cleanup.
- Easy connection of small, independent programs.

Trade-offs include limited buffering, blocking, backpressure, error handling and debugging complexity.

---

## 3–5. Pipes and File Descriptors

A pipe has two ends:

- **Write end:** Where a process sends data.
- **Read end:** Where another process receives data.

Example:

```text
Process A → stdout (FD 1) → Pipe → stdin (FD 0) → Process B
```

The OS/kernel manages the pipe and its buffer. Each process accesses its own end through its own file descriptor.

---

## 6–8. Buffering, Blocking, Backpressure and EOF

- **Buffering:** The OS temporarily holds data until the reader consumes it.
- **Finite capacity:** A pipe cannot store unlimited data.
- **Blocking:** A writer waits when the buffer is full; a reader waits when no data is available but the write end remains open.
- **Backpressure:** A slow consumer forces a fast producer to slow down.
- **EOF:** Means no more data will ever arrive.

**Important:** EOF occurs only after every reference to the pipe's write end is closed. Forgetting to close unused ends can make readers wait forever.

---

## 9–10. Broken Pipes and Pipe vs Regular File

A **broken pipe** occurs when a process writes after the reader has closed its end. On Unix/Linux, this can trigger `SIGPIPE`; Python commonly reports `BrokenPipeError`.

| Pipe | Regular file |
|---|---|
| Temporary communication | Persistent storage |
| Kernel buffer | Filesystem storage |
| Sequential stream | Supports random access |
| Data disappears after reading | Data remains until deleted |
| Connects processes | Can be opened independently |

---

## 11–12. Anonymous Pipes and Named Pipes (FIFO)

- **Anonymous pipe:** Has no filesystem name. Commonly shared between related processes through file-descriptor inheritance.
- **Named pipe (FIFO):** Has a filesystem-visible path, allowing unrelated processes to communicate through it.

Use `mkfifo` to create a FIFO. In `ls -l`, its file-type character is `p`. Despite its filesystem name, it does not store persistent data.

---

## 13–16. Shell Pipelines

`A | B` connects A's stdout to B's stdin.

For multiple stages, `A | B | C`, two pipes connect three processes.

Example:

```bash
printf '%s\n' apple banana apricot avocado | grep '^a' | sort
```

- `printf` produces values.
- `grep` filters them.
- `sort` orders them.

**Important:** stderr does not automatically travel through the pipe. Only stdout does.

Pipeline exit statuses also matter. In Bash, `$?` normally reports only the last command's status. `PIPESTATUS` shows individual statuses, while `set -o pipefail` helps expose earlier failures.

---

## 17–18. Python Pipes and Deadlocks

Python supports pipes through:

- `os.pipe()` — creates read and write file descriptors directly.
- `subprocess.Popen()` — creates pipes between parent and child processes.
- `communicate()` — coordinates input, output and process completion, avoiding common pipe-buffer deadlocks.

A **deadlock** can happen when the parent waits for the child to read input while the child waits for the parent to read output. Neither progresses.

---

## 19–21. Practical Labs and Platform Differences

The lesson demonstrates shell pipelines, multi-stage pipelines, stdout/stderr separation, FIFO creation, Python `os.pipe()`, and inspecting descriptors through `/proc/<PID>/fd`.

WSL2 runs genuine Linux pipe behaviour. PowerShell differs: its pipeline generally passes structured objects rather than Unix-style byte streams.

---

## 22–25. AI Engineering, Debugging and Mini-Project

Pipes are useful for data preprocessing, transformation, model evaluation, batch inference, log processing and subprocess orchestration.

The mini-project builds three Python programs:

1. **Producer:** Emits raw values.
2. **Processor:** Validates and transforms values, sending warnings to stderr.
3. **Consumer:** Aggregates processed values.

The lesson includes 12 debugging scenarios, common misconceptions, 37 exercises, review questions and interview/architecture questions.

---

## 26–32. Production and Roadmap

Production concerns include blocking, backpressure, deadlocks, output volume, stderr handling, EOF, resource cleanup and failure propagation.

The lesson also covers connections to processes, threads, scheduling, filesystems, permissions and signals.

Advanced IPC, sockets, asynchronous I/O, Kafka, RabbitMQ, distributed messaging, container internals and advanced deadlock theory are outside its scope.

**Final mental model:** Process A writes bytes to its stdout. The OS transfers them through a finite pipe buffer. Process B reads them through its stdin. Neither process needs to know that the other exists.
