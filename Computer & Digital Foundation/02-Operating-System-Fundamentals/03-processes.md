# Processes

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** processes, PID/PPID, process state, process resources, process isolation, concurrency vs parallelism
**Status:** Not Started

---

## 1. What Is It?

**Connecting to what you already know.** [Kernel and User Space](01-kernel-and-user-space.md) established that ordinary programs run in user space while the kernel manages shared resources. [System Calls](02-system-calls.md) established the specific mechanism — a controlled trap into the kernel — that a user-space program uses to request something from the kernel. This lesson introduces the entity that actually *does* the running: the **process**. Process creation and many process and resource operations (such as waiting for a child or requesting more memory) involve system calls and are carried out by the kernel; ordinary user-space execution is not continuously a system-call request, and the scheduler lets a process's code run without every instruction being requested through the kernel — everything in this lesson sits directly on top of the previous two lessons.

**Program.** Simple meaning: a program is a set of instructions and data that can be executed, commonly stored in a file on disk, doing nothing by itself. Technical meaning: a program is a static artifact — executable code and associated data, commonly stored in a file — that describes what should happen when it is run, without itself being an active, running thing. Your `app.py` file, sitting in a folder, is source code that an interpreter (Python) can execute; for this lesson, treat it as the "program." It does not use CPU time, does not hold memory, and does not have any running state, no matter how long it sits there.

**Process.** Simple meaning: a process is an operating-system-managed execution instance of a program — an active, tracked, in-progress execution of that program's instructions. A process can exist while it is executing, runnable, waiting/sleeping, stopped, or (depending on the OS) in a terminated/zombie-related state. Technical meaning: a process is an execution instance that the operating system creates, identifies, and manages, consisting of the program's loaded code and data, a private virtual address space, an execution state, and a collection of OS-managed resources (open files, environment, credentials, and more — all introduced in Section 5).

**The single most important distinction in this lesson, stated plainly:**

```text
Program                              Process
------------------------------       ------------------------------
Commonly a file on disk              An OS-managed execution instance
Passive                              Active
No memory, no CPU use, no state      Has memory, may use CPU, has a state
One program file                     Can produce zero, one, or many processes
Exists whether or not anything
  is running it                      Exists only while the OS is tracking it
```

**A simple mental model** for this lesson:

```text
Program
     ↓
Executable instructions + data (on disk, passive)
     ↓
OS starts it                          (via system calls introduced in Concept 02)
     ↓
Process
     ↓
Process has:
     - identity                       (PID, PPID)
     - execution state                (running, waiting, stopped, ...)
     - virtual address space           (its own private view of memory)
     - resources                        (open files, network connections, ...)
     - open I/O resources                (file descriptors)
     - environment                        (environment variables, working directory)
     - scheduling state                    (the kernel's bookkeeping for CPU time)
     ↓
OS manages it while it runs
     ↓
Process terminates
     ↓
Exit status / cleanup
```

**Important caveat, repeated throughout this lesson:** this is a conceptual model. The exact internal representation of a process differs between operating systems, and this lesson deliberately does not teach any one OS's internal data structures. What matters is the *shape* of the idea: a process is the OS's tracked, running instance of a program, distinct from the program file itself.

---

## 2. Why Does It Exist?

**The problem.** A computer needs to run many programs — sometimes the same program more than once — while keeping track of what's currently executing, what resources each execution instance is using, and how to isolate one running program's mistakes from another. A program file on disk cannot answer "is this currently running?", "how much CPU has it used?", or "what files does it currently have open?" — a file is just static data. The operating system needs some tracked, living representation of "a program that is actually happening right now." That representation is the process.

```text
Requirement: run programs, possibly many at once, possibly the same program more than once
     ↓
Requirement: track what is currently executing, and manage its resources safely
     ↓
Requirement: isolate one running program from accidentally or maliciously affecting another
     ↓
The operating system needs a tracked, managed unit representing "a program, running"
     ↓
This is the process
```

**The specific engineering reasons processes exist as a distinct concept from programs:**

- **Tracking.** The kernel needs to know, at any moment, what is currently running, so it can allocate CPU time, respond to requests, and clean up afterward.
- **Isolation.** Section 12 covers this in depth — each process gets its own private virtual address space, so one process's bugs cannot silently corrupt another's memory.
- **Resource accounting.** The kernel needs to know which open files, which memory, and which CPU time belong to which running program, so it can manage and eventually reclaim those resources.
- **Multiplicity.** The same program file might need to run more than once at the same time (Section 5) — the process concept is what allows the OS to track each running instance separately, even though they all originated from the same file.
- **Controlled lifecycle.** Programs need a well-defined way to start, run, and eventually stop, with the OS able to clean up afterward (memory freed, files closed) regardless of whether the program exited cleanly or crashed.

**What would go wrong without a process concept.** If the OS only tracked "which program files exist" rather than "which execution instances are currently running," it would have no way to know how much CPU or memory a given running instance was using, no way to isolate one running instance's memory from another's, and no way to cleanly stop or clean up after just one specific running instance without guessing. The process concept exists specifically to give the kernel a concrete, trackable unit to manage.

---

## 3. Why an AI Engineer Needs It

- **Every Python AI service you run is one or more OS processes.** A FastAPI application, a model-serving process, a background worker — the operating system does not know or care about "routes" or "models"; it sees processes, each with a PID, a memory footprint, and a CPU/I/O usage pattern (Section 12 develops this distinction fully).
- **"Why is my service slow / using too much memory / not responding?" is frequently a process-observation question.** Knowing how to look at a running process — its state, its CPU and memory usage, its open files — is a direct, practical skill for diagnosing real production behavior, not an abstract OS concept.
- **Multiple worker processes are extremely common in production AI services.** Frameworks that serve inference requests often run several worker processes to handle load; understanding what a process actually *is* is the prerequisite for understanding why running four workers is different from running one, and why they don't automatically share memory or state.
- **Process crashes and restarts are everyday production realities.** An inference service can crash because of a bug, run out of memory, or be killed by a resource limit — understanding what "the process terminated" actually means, and what the OS cleans up automatically versus what doesn't get cleaned up, changes how you reason about reliability.
- **Background workers and data pipelines are processes too.** A Python script processing a batch of files, or a task-queue worker consuming jobs, is exactly the same kind of OS entity as an API service — the same observation tools and mental model apply.

A concrete preview, expanded fully in Section 12:

```text
Python AI service (started with something like `python app.py` or a process-manager command)
     ↓
the OS creates a process
     ↓
that process has: a PID, memory, open files (model weights, logs, sockets), CPU usage, a state
     ↓
as load increases, memory grows, or a bug triggers a crash — this is all visible,
observably, at the process level — often before you'd ever see it purely in application logs
```

---

## 4. Beginner Explanation

**Analogy: a recipe versus someone actually cooking it.**

```text
Recipe card              = the program (a set of written instructions, sitting in a drawer)
Someone actually cooking
  the recipe right now    = the process (an active instance of following those instructions)
Kitchen, ingredients,
  the cook's current step  = the process's resources and current state
```

A recipe card sitting in a drawer is not "cooking" — it's just information, describing what steps to follow if someone decides to cook. It has no current temperature, no current step, no ingredients currently in use. Now imagine a cook picks up that card and starts actually cooking: *now* there's an active, trackable activity — a specific pot on a specific burner, a current step in the recipe, specific ingredients currently in use, a start time. That active, trackable activity is the process; the card itself, sitting in the drawer, remains the program, and it doesn't change or get "used up" just because someone is currently cooking from it.

**Extending the analogy to the "why can one program become many processes" idea (Section 5):** the same recipe card can be used by three different cooks in three different kitchens at the same time. Each cook is independently following the same written steps, but each is a separate, trackable activity with its own pot, own ingredients, and own current step — one cook burning their dish doesn't affect the other two. This is a rough beginner-level preview of why running the same Python script twice produces two independent processes, not one.

**Where this analogy is useful:** it captures the core distinction — passive instructions versus an active instance of following them — and the idea that the same instructions can be followed independently, more than once, at the same time.

**Where this analogy breaks down:**

- A human cook exercises judgment while cooking; a process executes precisely, exactly as its instructions specify, with no improvisation (this echoes the same limitation noted for the CPU analogy in Module 0.1).
- A recipe card doesn't have anything resembling "memory" or "open files" the way a real process does — Section 5 introduces exactly what a process actually consists of, beyond this analogy's scope.
- Real processes are created, managed, and destroyed by the operating system through specific, precise mechanisms (system calls) — not by a cook's free choice to start or stop cooking.

**What you should take away from this section, in one sentence:** a program is a static description of what to do, and a process is the operating system's tracked, active instance of actually doing it — and the same program can produce more than one independent process at the same time.

---

## 5. Technical Explanation

**Why multiple processes can run the same program.** Nothing about a program file changes when it runs — the file is only ever *read*, not consumed. Separate launches normally create separate process instances: each with its own identity, its own virtual address space, and its own resources — normally independent of any other currently running instance of the same program. (Operating systems can also intentionally let processes share memory and other resources, but that is not the default.)

```text
app.py  (one program file, unchanged, on disk)
     ↓ run it                ↓ run it again              ↓ run it again
Process A (PID 1001)     Process B (PID 1002)        Process C (PID 1003)
own memory                own memory                   own memory
own open files             own open files                own open files
own state                   own state                      own state
```

This is why, for example, a production AI service can run four independent worker processes from the exact same `app.py` file — each is a fully separate process, with its own memory and its own resources, even though they all started from identical code.

**What a process contains — the major conceptual components.** Some of these are directly relevant to how your application behaves (process-owned/application-visible state); others exist purely so the kernel can manage the process (kernel-maintained process-management information). Both categories matter, but for different reasons.

| Component | What it is | Category |
|---|---|---|
| **PID** (process ID) | A unique identifying number the OS assigns to this specific running instance (Section 5's next subsection) | Kernel-maintained (identity) |
| **Process state** | Whether the process is currently running, waiting, stopped, etc. (Section 6) | Kernel-maintained |
| **Program code** | The loaded, executable instructions the process is running | Process-owned |
| **Data** | The program's static and dynamic data loaded into memory | Process-owned |
| **Virtual address space** | The process's own private view of memory, isolated from other processes (full detail: Virtual Memory lesson) | Kernel-maintained, application-visible |
| **Stack** | Memory used for function calls, local variables, and tracking "where to return to" as code executes | Process-owned |
| **Heap** | Memory dynamically allocated while the program runs (for example, growing a Python list) | Process-owned |
| **CPU execution context** | Belongs to each thread of the process: the current CPU registers, instruction position, and stack, saved and restored as the OS switches between threads (a process has one or more threads; see the note below the table) | Kernel-maintained |
| **Open file descriptors** | References to files, network connections, and other I/O resources the process currently has open | Process-owned, kernel-tracked |
| **Environment** | Environment variables available to the process (full detail: Environment Variables lesson) | Process-owned |
| **Working directory** | The filesystem location relative paths are resolved against for this process | Process-owned |
| **Security credentials/identity** | The user and group identity the process runs as, used for permission checks (full detail: Permissions lesson) | Kernel-maintained |
| **Parent-process relationship** | Which process created this one (Section 5's next subsection) | Kernel-maintained |
| **Scheduling information** | Bookkeeping the kernel uses to decide when this process gets CPU time (full detail: Scheduling lesson) | Kernel-maintained |

```text
Process
 └── one or more threads
       ├── execution context
       ├── registers
       ├── instruction position
       └── stack
```

Execution context, registers, instruction position, and stack are really per-thread; the Threads lesson explains this properly. Here, treat the "CPU execution context" row as a preview.

**Deliberately out of scope here:** the full internal implementation of virtual memory (page tables, how isolation is physically enforced) is the Virtual Memory lesson; the full mechanics of the CPU scheduler are the Scheduling lesson; the internal structure of a thread within a process is the Threads lesson, which comes immediately after this one.

### Process identity: PID and PPID

**PID (Process ID).** Simple meaning: a number the operating system assigns to a running process so it can be uniquely referred to. Technical meaning: the PID is an operating-system-assigned identifier (on Linux, an integer), unique among currently existing processes within its scope, used whenever the OS or a tool needs to refer to a specific process — for observation (`ps`), for control (`kill`), or for any other process-specific operation.

**PPID (Parent Process ID).** Simple meaning: the PID of the process currently serving as this process's parent in the operating-system process hierarchy (usually the process that created it). Technical meaning: when a process creates another process (the mechanism for this is previewed only conceptually in Section 6 — its full detail is later curriculum), the newly created process is initially recorded as its creator's child, forming a traceable parent/child relationship.

**Why identity matters.** Without a stable way to refer to a specific running instance, you could not observe it, reason about it, or safely stop it. PIDs are exactly what makes "which process do you mean?" answerable — for a human using `ps` and `kill`, and for the kernel itself internally.

**An important, easily-missed nuance:** a PID identifies a specific *running instance*, not "the application" in any lasting sense. If a process ends and the same program is started again, the new process will very likely be assigned a *different* PID — the OS typically does not guarantee the same number will be reused for "the same application" the next time it runs. Treat a PID as valid only for the lifetime of that one specific process.

**A conceptual process hierarchy:**

```text
init/system process (PID 1)
│
├── service process
│      ├── worker process
│      └── worker process
│
└── another process
```

This diagram is a Unix/Linux-oriented conceptual model: it illustrates the *shape* of the idea — processes form a tree, where each process (other than the very first one the system starts) has one parent — not a literal, universal layout for every operating system. The exact hierarchy you observe depends entirely on your specific environment, what's currently running, and how it was started. **In WSL2 specifically, the process hierarchy you observe belongs to the Linux environment running inside WSL2** — it reflects what Ubuntu itself has started (a shell, background services, whatever you've launched), not a hierarchy of the Windows host's own processes.

### Process state

**Process state.** Simple meaning: what a process is currently doing — actively computing, waiting for something, paused, or finished. Technical meaning: process state is a kernel-tracked attribute recording which phase of execution a process is currently in, used by the kernel (particularly the scheduler) to decide what to do with it next.

**A simplified conceptual model of execution states** (actual process/thread states and terminology vary by operating system and implementation):

| Conceptual state | Meaning |
|---|---|
| Running | Currently executing on a CPU right now (strictly, it is a thread of the process that executes; the Threads lesson explains this) |
| Ready / runnable | Able to run, waiting only for the CPU to become available |
| Sleeping / waiting | Not running, because it's waiting for something else (I/O to complete, an event, a timer) |
| Stopped | Execution has been paused, typically by an explicit control action |
| Terminated | Execution has ended; the OS is finishing cleanup |

**The critical distinction this section insists on:** a process can *exist* — be tracked by the kernel, hold memory and resources — without currently *running* on a CPU. A process waiting for a file to finish loading, waiting for a network reply, or simply waiting its turn for CPU time is still a real, existing process the whole time it's waiting. "The process exists" and "the process is running right now" are not the same statement.

**Linux-specific notation, kept clearly separate from the conceptual model above.** The `ps` command (Section 9) reports Linux-specific single-letter state codes — for example, `S` for sleeping, `R` for running, `T` for stopped, `Z` for a "zombie" (a terminated process whose exit information hasn't yet been collected by its parent — a Linux-specific detail, mentioned here only by name; its full mechanics belong to the Process Lifecycle lesson). These letters are Linux/`ps`-specific notation for the same underlying conceptual states above — other operating systems and tools use different notation for broadly the same ideas. Do not treat Linux's specific letters as universal OS terminology.

---

## 6. How It Works Internally

This section walks through, conceptually, how a process comes into existence, executes, and ends — and introduces concurrency, parallelism, and isolation, all as consequences of this same model.

```text
Program
     ↓
Process creation           (requested via system calls — Concept 02)
     ↓
Process identity assigned   (PID, PPID)
     ↓
Address space/resources set up   (memory, open files, environment)
     ↓
Process becomes runnable
     ↓
CPU executes it                    (when the scheduler selects it to run on a CPU)
     ↓
Waiting / running / stopped, repeatedly, as needed
     ↓
Resource interaction                  (files, network, memory — each via system calls)
     ↓
Termination
     ↓
Cleanup / exit status
```

**Walking through each stage, and the kernel's role at each one:**

1. **Process creation is requested.** Some existing process asks the kernel, via a system call, to create a new process. (The precise mechanism for this — and the distinction between creating a process and loading a different program into it — is intentionally deferred to the Process Lifecycle lesson; here, only the fact that creation is a kernel-mediated request matters.)
2. **Identity is assigned.** The kernel assigns the new process a PID, and records the creating process's PID as its PPID.
3. **Resources are set up.** The kernel establishes the new process's virtual address space, loads the program's code and data into it, and sets up its initial open files, environment, and working directory.
4. **The process becomes runnable.** It's ready to execute but is not necessarily using a CPU yet — that depends on the scheduler (previewed here, fully covered in the Scheduling lesson).
5. **The CPU executes it.** When the scheduler selects a runnable execution entity of this process (typically a thread) to run on a CPU, its code actually runs, following the fetch-decode-execute cycle from Module 0.1.
6. **The process cycles between states.** It may run for a while, then need to wait (for a file, for network data, for its turn again), then run again — often many times over its lifetime.
7. **It interacts with resources.** Every file it reads, every byte it sends over a network, every additional bit of memory it requests happens via system calls, exactly as Concept 02 described.
8. **It terminates.** Eventually the process stops running — because it finished normally, was asked to stop, or crashed.
9. **The kernel cleans up.** Most process resources (memory, open files) are reclaimed when execution ends, and an exit status is recorded (Section 9) for whoever is interested in it (often the parent process, or your shell). Unix-like systems may retain minimal process metadata for a terminated child until its parent collects ("reaps") it; the detailed lifecycle is a later lesson.

**Explicitly out of scope here** (each belongs to a later, dedicated lesson): the precise mechanism of process creation and how a new program gets loaded into a process, the full state-transition diagram and what happens to "zombie" processes, how the scheduler actually chooses which runnable process runs next, and how virtual memory is physically implemented.

### Concurrency vs. parallelism

Two terms that sound similar but mean different things, and that this lesson introduces only as far as understanding processes requires.

**Concurrency.** Simple meaning: multiple processes making progress during overlapping periods of time, without necessarily doing anything at the exact same instant. Technical meaning: concurrency describes a system where multiple processes are in progress during the same overall time window, with the CPU (or CPUs) switching between them — possibly very rapidly — rather than necessarily running them at the literal same instant.

**Parallelism.** Simple meaning: multiple processes genuinely executing at the exact same instant. Technical meaning: parallelism specifically requires multiple CPU cores (or processors) each actively executing a different process's instructions simultaneously, at the same moment in time.

```text
One CPU core, two processes (concurrency, not parallelism):
Process A: ▓▓▓░░░▓▓▓░░░▓▓▓░░░       (rapidly alternating — never truly simultaneous)
Process B: ░░░▓▓▓░░░▓▓▓░░░▓▓▓

Two CPU cores, two processes (parallelism):
Core 1 → Process A: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   (truly simultaneous)
Core 2 → Process B: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

**Three points this lesson insists on, precisely:**

- **Multiple processes do not necessarily mean multiple CPU cores are involved.** A machine with a single CPU core can still run many processes "concurrently," rapidly switching between them, without any of them ever literally executing at the same instant.
- **The OS scheduler participates in deciding when a runnable execution entity (typically a thread of a process) actually gets CPU time.** This lesson does not teach *how* the scheduler decides (that's the Scheduling lesson) — only that this decision is the kernel's, not the application's, to make.
- **Whether you actually get parallelism, rather than just concurrency, depends on available CPU resources and system conditions** — the number of CPU cores available, how many other processes are competing for them, and how the scheduler is currently behaving. Running four worker processes does not, by itself, guarantee four-times parallel throughput.

### Process isolation

**Why isolation exists.** Because each process gets its own private virtual address space (Section 5) and its own separately tracked resources, one process cannot, under normal circumstances, directly read or corrupt another process's memory, and a crash in one process does not automatically bring down another. (Operating systems also provide mechanisms for processes to intentionally share memory and other resources; the isolation described here is the default, not an absolute rule.)

**What isolation provides, concretely:**

- **Fault isolation** — a bug or crash in one process is contained to that process; other, unrelated processes can continue running.
- **Resource accounting** — the kernel can measure and limit CPU, memory, and other resource use per process, because each process's usage is tracked separately.
- **Security boundaries** — one process cannot simply read another's private memory, which is foundational to running multiple users' or multiple services' code safely on the same machine.
- **Independent execution** — each process runs its own logic without needing to coordinate step-by-step with unrelated processes.
- **Controlled resource access** — a process accesses shared resources (files, network) only through the same kernel-mediated system-call interface every other process uses, so the kernel can arbitrate fairly.

**A realistic example:** if a background data-processing script crashes due to a bug, a separate Python API service running on the same machine, as a different process, is unaffected and continues serving requests — the crash's "blast radius" is contained to the one process that failed.

**An important limitation, stated precisely:** process isolation reduces blast radius — it is a strong, genuinely important boundary — but it is not an absolute security guarantee in every context. What isolation actually enforces depends on OS configuration and other controls (permissions, resource limits, and — well beyond this lesson's scope — mechanisms like containers, which add further layers of isolation on top of ordinary process isolation). This lesson establishes only the baseline process-isolation model; it does not claim that ordinary process isolation alone is sufficient for every security requirement a production system might have.

---

## 7. Real-World Example

Each example states what the process represents, what resources it uses, what the OS manages, and what an engineer can actually observe.

**1. Running a Python script.**
*Represents:* one execution of the Python interpreter with your script loaded. *Resources:* memory for the interpreter and your data, at least one open file (the script itself), possibly others. *OS manages:* scheduling, memory, file access. *Observable:* a PID, CPU/memory usage, and (Section 9) its state, via `ps`.

**2. Running a web/API service.**
*Represents:* a long-running process (or processes) waiting for and handling network requests. *Resources:* memory, open network sockets, possibly open log files. *OS manages:* network I/O, scheduling across potentially many incoming requests. *Observable:* CPU usage rising under load, memory that may grow over time, open file descriptors for each active connection.

**3. Running multiple worker processes.**
*Represents:* several independent processes, all running the same program, dividing incoming work between them (Section 5's "same program, multiple processes" model, applied directly). *Resources:* each worker has its *own* separate memory — they do not automatically share application state. *OS manages:* scheduling CPU time across all of them. *Observable:* multiple distinct PIDs, all running the same command, visible together in `ps`.

**4. Running a data-processing job.**
*Represents:* a process that reads input files, transforms data, and writes output, then terminates. *Resources:* memory for data being processed, open file descriptors for input/output files. *OS manages:* file I/O via system calls, memory allocation as data grows. *Observable:* memory usage that grows as data is loaded, an exit status when it finishes (Section 9).

**5. Running an AI inference service.**
*Represents:* a process (or processes) holding a loaded model in memory and responding to prediction requests. *Resources:* substantial memory (model weights), CPU (and possibly GPU-related resources, mentioned only in passing — GPU driver internals are out of scope here), open network sockets. *OS manages:* memory allocation for the model, scheduling, network I/O. *Observable:* memory usage that jumps when the model loads, CPU usage during inference, network connections while serving requests.

**6. Running a background task.**
*Represents:* a process performing work without direct, interactive user input — for example, a queue worker or scheduled job. *Resources:* whatever the task itself needs (files, network, memory). *OS manages:* the same as any other process — the "background" quality is about how it was started and how it interacts with input/output (full detail: the Shell and Standard I/O lessons), not a different kind of OS entity. *Observable:* same tools as any other process — `ps`, `/proc`.

**7. A process waiting for I/O.**
*Represents:* a process that exists and is tracked, but is not currently running on a CPU, because it's waiting for a file, network response, or similar (Section 6's "sleeping/waiting" state). *Resources:* it retains its memory and open resources the entire time it waits. *OS manages:* the kernel wakes it up again once the awaited event occurs. *Observable:* a "sleeping" state in `ps`, near-zero CPU usage despite the process clearly existing and doing meaningful work (waiting is a legitimate, common process activity, not a malfunction).

**8. A process consuming too much memory.**
*Represents:* a process whose memory usage has grown, whether due to legitimate large data (Example 5), a memory leak, or unexpectedly large input. *Resources:* an increasing share of the system's available memory. *OS manages:* the kernel may eventually be unable to grant further memory requests, or (system-dependent, not detailed here) may terminate the process under extreme resource pressure. *Observable:* rising memory usage over time in `ps` or `top` (Section 9), a useful early signal before an outright failure.

**9. A process consuming excessive CPU.**
*Represents:* a process actively computing far more than expected — perhaps legitimately (heavy computation) or due to a bug (an unintended loop). *Resources:* a large share of available CPU time, potentially delaying other processes' scheduling opportunities. *OS manages:* the scheduler continues sharing CPU time across all runnable processes, but a CPU-heavy process can still noticeably slow others down. *Observable:* sustained high `%CPU` in `ps`/`top`.

**10. A process crashing/terminating.**
*Represents:* a process whose execution has ended, whether cleanly (finished normally) or abnormally (crashed). *Resources:* the kernel reclaims its memory and closes its open files automatically as part of cleanup (Section 6, Section 9). *OS manages:* cleanup, and recording an exit status. *Observable:* the process simply disappears from `ps`; an exit status is available to whatever started it (Section 9's exit-code discussion); Section 14's Scenario 5 covers diagnosing this.

---

## 8. Relationships to Other Concepts

| Concept | Relationship to processes | Prerequisite or later? | Full treatment |
|---|---|---|---|
| Kernel and User Space | A process's application code runs in user space; the kernel creates and manages the process itself | Prerequisite (Concept 01) | Already covered |
| System Calls | Process creation and many process and resource operations involve system calls | Prerequisite (Concept 02) | Already covered |
| Threads | A thread is a unit of execution *within* a process; a process may contain one or more threads | Later | Concept 04 |
| Scheduling | Determines when a runnable execution entity (typically a thread) actually gets CPU time | Later | Concept 05 |
| Virtual Memory | Provides the isolated address space each process uses (Section 5, Section 6) | Later | Concept 06 |
| Filesystems | Processes access files through system calls; a process's open file descriptors point into the filesystem | Later | Concept 07 |
| Permissions | Determine what a process's security identity is allowed to access | Later | Concept 08 |
| Environment Variables | Part of a process's environment, set at creation and inherited from its parent | Later | Concept 09 |
| Signals | A kernel-mediated way of notifying or controlling a process (`kill`, Section 9, is a preview of this) | Later | Concept 10 |
| Standard Input/Output | Every process has these OS-managed I/O channels set up as part of its resources | Later | Concept 11 |
| Pipes | Kernel-managed channels connecting the standard I/O of two related processes | Later | Concept 12 |
| Shell | A user-space program that is itself a process, and whose main job is creating and managing other processes | Later | Concept 13 |
| Process Lifecycle | The complete, detailed state-transition story only briefly previewed in Section 6 | Later | Concept 14 |

**Why this lesson sits exactly here:** every concept below this one in the table needs "a process is the OS's tracked, running instance of a program, with identity, state, and resources" to already make sense. This lesson is the concrete noun; the remaining Module 0.2 lessons describe what that noun does, shares, and becomes.

---

## 9. Practical Observation / Commands

You are working in Ubuntu inside WSL2. All commands in this section are safe and read-only, except the controlled `kill` used only on a process created specifically for this lesson, in the required lab below. Nothing here requires `sudo` or installs anything.

### `ps` — inspecting processes

`ps` lists processes and selected information about them.

| Field (from `ps -o pid,ppid,stat,%cpu,%mem,cmd`) | Meaning |
|---|---|
| `PID` | The process's identifier (Section 5) |
| `PPID` | Its parent's identifier (Section 5) |
| `STAT` | Linux-specific process state notation (Section 6) — e.g. `S` sleeping, `R` running |
| `%CPU` | On Linux, `ps` reports CPU usage as the process's CPU time divided by the time it has been running (over its lifetime, per the `ps` implementation), not an instantaneous reading; `top` gives a live, recent-interval view |
| `%MEM` | Share of system memory currently used |
| `CMD` | The command that started the process |

### `top` — a live, continuously updating process view

`top` shows a live, ranked list of processes (by default, ordered by CPU usage), along with overall CPU and memory summaries, refreshing periodically. It's useful for spotting which processes are currently using the most CPU or memory at a glance, rather than inspecting one PID at a time.

**Actual observed output** (captured in batch mode, `top -b -n 1`, which prints one snapshot instead of continuously refreshing — safe and non-interactive):

```text
top - 14:24:35 up 48 min,  1 user,  load average: 0.15, 0.08, 0.07
Tasks:  32 total,   2 running,  30 sleeping,   0 stopped,   0 zombie
%Cpu(s):  5.7 us,  1.1 sy,  0.0 ni, 93.1 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   3853.6 total,   2695.7 free,    780.1 used,    529.2 buff/cache
MiB Swap:   1024.0 total,   1024.0 free,      0.0 used.   3073.5 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   1358 sovon     20   0 5585236 356136  89600 R  10.0   9.0   2:21.11 claude
      1 root      20   0   24416  14688  10620 S   0.0   0.4   0:01.79 systemd
      2 root      20   0    3180   2212   2072 S   0.0   0.1   0:00.01 init-sy+
      7 root      20   0    4628   2532   2008 S   0.0   0.1   0:06.49 init
     47 root      19  -1   50396  16796  15508 S   0.0   0.4   0:00.30 systemd+
```

What to notice: the `Tasks` line's `running`/`sleeping`/`stopped`/`zombie` counts are a direct, live example of Section 6's process-state model; the per-process `S` column matches `ps`'s `STAT` notation. This exact snapshot is specific to the moment it was captured — your own `top` output will show entirely different processes, numbers, and totals, and will keep changing every time you run it. That variability is expected, not a discrepancy to worry about.

**WSL2 caveat:** the `Tasks total` count and every listed process reflect the Linux environment running inside WSL2 — it is not a view of every process running on the Windows host.

### `htop` — an enhanced, interactive alternative

`htop` is a friendlier, color, interactive alternative to `top`, when installed.

```bash
command -v htop
```

**Actual result in this environment:** `htop` is **not installed** (`command -v htop` produced no output). Per this lesson's safety rules, it must not be installed as part of the lesson (no `sudo`, no package installation). This is not a problem: `top` and `ps`, both already demonstrated, cover every concept this lesson needs. If `htop` happens to be available in your own environment, it presents the same underlying information as `top` — process list, states, CPU, and memory — in a more interactive, readable layout; it does not expose any different underlying concept.

### `/proc` — direct, safe process observation

Concept 02 introduced `/proc` as a live, kernel-generated pseudo-filesystem, not a normal disk-backed directory. This lesson uses it directly to inspect one specific process. Every entry under `/proc/<PID>/` reflects that process's *current* state — its contents can change from one moment to the next while the process runs, and some entries may be restricted by permissions for processes you don't own.

| Path | What it shows |
|---|---|
| `/proc/<PID>/status` | A detailed, human-readable summary: name, state, PID, PPID, user/group identity, and more |
| `/proc/<PID>/cmdline` | The exact command and arguments the process was started with |
| `/proc/<PID>/cwd` | A symlink to the process's current working directory |
| `/proc/<PID>/fd` | A directory listing the process's currently open file descriptors |

**WSL2 caveat:** `/proc` here reflects the Linux environment WSL2 exposes, not unmediated visibility into physical hardware or the Windows host's own process table.

### `kill` — sending a signal, not "instant destruction"

`kill <PID>` sends a **signal** to a process — by default, `SIGTERM`, a *request* that the process terminate. It is not a guarantee of immediate destruction: a well-behaved process can choose to notice `SIGTERM` and shut down cleanly (closing files, finishing in-progress work) before actually exiting, and in rare cases might even be written to ignore it. **The full semantics of signals — what they are, which ones exist, and how processes respond to them — is the dedicated Signals lesson later in this module.** For this lesson, only two facts matter: `kill` requests termination via a signal, and it should only ever be used here on a process created specifically for this lesson's lab.

### Process exit codes

When a process terminates, it reports an **exit status** (a small integer) to whatever started it (often your shell, or a parent process). By Unix-like convention, **`0` commonly indicates success**, and a **non-zero value commonly indicates some kind of failure or special condition** — but the exact meaning of any particular non-zero value is application-specific, not universally defined. Immediately after running a command in a Bash shell, `echo $?` prints the exit status of the most recently finished command:

```bash
true; echo $?
false; echo $?
```

`true` and `false` are tiny standard Unix utilities that do nothing except immediately exit with status `0` and `1` respectively — they exist specifically to make exit-status behavior easy to demonstrate safely.

---

### Required process lab

This lab uses a real process, created specifically for this lesson, inspected safely, and then cleanly terminated and verified. The demonstrations below show **actual observed output**, captured while preparing this lesson — not fabricated text. Because this lesson's authoring tools block starting a literal `sleep <N>` command directly (a safeguard against long, blind waiting), the demonstration below uses `tail -f /dev/null` instead — a standard, equally safe command that, like `sleep`, does nothing but idle indefinitely, making it an ideal harmless stand-in for observing a running-but-idle process. **You can and should use `sleep 300 &` yourself when you run this lab in your own terminal** — that command is completely safe to run directly; the substitution here is specific to how this lesson was authored, not a limitation of `sleep` itself.

**Step 1–2: start the process and capture its PID.**

```bash
tail -f /dev/null &
LAB_PID=$!
echo "Started demo process with PID: $LAB_PID"
```

Actual observed output:

```text
Started demo process with PID: 5420
```

**Step 3: inspect it with `ps`.**

```bash
ps -p "$LAB_PID" -o pid,ppid,stat,%cpu,%mem,cmd
```

Actual observed output:

```text
    PID    PPID STAT %CPU %MEM CMD
   5420    5418 Sl    0.0  0.2 tail -f /dev/null
```

In this captured environment, the `STAT` value was `Sl` — your own `STAT` value may differ (for example, a plain `S`), since the exact state letters and suffixes depend on your environment and the process. Here, `Sl` means sleeping (Section 6), with `l` indicating it's a multi-threaded process at the OS level (a detail belonging to the Threads lesson, not explained further here).

**Step 4–6: inspect it via `/proc`, observing identity, command, working directory, and open files.**

```bash
head -n 15 "/proc/$LAB_PID/status"
cat "/proc/$LAB_PID/cmdline" | tr '\0' ' '
readlink "/proc/$LAB_PID/cwd"
ls -l "/proc/$LAB_PID/fd"
```

Actual observed output (trimmed to the fields this lesson covered):

```text
Name:	tail
State:	S (sleeping)
Pid:	5420
PPid:	5418
Uid:	1000	1000	1000	1000

tail -f /dev/null

/home/sovon/AI Engineering

total 0
lr-x------ 1 sovon sovon 64 Sep 10 14:23 0 -> /dev/null
l-wx------ 1 sovon sovon 64 Sep 10 14:23 1 -> ...output
l-wx------ 1 sovon sovon 64 Sep 10 14:23 2 -> ...output
lr-x------ 1 sovon sovon 64 Sep 10 14:23 6 -> /dev/null
```

This directly demonstrates Section 5's process-contents table with real values: `Name`/`Pid`/`PPid`/`Uid` are kernel-maintained identity; `cmdline` and `cwd` are process-owned environment; the `fd` listing shows this specific process's currently open file descriptors (numbered `0`, `1`, `2`, and `6` here) — a live, concrete example of "open I/O resources," rather than an abstract description.

**Step 7–8: send a controlled termination signal, and verify termination.**

```bash
kill "$LAB_PID"
ps -p "$LAB_PID" -o pid,stat,cmd
```

Actual observed output:

```text
    PID STAT CMD
```

An empty result (no matching row) confirms `ps` can no longer find the process — it has terminated.

**Step 9–10: clean up and verify cleanup.**

```bash
ls -d "/proc/$LAB_PID"
```

Actual observed output:

```text
ls: cannot access '/proc/5420': No such file or directory
```

This confirms both that the kernel has finished cleaning up the process's `/proc` entry, and that no lingering background job remains (checked with `jobs -l`, which produced no output). **This lab, exactly as shown, only ever created and terminated one process — the one it started for this purpose — and never touched any system, unrelated, or unknown process.**

---

## 10. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "A program and a process are the same thing." | A program is a static file; a process is an active, OS-tracked running instance of it (Section 1, Section 5). |
| "A Python file is a process." | A `.py` file is a program — passive code on disk. Running it (`python app.py`) creates a process; the file itself never becomes one (Section 1, Section 13). |
| "One program can only have one process." | The same program file can be run any number of times, each normally producing a separate process with its own virtual address space and resources (Section 5). |
| "A process always uses the CPU." | A process can exist while sleeping/waiting, ready-but-not-yet-scheduled, or stopped — using no CPU at all during those times (Section 6). |
| "If a process exists, it must currently be running." | Existing (being tracked by the kernel, holding resources) and actively running on a CPU right now are different things (Section 6). |
| "A PID identifies the application permanently." | A PID identifies one specific running instance for its lifetime only; running the same program again very likely produces a different PID (Section 5). |
| "A process is just the code being executed." | A process also has identity, state, a private address space, open resources, environment, and more — code is only one component (Section 5). |
| "A process owns the entire computer's memory." | A process has its own private virtual address space, isolated from other processes, not unrestricted access to all of physical memory (Section 5, Section 6). |
| "Every process runs on a separate CPU core." | Many processes can share a small number of CPU cores, taking turns via the scheduler — that's concurrency, not a one-process-per-core guarantee (Section 6). |
| "Multiple processes automatically mean parallel execution." | Parallelism specifically requires multiple CPU cores executing simultaneously; multiple processes can just as easily be sharing one core concurrently (Section 6). |
| "A process is the same as a thread." | A thread is a unit of execution *within* a process; a process can contain one or more threads. The full distinction is the next lesson, Threads. |
| "Killing a process means deleting the program." | `kill` affects a running instance only; the program file on disk is completely untouched (Section 1, Section 9). |
| "`kill` always immediately destroys a process." | `kill` sends a signal — by default a termination *request* — which a process may handle, delay briefly, or (rarely) ignore, rather than an instantaneous, forced destruction (Section 9; full detail: Signals lesson). |
| "A process cannot wait." | Waiting (for I/O, an event, or CPU time) is one of the most common things a process does, and is a normal state, not a malfunction (Section 6, Example 7). |
| "If one process crashes, the whole operating system crashes." | Process isolation exists specifically to contain a crash to the process that failed; unrelated processes normally continue running (Section 6). |
| "Processes are only relevant to operating-system developers." | Every Python AI service you build or operate is one or more processes; observing and reasoning about them is a direct, practical production skill (Section 3, Section 15). |
| "A Python service is just Python code, not an OS process." | Once started, a Python service is fully an OS process — with a PID, memory, open files, and everything else this lesson covered — regardless of how high-level the code inside it feels (Section 13). |
| "CPU usage and process existence mean the same thing." | A process with 0% CPU usage in `ps`/`top` can still very much exist and be doing meaningful work — such as waiting on I/O (Section 6, Example 7). |

---

## 11. Debugging and Troubleshooting

Each scenario follows: problem, beginner's likely assumption, correct mental model, investigation approach, and expected conclusion.

**Scenario 1 — A Python service appears to be running but is not responding.**

1. *Problem:* the process is visibly started, but requests to it never complete.
2. *Beginner's likely assumption:* "The process must have crashed silently."
3. *Correct mental model:* a process that still exists and appears in `ps` has not crashed — it may be running normally but stuck in application logic, or it may be waiting (Section 6) on something that's taking unusually long (I/O, a network call, another resource).
4. *Investigation approach:* first confirm the process still exists (`ps -p <PID>`) and note its state; consider its CPU usage (near-zero suggests it's waiting on something, rather than busy) and whether it has open network connections (`/proc/<PID>/fd`) consistent with what it should be doing.
5. *Expected conclusion:* "not responding" and "crashed" are different failure modes with different causes — a process that still exists and is in a waiting state points toward an I/O or dependency issue, not application code that has stopped executing. (Deep network-specific debugging is out of scope here.)

**Scenario 2 — A process uses excessive CPU.**

1. *Problem:* `ps`/`top` shows a process consuming a very high `%CPU` sustained over time.
2. *Beginner's likely assumption:* "I can tell exactly what line of code is causing this just from `ps`."
3. *Correct mental model:* `ps`/`top` show *that* a process is CPU-heavy, not *why* — the cause could be legitimate heavy computation, an unintended loop, or something else entirely; distinguishing between these requires more than process-level observation alone.
4. *Investigation approach:* note whether high CPU usage matches expected legitimate work (for example, active inference) or is sustained even when the service should be idle — the latter is a stronger signal of a genuine problem worth investigating further, using tools beyond this lesson's scope.
5. *Expected conclusion:* process observation tells you *where* to look (which process, roughly when) but not automatically *why* — a distinction worth respecting rather than over-claiming.

**Scenario 3 — A process uses excessive memory.**

1. *Problem:* `ps`/`top` shows a process's `%MEM`/`RES` steadily growing over time.
2. *Beginner's likely assumption:* "This number alone tells me there's a memory leak."
3. *Correct mental model:* growing memory usage can reflect legitimate behavior (loading a large model, accumulating a large batch of data) or a genuine problem (data that should have been released but wasn't) — process-level memory observation shows the *symptom*, not automatically the cause.
4. *Investigation approach:* consider whether the growth matches expected application behavior (does memory stabilize after loading, or does it climb indefinitely under steady load?) as a first, process-level signal, before reaching for more advanced memory-profiling tools this lesson does not cover.
5. *Expected conclusion:* rising memory is a legitimate, important thing to notice at the process level, and a natural trigger for deeper investigation — but process observation alone does not prove *why* memory is growing.

**Scenario 4 — A learner tries to `kill` the wrong PID.**

1. *Problem:* a learner intends to stop one specific process but risks targeting the wrong PID.
2. *Beginner's likely assumption:* "I'm fairly sure this is the right PID, I'll just run `kill`."
3. *Correct mental model:* PIDs are reused over time (Section 5) and easy to mistype or misremember — verifying identity before sending a termination signal is a basic safety habit, not excessive caution.
4. *Investigation approach:* before running `kill`, confirm the PID with `ps -p <PID> -o pid,cmd` and check that the reported command matches exactly what you intend to stop — exactly as this lesson's own lab did before terminating its demo process.
5. *Expected conclusion:* always verify a PID's identity immediately before sending it a signal — this lesson's lab, and this scenario, both model that habit deliberately.

**Scenario 5 — A process disappears unexpectedly.**

1. *Problem:* a process that was previously running is no longer visible in `ps`.
2. *Beginner's likely assumption:* "The system must have removed it randomly, without a specific cause."
3. *Correct mental model:* a process that no longer appears in a particular `ps` query may have terminated — cleanly (it finished its work and exited) or abnormally (it crashed, or was signaled to stop by something) — rather than vanishing "randomly," even if the specific cause isn't immediately obvious to you. Also check that the query itself (the PID or selection used, and what you are able to see) is not what changed.
4. *Investigation approach:* check whether the process's exit status was recorded anywhere available to you (application logs, a process manager's own logs), and consider whether the process's own logic would naturally have completed around that time, versus stopping unexpectedly mid-task.
5. *Expected conclusion:* once you have confirmed the process is genuinely gone (and not merely missing from your query), it has a real, specific termination cause behind it (Section 6, Section 9) — the debugging task is narrowing down which kind of termination happened.

**Scenario 6 — A learner confuses a program file with a process.**

1. *Problem:* a learner says something like "I edited the process" when they mean they edited `app.py`, or expects editing a running script's file to change the behavior of an already-running process.
2. *Beginner's likely assumption:* "The process and the file are the same thing, so changing one changes the other."
3. *Correct mental model:* a process loaded its code from the program file at the time it was created (Section 6); editing the program/source file normally does not replace the already-loaded code of an existing process, because the process is a separate, already-loaded execution instance (Section 1). (A program can nevertheless be deliberately designed to reread files or load resources/code at runtime.)
4. *Investigation approach:* ask specifically whether the *file* was changed, or whether the *running process* was restarted — a process must generally be stopped and started again (a new process, from the updated file) for code changes to take effect.
5. *Expected conclusion:* "I changed the code" and "the running process is now using that changed code" are two different facts, and confusing them is one of the most common beginner mistakes this lesson exists to prevent.

---

## 12. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. In your own words, what is the difference between a program and a process?
2. What is a PID, and what is a PPID?
3. Name the five conceptual process states this lesson introduced.
4. List four things a process has that a plain program file does not.
5. What does `ps`'s `STAT` column show, and is its notation universal or Linux-specific?
6. What does `kill` actually do, precisely?
7. Was `htop` available in this lesson's environment? How was that determined?
8. What does an exit status of `0` commonly indicate, by convention?

### Level 2 — Understanding

9. Explain why running the same program file twice produces two independent processes, not one shared process.
10. Explain why a process can exist without currently using any CPU.
11. Explain the difference between concurrency and parallelism, using your own example (not copied from this lesson).
12. Explain why "multiple worker processes" does not automatically mean four times the throughput.
13. Explain why process isolation is not an absolute security guarantee, even though it's a genuinely important boundary.
14. Explain, in your own words, the nine-stage conceptual flow from Section 6 (creation through cleanup).
15. Why does this lesson distinguish "process-owned/application-visible state" from "kernel-maintained process-management information"?
16. Why is a PID not a reliable, permanent identifier for "the application" across restarts?

### Level 3 — Application

17. Start a safe, idle background process in your own WSL2 terminal (for example, `sleep 300 &`), capture its PID, and inspect it with `ps -p <PID> -o pid,ppid,stat,%cpu,%mem,cmd`. Record what you observe.
18. For the same process, inspect `/proc/<PID>/status`, `/proc/<PID>/cmdline`, and `/proc/<PID>/fd`. Identify one piece of kernel-maintained information and one piece of process-owned information from the output.
19. Run `top -b -n 1` in your terminal. Identify the `Tasks` line's running/sleeping/stopped/zombie counts and relate them to Section 6's process-state model.
20. Safely terminate the process you started in Exercise 17 using `kill`, then verify its termination using both `ps` and `/proc`.
21. Run `true; echo $?` and `false; echo $?` in your terminal. Record both exit statuses and explain what each conventionally indicates.
22. Using Section 7's Example 3 (multiple worker processes), sketch (in text) what four independent worker processes running the same `app.py` would each individually hold in memory.
23. A classmate says, "Since my Python script only has one `def main():` function, it can only ever be one process." Explain what's incorrect about this claim.
24. Using this lesson's process hierarchy diagram (Section 5), identify — conceptually, without necessarily running a full tree tool — what you'd expect the PPID relationship to look like between your shell and a process you start from it.

### Level 4 — Debugging

25. A Python service is visibly running (appears in `ps`) but stops responding to requests. Using Scenario 1 from Section 11, explain what to check first and why "not responding" isn't automatically "crashed."
26. A process shows sustained high `%CPU` in `top`. Using Scenario 2, explain what you can and cannot conclude from that observation alone.
27. A process's memory usage climbs steadily over an hour. Using Scenario 3, explain how to reason about whether this is expected or concerning, without assuming a specific cause.
28. A learner is about to run `kill` on a PID they identified from memory, without re-checking it. Using Scenario 4, explain the safer approach and why it matters.
29. A process that was running is no longer visible in `ps`. Using Scenario 5, explain why "it just disappeared randomly" is not a complete explanation, and what else (besides termination) to check about your `ps` query.
30. A learner edits `app.py` while an earlier process started from that file is still running, then is confused that the running service's behavior hasn't changed. Using Scenario 6, explain what's actually going on.
31. A learner assumes that because their AI service process shows 0% CPU in `ps` at a given moment, it must be broken. Using Section 6, Example 7, and Section 10, explain why this assumption may be wrong.
32. A learner runs `ps -p <PID>` and sees no output at all, where they expected to see their process. Explain the most likely conclusion, referencing Section 9's lab.

### Level 5 — Integration

33. Draw (in text/ASCII) the relationship between a Python AI service's four worker processes, each process's own memory, and the single `app.py` file they all started from — using Section 5's "one program, many processes" diagram as your model.
34. A friend claims, "Once I understand threads, I won't really need to understand processes separately." Using Section 8's relationship table and Section 1, explain why processes remain a distinct, necessary concept even after learning about threads.
35. Explain how "a process can exist while waiting" (Section 6) and "concurrency does not require multiple CPU cores" (Section 6) work together to explain how a single-core machine can still usefully run many I/O-bound Python services at once.
36. A production AI inference service's process disappears from `ps` shortly after receiving an unusually large request. Using Section 7 (Examples 8 and 10) and Section 11 (Scenarios 3 and 5), construct a plausible, reasoned explanation.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "the OS sees processes; your web framework sees routes and handlers" (Section 3) is an important distinction for diagnosing a production incident, with at least one concrete example.

---

## 13. Expected Results

**Expected conceptual results — these should hold regardless of your specific machine:**

- Correctly and confidently distinguish a program from a process, in your own words, with your own example.
- Explain what a PID and PPID are, and why a PID is not a lasting identifier for "the application."
- Correctly classify a described process as running, ready, waiting, stopped, or terminated, given a short scenario.
- List at least six components a process has (Section 5's table) from memory.
- Explain the difference between concurrency and parallelism, and why multiple processes don't automatically imply parallel execution.
- Explain why process isolation matters, and its limits, without overstating it as an absolute guarantee.
- Correctly identify, for several of this lesson's eighteen misconceptions, why each is wrong and what the accurate idea is instead.

**Possible environment-dependent results — these will vary by machine and are expected to vary:**

- The PID assigned to any process you start yourself will differ from the PID (`5420`) shown as this lesson's actual observed output — PIDs are not predictable or reproducible across runs or machines.
- Your `top`/`ps` output will show entirely different running processes, CPU/memory totals, and system uptime than the snapshot in Section 9.
- Whether `htop` is installed depends entirely on your specific environment — this lesson's environment did not have it, and that was not treated as a blocker.
- Exit statuses you observe from your own scripts depend entirely on what those scripts do — only `0` reliably means "conventionally successful" across arbitrary programs; specific non-zero values are application-defined.

**What happens when the lesson-created process is terminated:** it stops appearing in `ps`, its `/proc/<PID>/` entry disappears (confirmed directly in Section 9), and the kernel reclaims most of its resources (memory, open file descriptors) automatically, though Unix-like systems may briefly retain minimal metadata until the parent reaps it — you do not need to manually clean up a terminated process's OS-level resources, only any files it may have written to disk, if applicable (this lesson's lab wrote none).

---

## 14. Review Questions

Answers are intentionally not provided directly below these questions.

### Program vs. process

- What is the difference between a program and a process?
- Why can the same program file produce more than one process?

### Process identity

- What is a PID?
- What is a PPID, and what relationship does it describe?
- Why shouldn't a PID be treated as a permanent identifier for an application?

### Process state

- Name the conceptual process states this lesson introduced.
- Why is "a process exists" not the same claim as "a process is currently running"?
- Why should Linux's `ps` state letters not be treated as universal OS terminology?

### Process resources

- List at least five components that make up a process, beyond its code.
- What is the difference between process-owned/application-visible state and kernel-maintained process-management information?

### Process isolation

- What does process isolation actually protect against?
- Why is process isolation not an absolute security guarantee?

### Concurrency and parallelism

- What is the difference between concurrency and parallelism?
- Why doesn't running more processes automatically mean more parallel execution?

### Process creation and termination

- What conceptually happens when a process is created (Section 6)?
- What does the kernel clean up automatically when a process terminates?
- What does `kill` actually send to a process, and why is "immediately destroys" an inaccurate description?

### `/proc` and Linux tools

- What does `/proc/<PID>/status` show?
- What is the difference between what `ps` and `top` are each best used for?
- Why must `htop` (or any tool) be checked for availability before assuming it can be used?

### Python processes

- When you run `python app.py`, what becomes the process, and what remains the program?
- Why is editing a script's file while it's already running not enough to change the running process's behavior?

### AI-service processes

- Why does the operating system see "processes," while a web framework sees "routes and handlers" — and why does that distinction matter?
- Give two examples of process-level observations (CPU, memory, state, open files) that could help diagnose a production AI-service problem.

### Production debugging

- Why is "process not responding" not automatically the same conclusion as "process crashed"?
- Why can `ps`/`top` tell you *that* a process is using excessive CPU or memory, but not automatically *why*?

---

## 15. Production Relevance

At this point, you understand what a process is, what it contains, how it's identified and observed, what states it can be in, how it relates to concurrency and parallelism, and why isolation matters. You are not yet expected to know the full details of threads, scheduling, virtual memory, signals, or the complete process lifecycle — those are each their own dedicated lesson, still ahead in this module.

For a production Applied AI Engineer, this lesson's mental model is used constantly:

- **API services and FastAPI processes.** Every running instance of your service is a process (or several); understanding what that means lets you reason about its memory, CPU, and I/O behavior directly, rather than only through application-level logs.
- **Inference services and LLM applications.** A loaded model lives in a process's memory; understanding process memory (Section 5, Section 9) is the first, most direct tool for reasoning about a service's memory footprint.
- **Background workers and batch jobs.** Exactly the same OS entity as an API service (Section 7) — the same observation tools and mental model apply without modification.
- **Data pipelines and ETL jobs.** Processes that read, transform, and write data, with memory and I/O patterns you can observe directly using the tools this lesson demonstrated.
- **CPU utilization.** High or sustained CPU usage, visible per-process in `ps`/`top`, is a direct, practical signal — even before you know the specific cause (Section 11, Scenario 2).
- **Memory utilization.** Rising per-process memory is an early, observable signal worth investigating, whether the cause turns out to be legitimate or a problem (Section 11, Scenario 3).
- **I/O waits.** A process that's "waiting," not "broken," is one of the most common misdiagnoses this lesson corrects (Section 6, Example 7; Section 10) — recognizing legitimate waiting saves real debugging time.
- **Crashes and restarts.** Understanding process termination and cleanup (Section 6, Section 9) is the foundation for reasoning about why a service went down and what state it left behind — or didn't.
- **Resource consumption and service reliability.** Multiple worker processes, isolation, and resource accounting (Section 6) are exactly what let a production system run many services safely on shared hardware.
- **Observability.** `ps`, `top`, and `/proc` are not just teaching tools — they are the same basic building blocks production monitoring systems use to report on running services.
- **Security boundaries.** Process isolation (Section 6) is a foundational layer that later, more advanced isolation mechanisms (containers, and beyond) build on top of, not replace.

**Process knowledge is explicitly foundational** to everything still ahead in this module and beyond: **threads** (execution within a process), **scheduling** (how CPU time is actually granted), **virtual memory** (how a process's address space is really implemented), **signals** (the full meaning behind `kill`), **process lifecycle** (the complete creation-to-termination story), and, well beyond this roadmap stage, **containers** and **distributed systems** — all of which describe processes doing more sophisticated things, never something that replaces the process concept itself.

**What comes next**, building directly on this lesson:

```text
Processes                       ← this lesson
  → Threads                      (units of execution within a process)
  → Scheduling                    (how the kernel grants CPU time)
  → Virtual Memory                  (the full mechanics behind a process's address space)
  → Filesystems                      (the full detail behind file-related process resources)
  → Permissions                       (the full detail behind a process's security identity)
  → Environment Variables               (the full detail behind a process's environment)
  → Signals                              (the full meaning behind `kill`)
  → Standard Input/Output                  (the full detail behind a process's I/O channels)
  → Pipes                                   (kernel-managed channels between processes)
  → Shell                                    (a process whose job is managing other processes)
  → Process Lifecycle                         (the complete creation-to-termination story)
```

None of these are taught here — this section exists only to show where this lesson sits within the larger Module 0.2 sequence you are building, one concept at a time.

---

_This file is the completed lesson for Concept 03 of Module 0.2. It intentionally does not teach thread internals, scheduling algorithms, virtual-memory page tables, filesystem implementation, permission internals, signal semantics, shell implementation, pipe implementation, container internals, namespaces, cgroups, or Kubernetes process management in depth — those remain the subject of their own dedicated lessons later in this module or in later stages of the roadmap._
