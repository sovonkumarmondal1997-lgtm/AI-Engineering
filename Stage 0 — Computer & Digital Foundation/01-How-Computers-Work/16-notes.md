# Processes

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 16

---

## 1. What Is a Process?

A **process** is a running instance of a program, with its own execution context and associated resources managed by the operating system (OS).

- **Source code:** Human-readable instructions.
- **Executable:** A file the OS can launch.
- **Program:** A general term for the instructions or code being run.
- **Process:** One specific running instance of a program.

Launching the same program twice can create two separate processes, each with its own Process ID (PID).

---

## 2. Why Processes Matter

The OS uses processes to track and manage running programs, their execution state, memory, files, I/O, and CPU time. Processes provide conceptual separation between programs so their execution and resources do not arbitrarily interfere.

Each process has a unique PID while it exists. A PID identifies a running instance, not the program itself.

---

## 3. Process Memory, Execution Context, and Resources

A process has a **virtual address space**—its view of memory, not necessarily a dedicated chunk of physical RAM. Common conceptual regions are:

- **Code:** Machine instructions.
- **Data:** Initialized program data.
- **Stack:** Function-call tracking and short-lived local values.
- **Heap:** Data requested dynamically while running.

Its **execution context** includes CPU-related state, register values, and the program counter/instruction pointer, which identifies the next instruction.

Resources can include RAM, files, I/O, CPU time, and devices accessed through the OS. A process uses these resources; it does not permanently own the CPU, physical RAM, or computer.

---

## 4. Process States and Lifecycle

The simplified five-state model is:

- **New:** Being created.
- **Ready:** Waiting for CPU execution time.
- **Running:** Executing instructions on a CPU core.
- **Waiting/blocked:** Waiting for I/O or another event.
- **Terminated:** Finished and no longer running.

A process can exist without using CPU time—for example, while waiting for a file read or network request. On termination, the OS reclaims resources; Unix-like systems may temporarily retain a **zombie** child process. An **exit status** indicates the outcome of a process.

---

## 5. Processes, Cores, Concurrency, and Threads

- **Process vs. CPU core:** A process is software execution context; a core is hardware. Processes can take turns on one core or execute in parallel when enough execution resources are available.
- **Concurrency:** Multiple tasks progress over overlapping periods, possibly by taking turns.
- **Parallelism:** Multiple tasks execute simultaneously.
- **Process vs. thread:** A process is the broader resource boundary; a thread is an execution path within a process. Threads generally share their process's memory and resources.

---

## 6. Practical Work, Exercises, and AI Relevance

The Linux/WSL2 practical demonstrates process creation and observation using `sleep`, `$!`, `pgrep`, `pidof`, `ps`, `/proc/PID/status`, and `kill` on a harmless, self-created process. PIDs vary by environment.

The module contains 34 exercises, 15 common misconceptions, and review questions. Answers are in `exercises/16-processes-answer-key.md`.

In AI engineering, processes run API servers, inference workers, training workloads, and logging tasks. They load models, process data, use CPU/GPU resources, read datasets, write checkpoints, and exchange network data.

**Scope boundaries:** Scheduling algorithms, context switching, thread programming, detailed process startup, OS internals, and production orchestration are reserved for later lessons.

---

## Next

**Concepts 17–20** — program startup, function execution, RAM vs. storage, and why GPUs matter for AI.
