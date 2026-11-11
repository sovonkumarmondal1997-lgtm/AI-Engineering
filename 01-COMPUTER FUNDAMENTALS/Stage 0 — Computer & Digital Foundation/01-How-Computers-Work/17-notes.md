# What Happens When a Program Starts

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 17

---

## 1. Program, Executable, and Process

- **Program:** Instructions or code stored as a file.
- **Executable:** An artifact that can be launched directly or through a runtime.
- **Process:** A running instance of a program managed by the operating system (OS), with its own Process ID (PID), execution context, and resources.

A stored program does not automatically run just because its file exists.

---

## 2. The Program Startup Sequence

Starting a program involves several steps—not simply clicking an icon and immediately executing code.

1. A user or another program requests a launch.
2. The OS receives the request.
3. A new process is created and assigned a PID.
4. The process's execution environment and address space are established.
5. The executable's code and data are made available to the process.
6. Required libraries and runtime components are prepared where applicable.
7. Initial execution state, environment information, and arguments are established.
8. The CPU begins executing instructions at the executable's entry point.
9. Startup/runtime initialization occurs where needed.
10. The program reaches its application-level code.

This is a conceptual sequence; the exact implementation differs across operating systems and programming languages.

---

## 3. Loading and Process Memory

The **loader** prepares an executable for execution. It is an oversimplification to say the OS always copies the entire executable into RAM at once.

A process's address space commonly includes:

- **Code/text:** Machine instructions.
- **Initialized data:** Data with specified starting values.
- **BSS:** Data that starts with default values, commonly zero.
- **Heap:** Dynamically requested memory.
- **Stack:** Function-call information and short-lived local values.

The executable remains on storage; the running process uses its own execution environment and memory.

---

## 4. Dependencies and Runtime Initialization

Executables may contain machine instructions, data, metadata, and references to required components. Programs may depend on shared libraries, interpreters, or runtimes.

The CPU begins at the **entry point**, which is not necessarily the programmer's `main` function. Startup code may execute before `main`.

- **C:** Commonly uses a native executable with startup code before `main`.
- **Python:** Typically starts an interpreter/runtime before executing application-level code.
- **Java:** Commonly starts the JVM, which loads and executes bytecode.

These are typical examples, not universal rules for every implementation.

---

## 5. Arguments and Environment Variables

- **Command-line arguments:** Values supplied at launch, such as a filename or option.
- **Environment variables:** Named configuration values made available to the process.
- **Standard input (stdin):** A separate stream a program may read during execution.

Arguments and environment variables are not the same as stdin, and environment variables are not files.

---

## 6. Practical Linux/WSL2 Exercises

The module demonstrates:

- `file /bin/sleep` — inspect the file type.
- `ldd /bin/sleep` — inspect shared-library dependencies; use only trusted executables.
- `readelf -h /bin/sleep` — inspect executable metadata, including the entry point.
- `sleep 60 &`, `PID=$!`, and `ps` — observe a harmless process and its PID.
- `time -p true` — observe command execution time, not startup time alone.
- `kill "$PID"` — clean up only the process created for the exercise.

Example outputs, PIDs, addresses, and library paths vary by environment. WSL2 observations do not necessarily represent Windows startup behavior.

---

## 7. AI Engineering Relevance, Mistakes, and Review

AI services and workers undergo startup before application logic runs. Process creation, dependency preparation, runtime initialization, and configuration can delay readiness. Model loading is a separate application-level activity that happens after the process reaches application code.

The module includes 38 exercises, 15 common misconceptions, review questions, and an answer key at `exercises/17-what-happens-when-a-program-starts-answer-key.md`.

Detailed kernel internals, executable formats, dynamic linking, function execution, GPU architecture, Docker, Kubernetes, and model-serving frameworks are outside this lesson's scope.

---

## Next

**Concept 18 — What Happens When a Function Executes**
