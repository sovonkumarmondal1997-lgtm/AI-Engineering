# Concept 17 — What Happens When a Program Starts — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../17-what-happens-when-a-program-starts.md`](../17-what-happens-when-a-program-starts.md),
> Section 15. Attempt every question yourself first, with your own worked reasoning, before
> reading any answer below.

---

## Level 1 — Recognition

**1. What is a program?** A general label for stored instructions/code — source code or a
compiled executable — that defines what should happen when run.

**2. What is an executable?** A file containing, typically, native machine code, ready for the
operating system to load and run directly.

**3. What is a process?** A running instance of a program, with execution context and resources,
managed by the operating system (Concept 16).

**4. What is a launch request?** A request — from a user or another program — that a specific
program should be started.

**5. What is a loader?** The conceptual mechanism (part of the operating system's responsibility)
responsible for preparing an executable so it can actually be executed by a process.

**6. What is an address space?** The memory a process uses to hold its code, data, stack, and
heap.

**7. What is an entry point?** The specific location in an executable's code where the CPU begins
executing instructions when the process starts.

**8. What is runtime initialization?** Startup code — running at or after the entry point — that
prepares the execution environment before the programmer's application-level logic (e.g., `main`)
begins.

**9. What is a command-line argument?** A value provided when the program was launched, commonly
following the program's name on a command line.

**10. What is an environment variable?** A named, configuration-style value made available to a
process's environment at startup, independent of command-line arguments.

---

## Level 2 — Understanding

**11. Why is a program file not a process?** A program file is stored, inert data; a process is a
running instance with execution context and resources that only comes into existence once the
program is actually launched (Section 1, Section 2).

**12. Why does process creation occur during startup?** Because the operating system must
establish a new, uniquely-identified running instance (with a PID, Concept 16) before any
execution related to that specific launch can happen — this is the concrete first step that turns
a launch request into something the OS can actually manage (Section 4).

**13. Why is executable loading necessary?** Because the executable is just stored data on
storage until its contents are made available within the process's actual execution
environment/address space — without loading, there would be nothing for the CPU to fetch and
execute (Section 5).

**14. Why does the process need an address space?** To hold its code, data, stack, and heap
(Section 6) — without an address space, there would be nowhere for the process's instructions and
working data to actually reside during execution.

**15. What does an entry point mean?** The specific, fixed location in the executable where CPU
execution actually begins — not necessarily the programmer's first source line (Section 9).

**16. Why is `main` not necessarily the first instruction executed?** Because startup/runtime code
frequently executes first, at the entry point, before calling `main` (Section 9, Section 10).

**17. Why can runtime initialization occur before application code runs?** Because for many
execution models (native and especially interpreted/managed), a runtime or interpreter must
itself be set up and ready before it can begin executing the program's own logic (Section 10).

**18. Why may dynamic dependencies need to be prepared before a program runs correctly?** Because
if a program's logic depends on functionality from a separate component (a shared library, a
runtime), that component must be located and made ready first, or the program would try to use
functionality that isn't actually present yet (Section 7).

**19. Why does startup differ between execution models?** Because "programming language" and
"execution strategy" are not the same thing (recalling Concept 8) — native, interpreted, and
managed/bytecode approaches involve genuinely different startup paths (compiled startup code vs.
an interpreter vs. a virtual machine), even though they share the same overall conceptual shape
(Section 13).

---

## Level 3 — Application

**20. Launching a native (compiled) application.** Stored executable (containing machine code,
Concept 7) → launch request → OS creates process → loader makes code/data available in the
process's address space → dependencies (shared libraries, Section 7) prepared → initial execution
state established → execution begins at the entry point → compiled startup code runs → `main`
begins (Section 13's native path).

**21. Launching a Python program.** Stored source file (or bytecode) → launch request (e.g.,
running `python3 script.py`) → OS creates a process for the Python interpreter/runtime → the
interpreter itself starts up (its own executable goes through the same general sequence) →
the interpreter then reads and executes your Python source-level code (Section 10, Section 13's
interpreted/managed path) — connecting directly to Concept 8's compilation/interpretation
vocabulary.

**22. Launching a Java program.** Stored bytecode (`.class`/`.jar`) → launch request → OS creates
a process for the JVM → the JVM itself starts up → the JVM loads and executes the bytecode →
`main` begins (Section 13's bytecode+VM path, recalling Concept 8's identical model).

**23. Launching a command-line tool.** Follows the general sequence (Section 2, the Startup
Timeline) — stored executable → launch (via a terminal command, Section 3) → process created →
loading → entry point → possibly brief runtime setup → application logic runs, commonly reading
command-line arguments (Section 11) to determine what to do.

**24. Launching an AI application.** Follows the same general sequence, with the AI-specific
detail that once application-level code begins (Section 12), it typically proceeds to load
configuration, dependencies, and eventually models/data (Section 15's AI relevance workflow) —
all of which happens *after* the program-startup sequence this lesson describes has completed.

**25. Starting an application that needs a model file.** The program-startup sequence (process
creation through entry point/runtime initialization, Sections 4–10) completes first, entirely
independent of the model file; only once application-level code begins (Section 12) does the
application actually read the model file from storage (Concept 11, Concept 14) — model loading is
application-level work, not part of program startup itself (Section 15, Reasoning Question 2).

---

## Level 4 — Debugging

**26. "The executable exists, so why is there no process?"** A stored executable file existing on
disk does not automatically mean a process is running from it — a process only comes into
existence once the program is actually *launched* (Section 4). An unlaunched executable is not a
process (Misconception 2).

**27. "A process appears, but the application has not finished initializing."** This is
expected: process creation (Section 4) and loading (Section 5) can complete, giving the process a
PID and observable existence, well before runtime initialization (Section 10) and
application-level initialization logic (Section 12) have finished — a process existing and an
application being fully initialized are two different milestones in the same sequence.

**28. A user assumes `main` is the first instruction executed.** This is incorrect per Section 9
and Section 10's central, required correction — execution begins at the entry point, which
frequently runs startup/runtime code before ever calling `main` (Misconception 1, Misconception
5).

**29. "The program starts slowly because dependencies/model files must be prepared" — why is this
expected, not a problem?** Because loading dependencies (Section 7) and, separately, loading
model/data files (Section 15, application-level work) are genuine, real work that takes real time
— slower storage (Concept 12) or larger/more numerous dependencies naturally increase this time;
it is not evidence of a malfunction.

**30. "Two launches of the same executable produce two different PIDs" — why is this expected?**
Because each launch triggers its own independent process-creation step (Section 4; Concept 16,
Section 2's identical concrete example) — each new process receives its own unique PID, even when
launched from the identical executable file.

**31. "The application receives an environment variable but apparently not stdin" — how can both
be true?** Environment variables (Section 11) and stdin (Concept 15, Section 10) are two entirely
separate input mechanisms — a process can have environment variables set at startup while
receiving no data via stdin (e.g., if stdin was never provided or piped), or vice versa; one being
present says nothing about the other (Section 11's comparison table, Misconception 12).

**32. "A native program and a Python program do not have identical startup paths" — why?**
Because a native program's entry point typically leads fairly directly into compiled startup code
and then `main`, while a Python program's launch involves the Python interpreter/runtime itself
starting up first, before it can begin executing your source-level code (Section 13's comparison
table; Misconception 6, Misconception 10).

**33. A user assumes the entire executable is simply copied into RAM as a single, complete step.**
This lesson does not support that specific claim (Section 5's explicit correction) — the exact
loading mechanism is not taught here, and assuming a single, complete, simple copy operation
oversimplifies what loading actually involves (Misconception 4).

---

## Level 5 — Integration / AI Engineering

**34. AI inference service startup.** Trace: stored executable/interpreter+script exists on
storage (Concept 11, 14) → launch request (Section 3) → OS creates the process (Section 4;
Concept 16) → loader makes code/data available in the process's address space (Section 5, 6) →
required runtime/dependencies (e.g., a language runtime, needed libraries, Section 7) are
prepared → initial execution state (command-line arguments, environment variables, Section 8, 11)
is established → execution begins at the entry point (Section 9), runtime initialization occurs
where applicable (Section 10) → application-level code begins (Section 12) and proceeds to load
configuration, connect to whatever it needs, and eventually become ready to receive requests —
this "ready to receive requests" state is application-level work, occurring after this lesson's
entire startup sequence has completed.

**35. Model-loading startup sequence.** Model loading is a distinct, later phase from program
startup: program startup (Sections 4–10) establishes the process, its memory, and reaches the
entry point/completes runtime initialization — all *before* any application-level code exists to
even reference a model file. Model loading only happens once execution reaches application-level
logic (Section 12) — it is explicitly application-level work, not part of the OS/loader-driven
startup sequence this lesson describes (Section 15, Reasoning Question 2 and 3).

**36. Configuration/environment-driven startup.** Environment variables and command-line
arguments (Section 11) are part of a process's initial execution state (Section 8), made
available before application code runs — application-level logic (Section 12) can then read these
values to decide, for example, which configuration file to load, which mode to run in, or which
model to use, meaning the same executable can behave differently across launches purely based on
what arguments/environment variables were provided at startup (Section 15, Reasoning Question 4).

**37. Multiple AI worker processes starting.** Each worker process launch is an independent
application of the launch-request → process-creation sequence (Section 3, Section 4) — even
though all workers might run the exact same executable, each launch produces its own distinct
process with its own PID (Concept 16, Section 2's identical concrete example; Section 15,
Reasoning Question 5), and each independently goes through its own full startup sequence
(loading, address-space setup, entry point, runtime initialization) before reaching its own
application-level execution.

**38. Startup bottleneck caused by storage/model loading.** Using Concept 12's HDD-vs-SSD
vocabulary: loading the executable and its dependencies (Section 5, Section 7) requires reading
data from storage — if that storage device has higher latency (e.g., an HDD rather than an SSD,
Concept 12, Section 7), this read step takes longer, directly increasing how long the overall
startup sequence takes before application-level code (and, later, model loading) can begin. This
connects Concept 12's storage-performance vocabulary directly to Section 15's "startup work may
involve both storage I/O and CPU computation" reasoning point.

---

_This answer key covers Concept 17 (What Happens When a Program Starts) only. It does not
contain, reference, or anticipate answers for Concept 18 (What Happens When a Function Executes),
Concept 19 (Why RAM and Storage Are Different), Concept 20 (Why GPUs Matter for AI), or any later
concept._
