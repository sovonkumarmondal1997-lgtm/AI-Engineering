# Threads — Simple Summary

**Stage 0 · Module 0.2 · Operating System Fundamentals · Concept 04**

---

## 1. What is a thread?

A **thread** is an independent path of execution inside a process.

- **Process:** The container that owns memory and resources.
- **Thread:** An execution path working inside that container.

Every running process has at least one thread. A process with multiple execution paths is called a **multithreaded process**.

---

## 2. Why do threads exist?

Threads allow one application to perform multiple activities during overlapping periods without creating separate processes. They improve responsiveness, handle multiple requests, overlap network/file waiting with other work, and support background tasks.

---

## 3. Why AI engineers need threads

AI applications use threads for tasks such as:

- Making multiple external LLM API calls.
- Handling database queries and network requests.
- Managing concurrent API requests.
- Running background tasks.

However, CPU-heavy model computations do not automatically become faster with more Python threads.

---

## 4. Beginner analogy

Think of a process as a kitchen and threads as multiple cooks working inside it. They share the same pantry and equipment, but each cook has their own task and progress. Sharing makes collaboration easier but can cause interference.

---

## 5. Process vs. thread

| Process | Thread |
|---|---|
| Has a PID | Has its own thread ID |
| Own address space | Shares process memory |
| Stronger isolation | Weaker isolation |
| Communication often needs IPC | Can communicate through shared memory |
| Typically heavier to create | Typically lighter to create |
| Crash generally isolated | Failure can affect the whole process |

**Threads share:** code, heap, global variables, address space and many resources such as open files.

**Threads have individually:** execution state, instruction position, registers/context, stack, thread ID and scheduling state.

Linux identifies threads using terms such as **SPID** (`ps -T`) and **LWP** (`ps -L`).

---

## 6. How threads work

Threads are created and managed through OS/runtime mechanisms. They move through conceptual states: created → runnable → executing → waiting → runnable → completed.

- **Concurrency:** Multiple threads make progress during overlapping periods, even on one CPU core.
- **Parallelism:** Multiple threads execute simultaneously on separate CPU cores.

**Race condition:** A timing-dependent bug caused when threads access shared data in an unsafe order. For example, two threads incrementing a shared counter may both read 0, calculate 1, and write 1. The expected result was 2.

**Synchronization** coordinates access to shared data. **Thread safety** means code remains correct when accessed by multiple threads. Immutable data and isolated per-thread data are generally safer than shared mutable data.

---

## 7. Real-world AI examples

- **Multiple LLM API calls:** threads can overlap network waiting.
- **Database and API calls:** independent I/O operations can run concurrently.
- **Model inference:** CPU/GPU computation needs different performance considerations.
- **Web services:** may use threads, processes, asynchronous execution or combinations.
- **Shared caches:** multiple threads updating a cache can create race conditions.

---

## 8. Python threading and the GIL

Python's `threading` module creates and manages threads.

In default GIL-enabled CPython, the **Global Interpreter Lock (GIL)** constrains CPU-bound Python threading from achieving ordinary parallel execution of Python bytecode within one process. I/O-bound tasks can still benefit because threads can make progress while another thread waits.

The GIL is not universal to every Python implementation; newer free-threaded CPython builds can optionally operate without it. GPU-bound behavior depends on the framework and runtime.

---

## 9. Practical Linux and Python lab

The file demonstrates a Python program creating three worker threads using `threading.Thread`, `start()` and `join()`.

Commands:

- `command -v htop` — check availability (`htop` was not installed in the lesson environment).
- `ps -T -p PID` — display threads using SPID.
- `ps -L -p PID` — display threads using LWP.
- `ls /proc/PID/task` — list thread identifiers.
- `python3 -c "import sys; print(sys._is_gil_enabled() if hasattr(sys, '_is_gil_enabled') else 'API unavailable')"` — inspect GIL status when supported.

The lab confirms that multiple thread rows share one PID but have different thread IDs. The workers finish naturally, and the process exits with status 0.

---

## 10. Misconceptions and debugging

The lesson covers 18 misconceptions and seven troubleshooting scenarios, including: threads are not separate processes; more threads do not guarantee speed; a blocked thread does not necessarily block the whole process; and intermittent shared-data errors may indicate race conditions.

---

## 11. Exercises, expected results and review

The file includes 37 exercises across recognition, understanding, application, debugging and integration, plus review questions. Expected results include explaining process/thread differences, identifying shared versus private state, recognizing race conditions, understanding the GIL and inspecting threads using Linux commands. Actual IDs, tool availability and Python GIL behavior vary by environment.

---

## 12. Production relevance and next topics

Thread knowledge supports API servers, LLM applications, background workers, database operations, model serving, latency/throughput analysis and production debugging.

Next topics include scheduling, virtual memory, filesystems, permissions, environment variables, signals, standard I/O, pipes, shells and process lifecycle.

---

## Most important takeaway

Threads share a process's memory and resources but maintain their own execution state and stack. This shared memory is their biggest advantage—and the source of many production bugs.
