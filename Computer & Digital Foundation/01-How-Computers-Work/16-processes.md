# Processes

**Module:** How Computers Work
**Roadmap reference:** Stage 0 — Module 0.1 — How Computers Work
**Concept(s) covered:** processes
**Status:** Not Started

---

## Prerequisites

**Primary prerequisite:** Concept 15 — Input/Output.

**Supporting prerequisites:** Concept 2 — CPU, Concept 3 — Cores, Concept 6 — Registers, Concept
7 — Instructions & Machine Code, Concept 8 — Compilation & Interpretation, Concept 9 — Cache,
Concept 10 — RAM, Concept 11 — Storage, Concept 13 — GPU, Concept 14 — Files.

This lesson treats all of the above as established knowledge and reuses their vocabulary directly
— fetch-decode-execute (Concept 2), cores (Concept 3), registers (Concept 6), instructions
(Concept 7), compilation/interpretation (Concept 8), RAM (Concept 10), storage (Concept 11), GPU
(Concept 13), files (Concept 14), and I/O (Concept 15) — without reteaching any of them from
scratch.

**A required, explicit boundary before you begin:** this lesson does not teach Concept 17 (What
Happens When a Program Starts), Concept 18 (What Happens When a Function Executes), Concept 19
(Why RAM and Storage Are Different), or Concept 20 (Why GPUs Matter for AI) in depth — each remains
a separate, later lesson. It also does not teach scheduling algorithms, context-switch
implementation, thread programming, or other Operating System Fundamentals (Module 0.2) internals
— only the process *abstraction* itself, at a foundational level.

**Next concepts:** Concept 17 — What Happens When a Program Starts, Concept 18 — What Happens When
a Function Executes, Concept 19 — Why RAM and Storage Are Different, Concept 20 — Why GPUs Matter
for AI.

---

## 1. What Is a Process?

**Starting from what you already know.** Concept 7 and Concept 8 established that a program's
source code eventually becomes machine code the CPU can execute. Concept 15 established that
programs exchange data with the outside world through I/O. This lesson introduces the concept that
ties these together: **what is a running program actually called, and what does the operating
system need to track about it?**

**A beginner approximation, stated explicitly as a starting point — not the final answer:**

> "A process is a program that is running."

This is a reasonable first sentence to hold onto, but this lesson requires you to expand it into a
technically stronger mental model, because it leaves out something essential: *what exactly does
"running" require the operating system to track and manage?*

**Process — technical meaning, the required definition for this lesson:**

> A process is a running instance of a program with an execution context and associated resources
> managed by the operating system.

Breaking this down, term by term (each developed fully in its own section below):

- **"Running instance of a program"** — Section 2 distinguishes program from process precisely;
  a process is one specific, running occurrence of a program, not the program itself.
- **"Execution context"** — Section 6 develops this: the CPU-related state (recalling Concept 2's
  registers, Concept 6) associated with this specific running instance.
- **"Associated resources"** — Section 7 develops this: memory, files (Concept 14), I/O (Concept
  15), and more, that this specific running instance is using.
- **"Managed by the operating system"** — Section 3 develops this: the operating system is
  responsible for creating, tracking, scheduling, and eventually cleaning up processes.

**Why this fuller definition matters.** "A program that is running" makes it sound like a process
is just a label — a flag flipped from "not running" to "running." The fuller definition makes
clear that a process is something the operating system actively constructs and maintains: a
bundle of execution state and resources, distinctly tracked, that continues to exist as a real,
manageable entity for as long as that running instance lasts.

---

## 2. Program, Executable, and Process

**Building a precise conceptual chain, distinguishing four related but different things:**

```text
Source code
      ↓  (compilation/build, Concept 8)
Executable artifact
      ↓  (the operating system launches it)
Process
```

**Source code — recalled from Concept 7 and Concept 8:** human-readable program text.

**Executable — recalled from Concept 8's own AOT-compilation discussion:** a file (Concept 14)
containing, typically, native machine code (Concept 7) that the operating system can load and run
directly.

**Program — this lesson's usage:** a general term referring to the stored instructions/code that
define what should happen when run — this can refer loosely to the source code, or to the compiled
executable artifact, depending on context. **This lesson does not treat "program" as a single,
narrowly-defined technical term with one precise meaning** — it is used, as is common, as a general
label for "the thing that gets run," while **process** is reserved specifically for the *running
instance*.

**Process — as defined in Section 1:** a running instance of a program, with execution context and
resources, managed by the operating system.

**A required, explicit clarification:**

> Do not assume these four terms — source code, executable, program, process — are always
> perfectly interchangeable. Each names a genuinely different thing.

### Comparison Table — Program vs. Process

| Property | Program | Process |
|---|---|---|
| What it is | Stored instructions/code — a general label for "the thing that gets run" (source code or a compiled executable) | A running instance of a program, with execution context and resources (Section 1) |
| Is it running? | No — it's static, stored content | Yes — by definition |
| How many can exist from one program? | One program (one executable file) | Potentially many processes, all launched from the same program (this section's required concrete example) |
| Managed by the operating system while it exists? | No — it's just a file on storage (Concept 11, 14) until launched | Yes — created, tracked, scheduled, and eventually terminated by the OS (Section 3) |

### Comparison Table — Source Code vs. Executable vs. Process

| Property | Source code | Executable | Process |
|---|---|---|---|
| What it is | Human-readable program text (Concept 7, 8) | A file containing machine code, ready to be run (Concept 8, 14) | A running instance, with execution context and resources (Section 1) |
| Is it "running"? | No | No — it's a file sitting on storage (Concept 11) until launched | Yes — by definition |
| Can multiple exist from one of these? | Yes — many builds/versions | Yes — one executable file, but see Section 2's concrete example below | Yes — many processes from the same executable, at once |
| Where does it typically reside? | A file (Concept 14) | A file (Concept 14), on storage (Concept 11) | Actively managed by the operating system, using CPU (Concept 2), RAM (Concept 10), and other resources |

**A concrete example, directly required by this lesson:**

```text
One executable/program
      ↓  launched once
   one process


One executable/program
      ↓  launched twice
   potentially two separate processes
```

If you run the same program twice (for example, opening two separate terminal windows and running
the same command in each), you get **two distinct processes** — each with its own execution
context and resources (Section 1) — even though both originated from the exact same executable
file (Concept 14) on storage. **Why this distinction matters:** if "program" and "process" meant
the same thing, this scenario would be nonsensical — there's still only *one* program (one
executable file), but there can be *many* processes running from it simultaneously, each
independently tracked by the operating system. This directly foreshadows Section 10's discussion
of multiple processes.

### Diagram — Program → Process, and One Program → Multiple Process Instances

```text
Executable (one file, on storage)
        │
        ├──── launched ────▶  Process 1  (its own execution context + resources)
        │
        └──── launched again ────▶  Process 2  (its own, separate execution context + resources)
```

> Simplified conceptual diagram. Both processes originate from the identical executable file, but
> exist as two separate, independently-managed running instances.

---

## 3. Why Operating Systems Use Processes

**The problem the process abstraction solves.** A computer commonly needs to run many programs
"at once" (Section 10 develops exactly what "at once" means), and the operating system needs a
reliable way to track, manage, and keep each running program's state and resources organized and
separate from every other running program's state and resources.

**What a process provides, as a conceptual boundary around a running program's:**

- **Execution state** — where this specific running instance currently is in its execution
  (Section 6).
- **Memory** — the memory this specific running instance is using (Section 5).
- **Resources** — files, I/O connections, and more, that this specific running instance is using
  (Section 7).
- **Identity** — a way to distinguish this running instance from every other one, even if they
  came from the same program (Section 4).
- **Interaction with the operating system** — the operating system's ability to observe, manage,
  and eventually terminate this specific running instance.

**Isolation, introduced conceptually.** One of the most important reasons the process abstraction
exists: it gives each running program's execution state and resources a boundary that keeps them
conceptually separate from every other process's — so that one process's activity doesn't
arbitrarily interfere with another's execution state or memory. **This lesson does not teach
detailed virtual-memory internals** — exactly how the operating system technically enforces this
separation at the memory-hardware level is later material (Module 0.2) — only that this separation
is a core reason the process abstraction exists in the first place.

---

## 4. Process Identity and PID

**PID — Process ID:** a unique identifying number the operating system assigns to each process
while it exists.

**Why the operating system needs process identity.** Since many processes can exist at once
(Section 3, Section 10), and since — as Section 2's concrete example showed — multiple processes
can even come from the exact same program, the operating system needs a reliable way to refer to
*this specific running instance*, distinct from every other one, including other instances of the
same program. A **name** (like the program's filename) is not sufficient for this, because
multiple processes can share the same name (Section 13's genuinely observed practical example
demonstrates this directly). A PID is.

**How a PID allows a process to be observed/referenced.** Once a process has a PID, tools and the
operating system itself can use that specific number to look up information about that exact
process, or to direct an action (like termination, Section 13) at that exact process — and only
that one, even if other processes with the identical program name also happen to be running.

**A required, explicit correction:**

> A PID is not "the program's identity." A PID identifies one specific *running instance* — a
> process — not the program itself. The same program, launched multiple times, produces multiple
> processes, each with its **own distinct PID** (Section 2's concrete example).

**A required, explicit boundary:**

> This lesson does not teach PID namespaces or container internals. Later topic — not taught here.

---

## 5. Process Memory

**A process has an associated memory space** — a portion of RAM (Concept 10) that this specific
running instance uses to hold its instructions, data, and working state.

**Commonly-used conceptual regions/uses of process memory, introduced only at this level:**

- **Code** — the portion holding the process's actual machine-code instructions (Concept 7) — the
  same instructions the CPU (Concept 2) fetches, decodes, and executes.
- **Data** — the portion holding the process's initialized program data (values known in advance).
- **Stack** — a region commonly associated with tracking function calls and local, short-lived
  values as the program executes (this lesson does not teach stack-frame mechanics — see Concept
  18's later, dedicated boundary).
- **Heap** — a region commonly associated with data the program requests more dynamically while
  running, as opposed to values fixed in advance.

### Comparison Table — Process Memory Conceptual Regions

| Region | Commonly associated with |
|---|---|
| Code | The process's machine-code instructions (Concept 7) |
| Data | Initialized program data known in advance |
| Stack | Function-call tracking and short-lived local values |
| Heap | Data requested more dynamically while the program runs |

**A required, explicit qualification:**

> These are commonly used ways to describe regions/uses of process memory — a conceptual
> vocabulary, not a claim about one single, universal, exact memory layout every process must
> follow identically.

**A required, explicit boundary:**

> This lesson does not teach virtual-memory implementation, page tables, the TLB, page faults,
> memory-mapping internals, or allocator internals. Later topic — not taught here (Module 0.2 and
> beyond).

---

## 6. Process Execution Context

**A process has execution state/context associated with its running execution** — connecting
directly back to Concept 2 and Concept 6.

**What this execution context conceptually includes:**

- **CPU** (Concept 2) — the process's instructions are what the CPU is currently executing, when
  this process is actually running (Section 9 distinguishes "running" from merely "existing").
- **Registers** (Concept 6) — the specific values a process's execution is currently using are
  held, at any given moment of actual execution, in registers.
- **Instruction execution** (Concept 7) — the process's machine code is what's being
  fetched-decoded-executed.
- **Program counter/instruction pointer** — a specific register (Concept 6) that tracks *which*
  instruction should be executed next for this process — mentioned here only by name, as part of
  this lesson's execution-context vocabulary; its detailed mechanics are not taught here (see
  Concept 18's later boundary).

**Why the operating system must be able to manage and track execution state.** Because many
processes can exist, and — on a system with fewer CPU cores than processes (Section 11) — they
may need to take turns actually executing, the operating system needs to be able to track exactly
where each process's execution currently stands (which instruction is next, what the relevant
register values are), so that when a process's turn to actually run on a CPU core comes around
again, its execution can correctly continue from precisely where it left off.

**A required, explicit boundary:**

> This lesson does not teach context-switch implementation in depth — exactly how the operating
> system saves and restores this execution context when switching between processes. Later topic
> — not taught here (Module 0.2).

---

## 7. Process Resources

**A running process can have/use resources such as:**

- **Memory** (Section 5, Concept 10).
- **Files** — directly recalling Concept 14; a process may have files open that it's reading from
  or writing to.
- **Input/output** — directly recalling Concept 15; a process may be actively engaged in I/O
  (reading input, producing output).
- **CPU time** — the process's share of actual execution time on a CPU core (Section 9, Section
  11).
- **Devices, through operating-system mechanisms** — recalling Concept 15, Section 8's identical
  point that programs interact with devices through the operating system, not directly.
- **Other operating-system-managed resources** — a general category this lesson does not
  enumerate exhaustively.

### Comparison Table — Process Resources

| Resource | What it represents | Related concept |
|---|---|---|
| Memory | The process's working data/instructions in RAM | Concept 10 |
| Files | Files the process is reading from/writing to | Concept 14 |
| Input/output | Active I/O the process is engaged in | Concept 15 |
| CPU time | The process's share of actual execution time | Concept 2, Section 9/11 (this lesson) |
| Devices (via OS mechanisms) | Hardware the process interacts with, through the OS | Concept 15 |

### Comparison Table — Process vs. File

| Property | Process | File |
|---|---|---|
| What it is | A running instance, with execution context and resources (Section 1) | A logical, persistent unit of stored data (Concept 14) |
| Persistent? | No — exists only while running, then terminates (Section 8, Section 13) | Yes — persists on storage independent of any process (Concept 11, Concept 14) |
| Has a PID? | Yes (Section 4) | No — a file has a name/path (Concept 14), not a PID |
| Relationship | A process may open, read from, or write to one or more files (this section) | A file may be opened by zero, one, or multiple processes over time |

**A required, explicit clarification:** a process and a file are entirely different kinds of
things — a process is a *running* entity the operating system manages; a file is *persistent
data* (Concept 14) a process may use as one of its resources, but the file itself is not running
and does not stop existing when the process that was using it terminates (directly recalling
Concept 14, Section 9's file-vs-RAM persistence distinction, now applied to file-vs-process).

**A required, explicit correction:**

> A process does not "own the physical computer" simply because it is running.

A process's resources are things it's *using*, under the operating system's management and
oversight — not things it exclusively, permanently controls. Other processes exist at the same
time (Section 10), sharing the same underlying CPU, RAM, storage, and devices — a theme Section 11
and Section 12's misconception corrections both return to directly.

### Diagram — Process + CPU + RAM + I/O Relationship

```text
                 ┌───────────────────────────────┐
                 │            Process             │
                 │  (execution context, Section 6) │
                 └───────────────────────────────┘
                    │              │             │
                    ▼              ▼             ▼
                  CPU            RAM            I/O
            (Concept 2, 3)   (Concept 10)   (Concept 15, 14)
            executes the      holds the       reads/writes
            process's         process's       data, via the
            instructions      memory          OS (Concept 15)
```

> Simplified conceptual diagram. A process relies on the CPU, RAM, and I/O together, all under
> operating-system management — it does not exclusively own any of them.

---

## 8. Process States and Lifecycle

**Basic conceptual process states, introduced at a foundational level:**

- **New** — the process is being created but is not yet ready to run.
- **Ready** — the process is prepared to run and is waiting for a CPU core to become available to
  it (Section 11 develops this).
- **Running** — the process is currently actively executing instructions on a CPU core (Section
  6, Section 9).
- **Waiting/blocked** — the process cannot currently proceed because it's waiting for something
  external (commonly I/O, Section 9 develops this fully).
- **Terminated** — the process has finished executing and is no longer running (Section 13
  develops creation/termination).

### Diagram — Process Lifecycle/State Model

```text
   New
    ↓
  Ready ◀────────────────┐
    ↓                     │
 Running ──── waits ────▶ Waiting
    │                     │
    │◀──── becomes ready ─┘
    ↓
Terminated
```

> Simplified conceptual lifecycle. A process commonly cycles between Ready, Running, and Waiting
> multiple times before eventually reaching Terminated.

### Comparison Table — Process States

| State | Meaning |
|---|---|
| New | Being created, not yet ready to run |
| Ready | Prepared to run, waiting for a CPU core |
| Running | Currently executing instructions on a CPU core |
| Waiting/blocked | Cannot proceed — waiting for something external (e.g., I/O) |
| Terminated | Finished executing; no longer running |

**A required, explicit qualification:**

> Actual operating systems may use more detailed state models and implementation-specific
> terminology than this simplified five-state model. This lesson does not teach detailed scheduler
> internals — exactly how and when the operating system moves a process between these states.
> Later topic — not taught here (Module 0.2).

---

## 9. Running, Waiting, and CPU Use

**A required, central, mandatory distinction for this entire lesson:**

> A process can exist even when it is not currently executing instructions on a CPU core.

This is precisely the "Waiting/blocked" state from Section 8, and it is one of the most important
ideas in this lesson — a very common beginner assumption is that a process must always be actively
"doing something" on a CPU. This is not correct.

**Why a process may not continuously execute on a CPU, connecting directly to Concept 15:**

- **Waiting for input** — a process may be blocked waiting for a user (or another program) to
  provide data (Concept 15, Section 3's human/program input categories).
- **Waiting for file I/O** — a process may be waiting for a file read/write to complete (Concept
  15, Section 7).
- **Waiting for network I/O** — a process may be waiting for a network request or response
  (Concept 15, Section 9).
- **Waiting for another event/resource** — a general category for other situations where a process
  cannot proceed until something external happens.

**The direct connection to Concept 15's central theme:** Concept 15 established that I/O commonly
involves *waiting*, and that this waiting can become a bottleneck (Concept 15, Section 12). This
lesson's "waiting/blocked" process state is precisely what that waiting looks like from the
process's own perspective — a process performing synchronous I/O (Concept 15, Section 11) enters
the waiting state until that I/O completes, during which time it is not executing on a CPU core at
all, even though it absolutely still exists, is still fully tracked by the operating system, and
will resume running once the I/O it's waiting on finishes.

**This lesson's own genuinely captured practical example (Section 14) demonstrates this exact
point concretely** — a `sleep` process shows a `State: S (sleeping)` in its real, observed
`/proc/<PID>/status` output, a direct, real illustration of "waiting" without being terminated.

---

## 10. Multiple Processes, Concurrency, and Parallelism

**An operating system can manage many processes.** Process A, Process B, and Process C may all
exist at the same time.

**A required, explicit, central correction:**

> "Exists at the same time" does not necessarily mean "all executing simultaneously on separate
> physical CPU cores."

Recall Concept 3's foundational distinction, directly reused here:

```text
Concurrency:
multiple tasks are being managed/progressed.

Parallelism:
multiple tasks actually execute simultaneously.
```

**Applying this to processes specifically:** several processes can all exist, all be in the
"Ready" or "Running" state at different moments (Section 8), and all make progress *over time* —
this is **concurrency**. Whether they are genuinely executing *at the exact same instant*, on
separate CPU cores, is a separate question — that specifically is **parallelism**, and it depends
on how many CPU cores are actually available (Concept 3) and how many processes are truly ready to
run at that exact moment (Section 11 develops this directly).

### Diagram — Multiple Processes Sharing CPU Execution Opportunities

```text
One CPU core, three processes (concurrency without parallelism):

Time  →   [ A running ] [ B running ] [ A running ] [ C running ] [ B running ] ...
              (only one process actually executes at any single instant)


Multiple CPU cores, three processes (parallelism possible):

Core 1 →  [ A running ][ A running ][ A running ] ...
Core 2 →  [ B running ][ B running ][ B running ] ...
Core 3 →  [ C running ][ C running ][ C running ] ...
              (multiple processes can genuinely execute at the same instant)
```

> Simplified conceptual diagram. This lesson does not teach the specific scheduling algorithm an
> operating system uses to decide the exact order or timing shown in the single-core case — see
> Section 8's identical boundary.

### Comparison Table — Concurrency vs. Parallelism

| Property | Concurrency | Parallelism |
|---|---|---|
| Definition | Multiple tasks being managed/progressed | Multiple tasks actually executing at the same instant |
| Requires multiple CPU cores? | No | Yes (Concept 3) |
| Can happen on a single core? | Yes (by taking turns, Section 11) | No |
| Example (this lesson) | Three processes taking turns on one core | Three processes each running on their own core, at once |

**A required, explicit boundary:**

> This lesson does not teach concurrency programming — how to actually write software that
> coordinates multiple tasks. Later topic — not taught here.

---

## 11. Process vs. CPU Core

**A required, explicit, central distinction:**

- **A process is software execution context** — the running instance and its associated state and
  resources (Section 1, Section 6, Section 7).
- **A CPU core is hardware capable of executing instructions** — a physical component (Concept 3).

**Simple examples, directly required:**

```text
1 core + multiple processes
→ processes can take turns using CPU execution time.

Multiple cores + multiple runnable processes
→ multiple processes may execute in parallel.
```

This is precisely Section 10's diagram, restated in this section's specific process-vs-core
framing: a single CPU core can only actually execute one process's instructions at any given
instant (Section 6's execution-context idea, tied to Concept 2's fetch-decode-execute model) — but
it can switch between different processes' execution contexts over time, giving the *appearance*
of many processes running "at once" even though, on that single core, only one genuinely is at any
exact instant (concurrency, per Section 10). With multiple cores (Concept 3), genuine parallel
process execution becomes possible.

### Comparison Table — Process vs. CPU Core

| Property | Process | CPU core |
|---|---|---|
| What it is | Software — a running instance with execution context/resources | Hardware — a physical execution unit (Concept 3) |
| Can exist without currently executing? | Yes (Section 9's waiting state) | N/A — a core is hardware, always physically present regardless of what it's doing |
| Quantity on a typical system | Can be many (dozens, hundreds) | Typically a small, fixed number (Concept 3) |
| Relationship | A process needs a core to actually execute its instructions (Section 6) | A core can execute different processes' instructions, at different times or in parallel with other cores |

**A required, explicit correction:**

> "A process gets an entire CPU core permanently" is incorrect. A process may be given a core's
> execution time temporarily, take turns with other processes (Section 10's single-core diagram),
> and does not permanently, exclusively claim a core simply by existing or even by currently
> running.

---

## 12. Process vs. Thread

**Introduced only enough to establish the distinction — threads are not the main topic of this
lesson.**

- **Process** — the broader execution/resource boundary (Section 1, Section 3, Section 7) — has
  its own memory space (Section 5), its own PID (Section 4), and its own set of resources.
- **Thread** — an execution path *within* a process.

**A process may contain one or more threads.** A single process can have just one execution path
(a "single-threaded" process, though this lesson does not use that term as required vocabulary),
or it can have multiple execution paths running within the same process's shared memory and
resources (a "multi-threaded" process).

### Diagram — Process vs. Thread Conceptual Relationship

```text
                    Process
        (its own memory, PID, resources)
                       │
        ┌──────────────┼──────────────┐
        ▼               ▼              ▼
    Thread 1         Thread 2       Thread 3
  (an execution    (an execution   (an execution
   path within      path within     path within
   the process)      the process)    the process)
```

> Simplified conceptual diagram. Multiple threads within one process generally share that
> process's memory and resources — this lesson does not teach how that sharing actually works
> internally.

### Comparison Table — Process vs. Thread

| Property | Process | Thread |
|---|---|---|
| Scope | Broader execution/resource boundary (Section 1) | An execution path within a process |
| Has its own memory space? | Yes (Section 5) | Generally shares the containing process's memory |
| Has its own PID? | Yes (Section 4) | Not in the same sense — threads exist within a process's identity |
| Minimum count per process | At least one | N/A (a thread only exists within a process) |

**A required, explicit boundary, restated firmly:**

> This lesson does not teach thread synchronization, mutexes, locks, race conditions, thread
> pools, thread scheduling, pthreads, Python threading, or async programming. Threads are
> introduced here only to establish this one distinction — everything about actually programming
> with threads is later material.

---

## 13. Process Creation, Termination, and Exit Status

**The conceptual lifecycle, tying Section 8's states to a concrete beginning and end:**

```text
program launched
      ↓
process created
      ↓
process executes
      ↓
process terminates
```

**Process creation.** When a program is launched (this lesson does not teach the detailed startup
sequence — that is Concept 17, a later, dedicated lesson), the operating system creates a new
process for it: assigning it a PID (Section 4), setting up its initial memory (Section 5), and
placing it into the "New," then "Ready," state (Section 8).

**Process termination.** When a process finishes executing (or is stopped), it transitions to the
"Terminated" state (Section 8) — its resources (Section 7) are reclaimed by the operating system,
and it no longer exists as a running entity.

**Exit status.** A value a process provides when it terminates, conventionally indicating whether
it completed successfully or encountered a problem. **This lesson introduces exit status only at
this conceptual level** — the specific meaning of particular exit status values, and how programs
are meant to use them, is not taught here in depth.

**A required, explicit boundary:**

> This lesson does not teach `fork()`, `exec()`, `wait()`, `clone()`, process groups, sessions, or
> signals implementation. Later topic — not taught here (Module 0.2). You may mention that process
> creation occurs when a program is launched (as this section does), but the detailed startup
> sequence itself belongs to Concept 17, not this lesson.

---

## 14. Practical Linux/WSL2 Process Observation

As with every prior concept file, this section is safe, uses only a harmless, clearly-identified
temporary process for anything created, requires no `sudo`, never kills arbitrary processes, does
not modify system configuration, and never fabricates output. Reminder of your environment:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu
```

**Checking command availability first.** Every command below (`ps`, `pgrep`, `pidof`, `sleep`) was
confirmed available in the environment used to prepare this lesson via `which`. **The output shown
below is genuinely observed** — captured by actually running these commands, using a harmless
background `sleep` process created specifically for this observation and safely terminated
afterward. **Your own output will very likely differ (your own PID values, username, timing) —
treat the output below as this lesson's own observed example.**

**Step 1 — start a harmless, clearly-identified process to observe.**

```bash
sleep 60 &
```

Running this in the background starts a `sleep` process that does nothing but wait for 60 seconds
— a completely harmless process, ideal for safe observation, matching this lesson's requirement to
use `sleep` specifically for this purpose.

**Step 2 — capture its PID.**

```bash
echo "$!"
```

*Observed output from this WSL2 environment:*

```text
4949
```

*What this demonstrates:* `$!` captures the PID (Section 4) of the most recently started
background process — a direct, concrete way to obtain a process's unique identity right after
creating it.

**Step 3 — find the process by name, using `pgrep`.**

```bash
pgrep -a sleep
```

*Observed output from this WSL2 environment:*

```text
4949 sleep 60
```

*What this demonstrates:* `pgrep -a` searches for processes by (part of) their command name and
reports their PID alongside the full command — confirming PID `4949` corresponds to our `sleep 60`
process, matching Step 2's captured value exactly.

**Step 4 — find the process by name, using `pidof`.**

```bash
pidof sleep
```

*Observed output from this WSL2 environment:*

```text
4949
```

*What this demonstrates:* `pidof` reports the PID(s) of running processes matching a given
executable name — again confirming the same PID.

**Step 5 — inspect the process directly by PID, using `ps`.**

```bash
ps -p 4949 -o pid,ppid,stat,etime,cmd
```

*Observed output from this WSL2 environment:*

```text
    PID    PPID STAT     ELAPSED CMD
   4949    4947 S          00:00 sleep 60
```

*What this demonstrates:* `ps -p <PID>` reports detailed information about one specific process —
its PID, its **PPID** (parent process ID — mentioned here only conceptually, not taught in depth),
its **STAT** (status/state — `S` here means "sleeping," directly matching Section 8's
"waiting/blocked" state), how long it's been running (`ELAPSED`), and its command.

**Step 6 — inspect the process through `/proc/<PID>/status`.**

```bash
head -n 8 /proc/4949/status
```

*Observed output from this WSL2 environment:*

```text
Name:	sleep
Umask:	0022
State:	S (sleeping)
Tgid:	4949
Ngid:	0
Pid:	4949
PPid:	4947
TracerPid:	0
```

*What this demonstrates:* the `/proc/<PID>/status` file (part of the `/proc` filesystem, mentioned
here only as an observation interface — not taught in depth) provides detailed process
information. Notice `State: S (sleeping)` — this is a **direct, genuine, real confirmation of
Section 9's central claim**: this process exists, has a name, a PID, a parent, and a tracked
state, while *not* currently executing on a CPU core at all — it's waiting (sleeping), exactly as
Section 8 and Section 9 describe conceptually.

**Step 7 — clean up: terminate only this specific, clearly-identified process.**

```bash
kill 4949
```

*What this does:* sends a termination request to the specific process with PID `4949` — the exact
`sleep` process created in Step 1 for this observation, and no other process. **This lesson never
kills arbitrary processes** — only a harmless, self-created process, clearly identified by its
exact PID, is ever terminated.

**Step 8 — confirm termination.**

```bash
ps -p 4949 -o pid,cmd
```

*Observed output from this WSL2 environment:*

```text
    PID CMD
```

*What this demonstrates:* no matching process is found — PID `4949` has genuinely terminated
(Section 8's "Terminated" state, Section 13's process-termination discussion), confirmed by `ps`
reporting nothing for that PID.

**Required WSL2-specific caveats:**

- These observations were made inside WSL2's Ubuntu Linux environment — process information
  observed here reflects the WSL2 Linux environment specifically.
- WSL2 exposes a virtualized Linux environment; process and hardware observations made here should
  not automatically be interpreted as direct observations of the underlying Windows host — a
  caution directly consistent with every prior concept file's identical WSL2-virtualization
  caveats (Concept 3, Concept 6, Concept 9, Concept 10, Concept 11, Concept 12, Concept 13).
- Do not assume a specific PID value — PIDs are assigned dynamically and will differ every time
  you run these steps yourself, even on the exact same system.

---

## 15. AI Engineering Relevance, Exercises, Review, and Production Context

### AI Engineering Relevance

**A simple conceptual workflow, connecting this lesson's vocabulary to a realistic AI scenario:**

```text
User request
      ↓
AI application process       (Section 1 — a running instance, with its own PID, Section 4)
      ↓
input                          (Concept 15 — request data arriving)
      ↓
model/data access               (Concept 14 — files; Concept 11 — storage)
      ↓
CPU/GPU computation               (Concept 2, Concept 13 — the process's execution, using
                                    CPU and, where applicable, GPU resources, Section 7)
      ↓
output                              (Concept 15 — a response)
      ↓
logging/persistence                  (Concept 14 — writing to a file)
```

**Why processes matter to an Applied AI Engineer, kept conceptual — this lesson does not teach
distributed systems, production orchestration, Docker, Kubernetes, distributed workers,
multiprocessing frameworks, Ray, Celery, distributed training, or GPU process isolation:**

- **AI application execution** — every running AI application is, at the level this lesson
  teaches, a process (or several).
- **Model loading** — loading a model's data (Concept 11, Concept 14) happens within a specific
  process's execution and memory (Section 5).
- **Data processing** — a process's CPU/GPU computation (Section 7) on input data.
- **API services** — an API server commonly runs as its own process, handling requests (Concept
  15).
- **Inference workers** — a process (or several) dedicated to performing model inference.
- **Training workloads** — a process (or several) performing model training, commonly
  long-running and CPU/GPU-intensive.
- **CPU/GPU usage** — Section 7's process-resources concept applies directly: a process uses CPU
  time, and, where relevant, GPU resources (Concept 13), under operating-system/driver management.
- **File I/O** — reading datasets, writing checkpoints and logs (Concept 14).
- **Network I/O** — receiving requests, sending responses (Concept 15, Section 9).
- **Logging** — a process commonly writes ongoing records of its activity to a file (Concept 14,
  Concept 15).
- **Resource consumption** — understanding that a process consumes (rather than exclusively owns)
  memory, CPU time, and other resources (Section 7's explicit correction) is directly relevant to
  reasoning about real AI system behavior.

**A required, explicit note on multiple processes in real AI systems:** real AI systems commonly
involve **multiple processes** working together — conceptually, an **API server process**, one or
more **worker processes**, an **inference process**, a **training process**, and a
**monitoring/logging process** might all exist as part of one overall AI system. **This lesson does
not teach production orchestration** — how these multiple processes are actually coordinated,
deployed, or scaled in a real production system is genuinely later material.

### Exercises and Debugging Scenarios

Work through these in order, showing your reasoning for every explanation or comparison — not just
a final answer.

#### Level 1 — Recognition

1. What is a program?
2. What is an executable?
3. What is a process?
4. What is a PID?
5. What is a CPU core, as distinct from a process?
6. What is a thread, at the conceptual level this lesson introduces it?
7. Name the five process states this lesson introduces.
8. Name three examples of process resources.

#### Level 2 — Understanding

Answer each in your own words, in at least one or two full sentences.

9. Why is a process more than just "a program that is running"?
10. Why does a process need a PID, rather than just being identified by its program name?
11. What does a process's memory conceptually consist of?
12. What are a process's resources, and why doesn't a process "own" them outright?
13. Describe the basic process lifecycle, from creation to termination.
14. Why can a process exist without currently executing on a CPU core?
15. Why is a process different from a CPU core?
16. Why is a process different from a thread?

#### Level 3 — Application

**Exercise A — Launching programs.** A user runs the same script twice, in two separate terminal
windows.

17. How many processes result? Explain your reasoning, referencing Section 2.

**Exercise B — File I/O and waiting.** A process is reading a very large file from a slow storage
device (recalling Concept 12).

18. Which process state (Section 8) is this process most likely in while the read is happening,
    and why?

**Exercise C — Network I/O.** A server process is waiting for a client to send a request.

19. Which process state is this server process in while waiting, and why?

**Exercise D — CPU usage.** A system has 4 CPU cores and 10 runnable processes.

20. Can all 10 processes be executing in parallel at the exact same instant? Explain your
    reasoning, referencing Section 10 and Section 11.

**Exercise E — AI application scenario.** An AI inference process reads a model checkpoint from
storage, loads it into memory, and uses the GPU to compute a result.

21. Identify each step in terms of this lesson's vocabulary (process resources, states, and
    execution context).

#### Level 4 — Debugging

For each scenario, reason through what's happening and why.

22. "The program file exists on disk, so why isn't there a process for it?" — explain what's
    missing from this reasoning.
23. A process exists (confirmed via `ps`), but its CPU usage is reported as near zero. What are at
    least two plausible explanations?
24. Two processes are observed with the exact same program name in `ps aux` output. Explain how
    this is possible and how you'd tell them apart.
25. A process is in the "waiting/blocked" state, and a user assumes it has crashed. Explain why
    this assumption is not necessarily correct.
26. A user assumes that once a process starts running, it permanently owns a CPU core until it
    terminates. Explain why this is incorrect.
27. A user sees multiple processes listed in `ps aux` at the same time and assumes they must all be
    executing in parallel right now. Explain why this assumption requires more information to
    confirm.
28. A user confuses a process's PID with its executable/program name, using them interchangeably.
    Explain why this is imprecise.
29. A user says, "This process has multiple threads, so it must actually be multiple processes."
    Explain why this is incorrect.

#### Level 5 — Integration / AI Engineering

**Scenario A — AI inference process reading a model from storage.** An inference process reads a
large model checkpoint from a storage device (Concept 11, Concept 12), loads it into RAM (Concept
10), and then uses the GPU (Concept 13) to compute a result, finally writing the result to a log
file (Concept 14).

30. Trace this scenario end to end, identifying every process state transition (Section 8) and
    every resource (Section 7) involved.

**Scenario B — AI application waiting for network input.** An AI application process is waiting to
receive a request over the network (Concept 15).

31. Which process state is it in while waiting? What happens to its CPU usage during this time,
    and why?

**Scenario C — Worker process using CPU and GPU.** A worker process alternates between CPU-based
data preparation and GPU-based computation.

32. Explain, using Section 6, Section 7, and Concept 13, how this single process can be described
    as using two different kinds of processing resources over the course of its execution.

**Scenario D — Multiple AI-related processes.** A system runs an API server process, an inference
worker process, and a logging process, all at the same time, on a machine with 2 CPU cores.

33. Using Section 10 and Section 11, reason about whether these three processes can all be
    executing in parallel at any given instant, and what determines whether they are.

**Scenario E — Process consuming memory while waiting for I/O.** A process has loaded a large
dataset into RAM and is now waiting for a slow disk write to complete.

34. Using Section 5, Section 7, and Section 9, explain why this process still consumes memory
    resources even though it is not currently executing on a CPU core.

**Solutions are not provided here.** See
[`exercises/16-processes-answer-key.md`](./exercises/16-processes-answer-key.md) — open it only
after attempting every question above.

### Common Mistakes and Misconceptions

```text
Misconception 1  → "A process is just a program file."
Correct idea     → A program file (an executable, Concept 14) is a stored, non-running artifact;
                    a process is a running instance, with execution context and resources
                    (Section 1, Section 2). The file continues to exist on storage regardless of
                    whether any process is currently running from it.
Example          → The `sleep` executable exists on disk whether or not any `sleep` process is
                    currently running — Section 14's practical work shows the process (PID 4949)
                    coming into existence and later terminating, while the underlying `sleep`
                    program file itself was never created or destroyed by this.
```

```text
Misconception 2  → "A process and a program are exactly the same thing."
Correct idea     → A program is the stored code/instructions; a process is a specific running
                    instance of it, with its own execution context and resources (Section 2's
                    comparison table).
Example          → The same program, run twice, produces two different processes (Section 2's
                    required concrete example) — if program and process were identical, this
                    would be a contradiction.
```

```text
Misconception 3  → "One program can only have one process."
Correct idea     → A single executable can be launched multiple times, producing multiple,
                    independent processes, each with its own PID and execution context
                    (Section 2, Section 4).
Example          → Running the same script in two separate terminal windows (Level 3, Exercise
                    A) produces two separate processes.
```

```text
Misconception 4  → "If a process exists, it must currently be using a CPU core."
Correct idea     → A process can exist in the "waiting/blocked" state (Section 8) without
                    currently executing on any CPU core at all (Section 9's central, required
                    point).
Example          → Section 14's genuinely observed `/proc/4949/status` output showed
                    `State: S (sleeping)` — the process existed, with a tracked PID and state,
                    while not executing any instructions on a CPU core.
```

```text
Misconception 5  → "A CPU core is a process."
Correct idea     → A CPU core is hardware (Concept 3); a process is software execution context
                    (Section 1, Section 11's explicit comparison table). A core can execute
                    different processes' instructions at different times, or in parallel with
                    other cores — it is not itself a process.
Example          → Section 11's table draws this distinction explicitly: "hardware" vs.
                    "software," with fundamentally different properties.
```

```text
Misconception 6  → "A process gets an entire CPU core permanently."
Correct idea     → A process may be given a core's execution time temporarily, taking turns
                    with other processes on the same core (Section 10, Section 11's explicit
                    correction) — it does not permanently, exclusively claim a core.
Example          → Section 10's single-core diagram shows processes A, B, and C taking turns on
                    one core over time, none of them permanently holding it.
```

```text
Misconception 7  → "Multiple processes always execute simultaneously."
Correct idea     → Multiple processes can exist "at the same time" (all in existence) without
                    necessarily executing at the exact same instant — that specifically requires
                    parallelism, which depends on having enough CPU cores available (Section 10's
                    required, central correction).
Example          → On a single-core system, multiple existing processes take turns
                    (concurrency) rather than genuinely executing simultaneously (parallelism) —
                    Section 10's diagram shows both cases side by side.
```

```text
Misconception 8  → "Concurrency and parallelism are the same thing."
Correct idea     → Concurrency means multiple tasks are being managed/progressed; parallelism
                    means multiple tasks are actually executing at the same instant (Section 10's
                    comparison table, recalled directly from Concept 3). Concurrency can happen
                    on a single core; parallelism cannot.
Example          → Three processes taking turns on one core is concurrency without parallelism;
                    three processes each on their own core, running at the same instant, is
                    parallelism.
```

```text
Misconception 9  → "A process is the same as a thread."
Correct idea     → A process is the broader execution/resource boundary; a thread is an
                    execution path within a process (Section 12's explicit definitions and
                    comparison table) — a process may contain one or more threads.
Example          → A single process with multiple threads still has one PID, one memory space
                    (generally shared among its threads) — it is not multiple processes
                    (directly corrects the Level 4, Exercise 29 debugging scenario).
```

```text
Misconception 10 → "A process owns physical RAM."
Correct idea     → A process uses a portion of RAM (Section 5, Section 7) under operating-system
                    management — it does not exclusively, permanently own the physical RAM
                    hardware itself (Concept 10), which is a shared resource across the whole
                    system.
Example          → Section 7's diagram shows the process relying on RAM as one of several
                    resources it uses, not something it possesses outright.
```

```text
Misconception 11 → "A process owns the CPU."
Correct idea     → A process uses CPU time (Section 7) — temporarily, and typically taking
                    turns with other processes (Section 10, Section 11) — it does not own the
                    CPU hardware itself.
Example          → Directly corrects Misconception 6 above, from the CPU-specific angle.
```

```text
Misconception 12 → "Waiting means the process has terminated."
Correct idea     → Waiting/blocked (Section 8) is a distinct, active state — the process still
                    exists, is still tracked by the operating system, and will resume once
                    whatever it's waiting on completes. Terminated (Section 8, Section 13) is a
                    completely different, final state.
Example          → Section 14's genuinely observed `sleep` process was in state `S (sleeping)`
                    — waiting, not terminated — confirmed by `ps` still finding it; only after
                    Step 7's explicit `kill` command did it actually terminate, confirmed by
                    Step 8's empty `ps` result.
```

```text
Misconception 13 → "A PID is the program's identity."
Correct idea     → A PID identifies one specific running instance (a process), not the program
                    itself (Section 4's explicit correction) — the same program launched
                    multiple times produces multiple different PIDs.
Example          → If you ran `sleep 60` a second time while the first was still running, it
                    would receive a different PID from `4949` — both would be "the `sleep`
                    program," but two distinct process identities.
```

```text
Misconception 14 → "A process is always doing useful computation."
Correct idea     → A process spends real time in the waiting/blocked state (Section 8, Section
                    9) doing no computation at all — simply waiting for I/O or another event.
                    Existing and actively computing are not the same thing.
Example          → Section 14's `sleep` process did no computation whatsoever during its
                    existence — its entire purpose was to wait, genuinely demonstrating a
                    process that exists without computing.
```

```text
Misconception 15 → "Every process has exactly one fixed state forever."
Correct idea     → A process moves through multiple states over its lifetime (Section 8's
                    lifecycle diagram) — commonly cycling between Ready, Running, and Waiting
                    multiple times before eventually reaching Terminated. State is dynamic, not
                    fixed.
Example          → Section 14's `sleep` process moved from New/Ready (at creation) to Running
                    briefly, to Waiting (sleeping, as observed), and finally to Terminated (after
                    `kill`) — several distinct states over its short lifetime.
```

### Review Questions

Answers are intentionally not provided directly below these questions.

1. What is a process, using this lesson's full technical definition (not just the beginner
   approximation)?
2. Why is a process more than "a program that is running"?
3. What is the difference between a program, an executable, and a process?
4. What is a PID, and why does the operating system need it?
5. What are the commonly-described regions/uses of process memory?
6. What is a process's execution context?
7. What resources can a process have/use?
8. What are the basic process states, and what does each mean?
9. Why can a process exist without currently executing on a CPU core?
10. What is the difference between concurrency and parallelism?
11. What is the difference between a process and a CPU core?
12. What is the difference between a process and a thread?
13. What happens conceptually during process creation and termination?
14. Why do real AI systems commonly involve multiple processes?

### Production Relevance

You now understand what a process actually is (a running instance with execution context and
resources, managed by the operating system — not merely "a running program" as a vague label), how
it differs from a program, executable, CPU core, and thread, what process memory, execution
context, and resources conceptually consist of, the basic process lifecycle and states, why a
process can exist while waiting without executing on a CPU, and the difference between concurrency
and parallelism.

**How this connects to your future work:**

- **What Happens When a Program Starts (Concept 17)** — the detailed process-creation sequence
  this lesson only introduced at the surface level (Section 13).
- **What Happens When a Function Executes (Concept 18)** — the detailed mechanics of execution
  context (Section 6), stack frames (Section 5), and the program counter, which this lesson
  introduced only conceptually.
- **Why RAM and Storage Are Different (Concept 19)** — building further on process memory's
  reliance on RAM (Section 5).
- **Why GPUs Matter for AI (Concept 20)** — building further on how a process can use GPU
  resources (Section 7, Section 15's AI relevance).
- **Operating System Fundamentals (Module 0.2)** — scheduling, context switches, system calls, and
  every other mechanism this lesson deliberately deferred.
- **AI Engineering** — every real AI system you build will run as one or more processes, using the
  exact resources (CPU, RAM, storage, files, I/O, GPU) this entire module has built vocabulary for,
  one concept at a time.

**A required, final, explicit boundary:**

> This lesson does not teach scheduling algorithms, context-switch implementation, thread
> programming, detailed process-creation mechanics, or distributed-systems/production
> orchestration. What this lesson provides is the conceptual foundation — what a process is, how
> it relates to programs and executables, its identity, memory, execution context, resources,
> states, and its relationship to CPU cores and threads — that all of that later material will
> build directly on top of.

---

_This file was written as the completed Concept 16 lesson for Module 0.1. It does not teach
kernel architecture, system calls, scheduling algorithms, context-switch implementation,
interrupts, virtual-memory implementation, page tables, the TLB, process namespaces, cgroups,
signals implementation, IPC mechanisms, file descriptors, VFS, filesystem internals, or
synchronization primitives (Module 0.2); thread synchronization, mutexes, locks, race conditions,
thread pools, thread scheduling, pthreads, Python threading, or async programming; `fork()`,
`exec()`, `wait()`, `clone()`, process groups, sessions, or signals implementation; loader
internals, executable-loading internals, dynamic-linking internals, environment initialization,
runtime initialization, or entry-point internals (Concept 17); stack-frame internals,
function-call mechanics, calling conventions, detailed register usage, return-address mechanics,
or recursion internals (Concept 18); the deeper RAM/storage material reserved for Concept 19; GPU
architecture, CUDA, tensor operations, kernels, distributed training, or GPU optimization (Concept
20); or Docker's process model, Kubernetes, distributed workers, multiprocessing frameworks, Ray,
Celery, distributed training, or GPU process isolation — in depth. Those remain scaffolded,
unwritten concept files (or entirely untouched, in the case of later-stage or later-module
material) until their own turn in the sequence. Concepts 17 through 20 specifically are the next
lessons in this module, and none of them are taught here._
