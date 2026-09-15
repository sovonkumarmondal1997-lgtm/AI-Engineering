# Concept 16 — Processes — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../16-processes.md`](../16-processes.md), Section 15. Attempt every question yourself first,
> with your own worked reasoning, before reading any answer below.

---

## Level 1 — Recognition

**1. What is a program?** Stored instructions/code — a general label for "the thing that gets
run" (source code or a compiled executable).

**2. What is an executable?** A file containing, typically, native machine code that the
operating system can load and run directly.

**3. What is a process?** A running instance of a program with an execution context and
associated resources managed by the operating system.

**4. What is a PID?** Process ID — a unique identifying number the operating system assigns to
each process while it exists.

**5. What is a CPU core, as distinct from a process?** A CPU core is hardware capable of
executing instructions; a process is software execution context — a running instance a core may
execute at a given moment.

**6. What is a thread?** An execution path within a process; a process may contain one or more
threads.

**7. The five process states.** New, Ready, Running, Waiting/blocked, Terminated.

**8. Three examples of process resources.** Any three of: memory, files, input/output, CPU time,
devices (via OS mechanisms).

---

## Level 2 — Understanding

**9. Why is a process more than just "a program that is running"?** Because that phrase makes it
sound like a simple label, when in reality a process is an actively-constructed bundle of
execution context (Section 6) and associated resources (Section 7), managed by the operating
system — it has identity (a PID), memory, state, and resources that the OS actively tracks and
maintains.

**10. Why does a process need a PID rather than being identified by program name alone?**
Because multiple processes can share the exact same program name (the same program launched
multiple times, Section 2's concrete example) — a name alone cannot distinguish between them,
while a PID uniquely identifies one specific running instance.

**11. What does a process's memory conceptually consist of?** Commonly-described regions: code
(machine-code instructions), data (initialized program data), stack (function-call tracking and
short-lived local values), and heap (more dynamically-requested data) — a conceptual vocabulary,
not one single universal layout.

**12. What are a process's resources, and why doesn't a process "own" them outright?** Memory,
files, I/O, CPU time, and devices (via OS mechanisms) — a process *uses* these under
operating-system management; it doesn't exclusively, permanently own them, since other processes
share the same underlying hardware and the OS oversees allocation (Section 7's explicit
correction).

**13. Describe the basic process lifecycle.** A process is created (New), becomes Ready to run,
enters Running when actually executing on a CPU core, may move to Waiting/blocked when it needs
something external, cycles back to Ready and Running potentially many times, and eventually
reaches Terminated when it finishes (Section 8).

**14. Why can a process exist without currently executing on a CPU core?** Because it can be in
the Waiting/blocked state (Section 8, Section 9) — for example, waiting on file or network I/O
(Concept 15) — during which it still exists, is still tracked by the OS, but is not actively
executing instructions.

**15. Why is a process different from a CPU core?** A process is software (execution context and
resources); a CPU core is hardware (a physical execution unit, Concept 3). A core can execute
different processes' instructions at different times or in parallel with other cores; it is not
itself a process (Section 11).

**16. Why is a process different from a thread?** A process is the broader
execution/resource boundary with its own memory space and PID; a thread is an execution path
within a process, generally sharing that process's memory and resources rather than having its
own separate identity (Section 12).

---

## Level 3 — Application

**17. Exercise A — Same script run twice, two terminal windows.** Two processes result. Each
launch of the program creates a new, independent process with its own PID and execution context
(Section 2's required concrete example: "one program, launched twice, potentially two separate
processes") — even though both originate from the identical executable file.

**18. Exercise B — Process reading a large file from slow storage.** The process is most likely in
the **Waiting/blocked** state while the read is in progress — it cannot proceed with whatever
comes next until the data arrives from the slower storage device (Concept 12), directly matching
Section 9's "waiting for file I/O" example.

**19. Exercise C — Server process waiting for a client request.** The server process is in the
**Waiting/blocked** state — it cannot proceed until the expected network input arrives (Section 9's
"waiting for network I/O" example, directly recalling Concept 15).

**20. Exercise D — 4 CPU cores, 10 runnable processes — can all 10 execute in parallel at the
same instant?** No. Only up to 4 processes can genuinely execute at the exact same instant, one
per core (Section 10, Section 11) — the remaining 6 processes, even if "Ready," must wait their
turn (concurrency, taking turns on the available cores over time) rather than all executing in
true parallel simultaneously.

**21. Exercise E — AI inference process reading a checkpoint, loading it, using the GPU.**

- Reading the checkpoint from storage: a **resource use** (file/storage I/O, Section 7; Concept
  11, Concept 14) — the process is likely in the **Waiting/blocked** state during the actual read.
- Loading it into memory: the checkpoint's data becomes part of the process's **memory** (Section
  5, Concept 10) — the process is Running (or transitioning through Ready/Running) as this
  proceeds.
- Using the GPU to compute a result: the process is **Running**, using GPU as one of its resources
  (Section 7, Concept 13) — its **execution context** (Section 6) reflects this active computation.

---

## Level 4 — Debugging

**22. "The program file exists on disk, so why isn't there a process for it?"** What's missing:
a program file existing on storage (Concept 14) does not automatically mean a process is running
from it — a process only comes into existence when the program is actually *launched* (Section
13's creation step). A stored, unlaunched executable is not a process (Section 2's comparison
table, Misconception 1).

**23. A process exists but CPU usage is reported as near zero — at least two explanations.**
(1) The process is currently in the **Waiting/blocked** state (Section 8, Section 9) — for
example, waiting on file or network I/O — and therefore isn't consuming CPU time right now, even
though it exists. (2) The process may simply be idle/inactive by design (e.g., waiting for a rare
event) without necessarily being blocked on I/O specifically — either way, near-zero CPU usage
does not imply anything is broken (Misconception 4, Misconception 14).

**24. Two processes with the identical program name in `ps aux` — how is this possible, and how
to tell them apart?** This is possible because the same program can be launched multiple times,
producing multiple independent processes (Section 2's concrete example) — each has its own
distinct PID (Section 4), which is exactly how you'd tell them apart, even though their program
name/command column looks identical (Misconception 13).

**25. A process is Waiting/blocked, and a user assumes it has crashed.** This assumption is not
necessarily correct: Waiting/blocked is a normal, active, distinct state (Section 8) — the process
still exists and is still tracked by the OS; it will resume once whatever it's waiting on
completes. This lesson's own genuinely observed `sleep` example (state `S`, sleeping) demonstrated
exactly this — waiting, not crashed or terminated (Misconception 12).

**26. A user assumes a process permanently owns a CPU core once it starts running.** This is
incorrect: a process may be given a core's execution time temporarily, taking turns with other
processes (Section 10, Section 11's explicit correction, Misconception 6) — it does not
permanently, exclusively claim the core simply by running.

**27. A user sees multiple processes in `ps aux` and assumes they're all executing in parallel
right now.** This assumption requires more information: "existing at the same time" (all being
listed by `ps`) does not necessarily mean "all executing at the exact same instant" (Section 10's
required, central correction, Misconception 7) — whether genuine parallelism is happening depends
on how many CPU cores are available and how many of those processes are actually in the Running
state at that exact instant, which a simple process listing alone doesn't reveal.

**28. A user confuses a process's PID with its executable/program name.** This is imprecise: a
PID identifies one specific running instance; the program name/executable identifies the
underlying stored code, which can be shared by many different processes (Section 4's explicit
correction, Misconception 13) — the two are not interchangeable identifiers.

**29. "This process has multiple threads, so it must actually be multiple processes."** This is
incorrect: a process may contain one or more threads (Section 12) — multiple threads within one
process still share that same process's single memory space and single PID; having multiple
threads does not turn it into multiple separate processes (Misconception 9).

---

## Level 5 — Integration / AI Engineering

### Scenario A — AI inference process, model checkpoint, GPU, log file

**30.** Trace: the process is created (**New → Ready**) when launched. It reads the checkpoint
file from storage — during this read, it is likely **Waiting/blocked** (Section 9, "waiting for
file I/O"), using its **files resource** (Section 7, Concept 14) and depending on the storage
device's characteristics (Concept 11, Concept 12). Once data arrives, it becomes **Ready**, then
**Running**, loading the checkpoint data into its **memory** (Section 5, Concept 10). It continues
**Running** while using the **GPU resource** (Section 7, Concept 13) to compute the result. Writing
the result to a log file involves another brief **Waiting/blocked** period for that file I/O
(Concept 14), before the process eventually reaches **Terminated** once finished (Section 8,
Section 13).

### Scenario B — AI application waiting for network input

**31.** The process is in the **Waiting/blocked** state (Section 8, Section 9's "waiting for
network I/O" example, directly recalling Concept 15). Its CPU usage during this time drops to
near zero (or is reported as idle) — it is not executing any instructions on a CPU core while
genuinely waiting for the network request to arrive, consistent with Section 9's central,
required point that a process can exist without currently executing.

### Scenario C — Worker process alternating CPU and GPU work

**32.** A single process's **execution context** (Section 6) and **resources** (Section 7) are
not limited to just one kind of processing hardware — the same process can, over the course of its
execution, use the CPU (Concept 2) for some steps (e.g., data preparation) and the GPU (Concept 13)
for others (e.g., heavy computation), because "resources" (Section 7's comparison table explicitly
lists both CPU time and, implicitly through general devices, GPU access) describes *what the
process uses*, not a fixed, single-hardware-type limitation. The process remains one single running
instance throughout, simply using different resources at different points in its execution.

### Scenario D — Three AI-related processes, 2 CPU cores

**33.** With only 2 CPU cores and 3 processes (API server, inference worker, logging), not all
three can be executing in parallel at the exact same instant (Section 10, Section 11) — at most 2
can genuinely run simultaneously, one per core, while the third must wait its turn (concurrency).
Whether all three are making progress "at the same time" in the broader, concurrent sense is
possible and likely (each gets turns over time) — but true parallel execution of all three at one
exact instant is not possible with only 2 cores available, directly illustrating Section 10's
required concurrency-vs-parallelism distinction in a concrete AI-system scenario.

### Scenario E — Process consuming memory while waiting for I/O

**34.** Using Section 5, Section 7, and Section 9: the process's **memory** (Section 5) — the
large dataset it loaded into RAM — remains part of its resource allocation (Section 7) regardless
of what execution state (Section 8) the process is currently in. Being in the **Waiting/blocked**
state (Section 9) affects whether the process is *executing on a CPU core*, not whether it
continues to hold its allocated memory resources — the operating system does not automatically
reclaim a waiting process's memory simply because it's temporarily not running; the memory remains
associated with that process's execution context until the process itself either releases it or
terminates (Section 13), directly illustrating that "not currently running" and "not consuming
resources" are two entirely different things (Misconception 10, Misconception 14).

---

_This answer key covers Concept 16 (Processes) only. It does not contain, reference, or anticipate
answers for Concept 17 (What Happens When a Program Starts), Concept 18 (What Happens When a
Function Executes), Concept 19 (Why RAM and Storage Are Different), Concept 20 (Why GPUs Matter
for AI), or any later concept._
