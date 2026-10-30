# Module 0.2 — Operating System Fundamentals

## Lesson 02: System Calls

**Main objective:** Understand how applications communicate with the operating system's kernel to access resources such as files, memory, CPU and networks.

---

## 1. What is a system call?

A **system call** (syscall) is a specific request made by an application to the operating system's kernel to perform an operation that the application cannot perform directly.

For example:

- Reading a dataset.
- Writing a file.
- Creating another process.
- Communicating over a network.
- Requesting additional memory.

**Remember:** The previous lesson explained why the kernel/user-space boundary exists. This lesson explains how applications cross that boundary safely.

---

## 2. Why do system calls exist?

Applications cannot directly control sensitive hardware. However, they still need hardware resources to work.

System calls solve this problem through:

1. **Protection** — prevents unauthorized operations.
2. **Isolation** — protects other applications' resources.
3. **Resource management** — coordinates access to shared resources.
4. **Validation** — checks whether requests are valid and permitted.
5. **Security** — protects against malicious requests.
6. **Hardware abstraction** — applications don't need to understand specific hardware.
7. **Consistency** — provides a common way to request operating-system services.

---

## 3. Why AI and Data Engineers need system calls

Your Python applications depend on system calls for:

- Loading model checkpoints and datasets.
- Accepting HTTP requests through FastAPI.
- Writing application logs.
- Allocating memory for tensors and batches.
- Launching subprocesses and workers.
- Communicating with external APIs.

Excessive system calls can also introduce performance overhead.

---

## 4. Understanding the important terminology

| Term | Simple explanation |
|---|---|
| System call | Request to the kernel |
| Normal function call | One user-space function calls another |
| Library function | Reusable code that may internally use system calls |
| API | Interface through which software communicates |
| Kernel function | Code executing inside the kernel |
| Shell command | Command interpreted or executed by the shell |

For example, Python's `open()` is a library-level function, not itself a Linux system call.

---

## 5. How does a system call work internally?

The process follows nine conceptual steps:

1. Application needs an OS-managed resource.
2. Application or library prepares the request.
3. System-call mechanism is invoked.
4. CPU switches from user mode to kernel mode.
5. Kernel identifies and validates the request.
6. Kernel performs the requested operation.
7. Kernel generates a result or error.
8. CPU returns to user mode.
9. Application continues execution.

A system call generally contains:

- **Syscall number:** Identifies the requested operation.
- **Arguments:** Information needed to perform it.
- **Return value:** The result or error indication.

---

## 6. Important technical concepts

- One Python operation can involve multiple system calls.
- Multiple high-level operations can use the same system call.
- Ordinary arithmetic and in-memory operations normally require no system calls.
- **Buffering** temporarily stores data in memory before actual I/O occurs.
- System calls are the primary controlled mechanism for explicit kernel requests, but exceptions and interrupts can also enter kernel handling.
- Unix-like systems commonly use **file descriptors** to identify files, sockets, pipes and terminals.
- Exact system-call mechanisms differ across operating systems and CPU architectures.

---

## 7. Six real-world examples

1. **Reading files:** Python requests model or dataset contents.
2. **Writing files:** Kernel handles saving logs and checkpoints.
3. **Networking:** AI services send and receive HTTP requests.
4. **Process creation:** Python launches another worker or program.
5. **Standard I/O:** Applications read input and produce output.
6. **Memory operations:** Runtime requests additional memory when needed.

---

## 8. Relationship with upcoming lessons

System calls provide the foundation for processes, threads, scheduling, virtual memory, filesystems, permissions, environment variables, signals, standard I/O, pipes, shell and process lifecycle.

---

## 9. Practical Linux commands

| Command | Purpose |
|---|---|
| `uname -a` | Displays Linux kernel information |
| `python3 --version` | Displays Python version |
| `command -v strace` | Checks whether syscall tracing is available |
| `ps` | Displays running processes |

`strace` is a Linux tool that observes the system calls made by a program. The reference environment did not have it installed, and the lesson explicitly says not to install it for this exercise.

---

## 10. Misconceptions and debugging

The lesson corrects 14 misconceptions and explains eight troubleshooting scenarios:

- **Permission denied:** kernel rejects a file-access request.
- **File not found:** requested resource may not exist.
- **Network failure:** issue may be outside application logic.
- **Unexpected error:** distinguish application errors from OS-level failures.
- **Slow Python function:** not necessarily caused by system calls.
- **Delayed output:** buffering may delay actual I/O.
- **Missing `strace`:** does not prevent conceptual learning.
- **Program runs but later gets permission denied:** each resource request is checked independently.

---

## 11. Exercises and expected outcomes

The file provides 37 exercises across five levels: Recognition, Understanding, Application, Debugging and Integration.

It also includes review questions covering definitions, system-call mechanics, permissions, Python, Linux observations and AI engineering.

---

## 12. Production relevance

System-call knowledge helps engineers understand:

- Slow data pipelines reading thousands of small files.
- AI inference services loading models.
- Network timeouts and connection failures.
- Memory allocation problems.
- Subprocess management.
- Permission-related production failures.
- I/O performance and observability.
- Reliability and security.

---

## What comes next

Processes → Threads → Scheduling → Virtual Memory → Filesystems → Permissions → Environment Variables → Signals → Standard I/O → Pipes → Shell → Process Lifecycle.

---

## Most important takeaway

Your Python code does not directly control the operating system's hardware resources. It uses libraries and runtimes that make system calls to request services from the kernel.

As a Data Engineer or AI Engineer, understanding this mechanism helps you identify whether a problem originates in your Python code or in the underlying operating system.
