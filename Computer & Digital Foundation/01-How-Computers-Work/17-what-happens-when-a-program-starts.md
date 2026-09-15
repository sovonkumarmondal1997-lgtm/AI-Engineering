# What Happens When a Program Starts

**Module:** How Computers Work
**Roadmap reference:** Stage 0 — Module 0.1 — How Computers Work
**Concept(s) covered:** what happens when a program starts
**Status:** Not Started

---

## Prerequisites

**Primary prerequisite:** Concept 16 — Processes.

**Supporting prerequisites:** Concept 2 — CPU, Concept 3 — Cores, Concept 6 — Registers, Concept
7 — Instructions & Machine Code, Concept 8 — Compilation & Interpretation, Concept 10 — RAM,
Concept 11 — Storage, Concept 14 — Files, Concept 15 — Input/Output.

This lesson treats all of the above as established knowledge, reusing process/PID vocabulary
(Concept 16), fetch-decode-execute and registers (Concept 2, Concept 6), machine code (Concept 7),
compilation/interpretation (Concept 8), RAM (Concept 10), storage/files (Concept 11, Concept 14),
and I/O (Concept 15) directly, without reteaching any of them.

**A required, explicit boundary before you begin:** this lesson does not teach Concept 18 (What
Happens When a Function Executes), Concept 19 (Why RAM and Storage Are Different), or Concept 20
(Why GPUs Matter for AI) in depth — each remains a separate, later lesson. It also does not teach
kernel/system-call internals, ELF/PE format internals, dynamic-linker internals, or shell
internals — only the conceptual startup sequence.

**Next concepts:** Concept 18 — What Happens When a Function Executes, Concept 19 — Why RAM and
Storage Are Different, Concept 20 — Why GPUs Matter for AI.

---

## 1. What Does It Mean to Start a Program?

**Starting from what you already know.** Concept 16 established what a process is — a running
instance of a program, with execution context and resources, managed by the operating system. But
Concept 16 deliberately did not explain *how a process comes into being* when a program is
launched — it only introduced process creation and termination at the surface level, explicitly
deferring the detailed sequence to this lesson.

**The core question this lesson answers:** what actually happens between "I ask the computer to
run a program" and "the program is now executing"?

**A required, explicit correction, stated immediately:**

> Starting a program is NOT simply "click program → CPU runs it."

This lesson requires you to replace that oversimplified mental model with a real conceptual
sequence — several distinct things must happen, involving the operating system, memory, and more,
before the CPU ever executes a single instruction belonging to your program.

**Distinguishing four things that are easy to conflate, directly recalling Concept 16, Section 2:**

- **Program stored on storage** — inert data sitting on a storage device (Concept 11), not
  currently doing anything (Concept 14's file vocabulary applies directly).
- **Executable artifact** — a specific kind of stored file (Concept 14) containing, typically,
  machine code (Concept 7) ready to be run.
- **Process** — a *running instance* (Concept 16, Section 1) — this only comes into existence once
  the program is actually launched.
- **Running program** — informal language for "a process that is currently executing" — this
  lesson uses "process" as the precise term (Concept 16) and "running program" only as an
  everyday, looser synonym.

**A program can exist as stored data without currently executing** — exactly as Concept 16,
Misconception 1 already established ("a process is just a program file" is incorrect). A program
file sitting on your storage device (Concept 11, Concept 12) is not doing anything at all until
something causes it to be launched — which is precisely what this entire lesson explains.

### Comparison Table — Program vs. Executable vs. Process

| Property | Program | Executable | Process |
|---|---|---|---|
| What it is | General label for stored instructions/code (source or compiled) | A specific file containing machine code, ready to run (Concept 8, 14) | A running instance, with execution context and resources (Concept 16) |
| Currently running? | No | No — a file on storage until launched | Yes — by definition |
| Where it resides | Storage, typically as source or a built artifact | Storage, as a file (Concept 11, 14) | Actively managed by the OS, using CPU/RAM (Concept 2, 10) |
| Created when? | N/A — it's written/built ahead of time | N/A — produced by compilation/build (Concept 8) | At launch, via process creation (Section 4) |

**A required, explicit clarification:** this table restates and extends Concept 16, Section 2's
identical program-vs-executable-vs-process distinction — this lesson does not introduce a new,
different meaning for these terms; it reuses them exactly as Concept 16 established.

---

## 2. From Program File to Process

**The conceptual chain this lesson builds, in full, stated here as an overview before each step
is developed individually in later sections:**

```text
Stored program/executable
        ↓
Launch request
        ↓
Operating system receives request
        ↓
Process created
        ↓
Process execution environment established
        ↓
Executable mapped/loaded into the process's address space
        ↓
Required program/runtime components prepared
        ↓
Initial execution state established
        ↓
Entry point begins executing
        ↓
Application-level code begins
```

**A required, explicit qualification, stated immediately and repeated throughout this lesson:**

> This is a conceptual model, not a universal, instruction-by-instruction implementation. The
> exact details vary between Linux, Windows, macOS, different executable formats, compiled
> languages, interpreted languages, managed runtimes, and containers/virtualized environments.

Do not treat this as a rigid, step-numbered algorithm every system follows identically — treat it
as a correct, reliable *shape* that helps you understand roughly what must happen, in roughly what
order, regardless of exactly how any one specific system implements it.

### Diagram — Program File → Process

```text
Program file (executable, on storage, Concept 11/14)
            │
            │   launch request (Section 3)
            ▼
   Operating system participates (Section 3)
            │
            ▼
      Process created (Concept 16; Section 4)
            │
            ▼
  Process begins executing (eventually reaching
  application-level code, Section 12)
```

> Simplified conceptual diagram. The program file itself does not change or move during this —
> it remains on storage; what's created is a new, separate process (Concept 16).

### Comparison Table — Launch vs. Loading vs. Execution

| Property | Launch (Section 3) | Loading (Section 5) | Execution (Section 9 onward) |
|---|---|---|---|
| What happens | A request is made and received by the OS, which creates a process | The executable's contents are made available within the process's address space | The CPU actually fetches/decodes/executes instructions (Concept 2, 7), beginning at the entry point |
| Who/what acts | User or another program, then the OS (Section 3, 4) | The loader (part of OS responsibility, Section 5) | The CPU (Concept 2) |
| Result | A new process exists (Concept 16) | The process's code/data are ready to run (Section 6, 7) | Instructions are actually carried out, eventually reaching application code (Section 12) |

**A required, explicit clarification:** these three phases happen in roughly this order (launch →
loading → execution) as part of the one overall conceptual sequence (Section 2's diagram) — they
are not independent, unrelated events.

### The Startup Timeline

A concise conceptual timeline, numbering the same sequence introduced above:

```text
1. Program/executable exists on storage.
2. User/program requests launch.
3. Operating system handles the request.
4. A process is created.
5. Process resources/address space are established.
6. Executable information/code/data are made available to the process.
7. Required runtime/dependencies are prepared where applicable.
8. Initial execution state/environment is established.
9. CPU begins executing from the relevant entry point.
10. Runtime initialization may occur.
11. Application-level execution begins.
```

**A required, explicit label:**

> This is a conceptual model, not a claim that every operating system or language implementation
> follows these exact eleven steps in this exact form. It exists to give you one coherent,
> memorable timeline tying together every section of this lesson (Sections 3 through 12
> correspond, roughly, to steps 3 through 11 above).

---

## 3. The Launch Request and Operating System

**A launch request** is a request — from a user or from another program — that a specific program
should be started.

**Examples:**

- A **terminal command** — a user typing a command and pressing Enter.
- A **graphical application launch** — a user clicking an icon.
- **Another application launching a program** — one running process requesting that another
  program be started.

**This lesson does not teach shell implementation** — exactly how a terminal/shell interprets what
you type and turns it into a launch request is not covered here; only the general idea that a
launch request exists and must eventually reach the operating system.

**Why the launch request must eventually cause the operating system to establish a running
process.** Recall Concept 16, Section 3: processes are managed by the operating system. Since only
the operating system has the authority and mechanism to actually create a new process (Concept 16),
any launch request — regardless of its origin (terminal, graphical click, or another program) —
must ultimately be communicated to the operating system, which is the only party capable of acting
on it.

**The operating system's conceptual role, developed across Section 4 through Section 8:** once it
receives a launch request, the operating system must arrange the entire execution environment for
the new process — creating it, setting up its resources, loading the executable, and establishing
its initial execution state. **This lesson does not teach detailed kernel implementation** — how
the operating system's internal code actually accomplishes each of these steps — only that these
steps conceptually happen and roughly what each accomplishes.

---

## 4. Process Creation and Initial Setup

**Directly connecting to Concept 16.** Once the operating system receives and acts on a launch
request, a **new process is created** — this is precisely Concept 16, Section 13's "process
creation" step, now given its proper place in the full startup sequence.

**The new process receives an identity** — a **PID** (Concept 16, Section 4) — uniquely
identifying this specific new running instance, distinct from any other process, even another
instance of the exact same program (Concept 16, Section 2's concrete example).

**A required, explicit boundary:**

> This lesson does not teach `fork()`, `exec()`, `clone()`, `wait()`, process groups, or sessions
> — the specific operating-system mechanisms real systems use to actually create processes. Later
> topic — not taught here (Module 0.2 — Operating System Fundamentals).

---

## 5. Executable Loading

**The problem this section solves.** The executable (Section 1) is just stored data sitting on
storage (Concept 11) — inert bytes, per Concept 14's file vocabulary. For the CPU to actually
execute the instructions inside it, those bytes must somehow become available to the newly created
process in a form its execution can actually use.

**Loader — simple meaning:** a loader is the conceptual mechanism (part of the operating system's
responsibility, Section 3) responsible for preparing an executable so it can actually be executed
by a process.

**What loading conceptually involves.** Loading means making the program's executable contents —
its instructions (Concept 7) and associated data (Section 7) — available within the newly created
process's execution environment/address space (Section 6, introduced properly next).

**A required, explicit correction:**

> "The operating system simply copies the entire executable into RAM" is an oversimplification.
> This lesson does not teach the detailed mechanism real loaders use — which may or may not
> involve copying the entire file into RAM all at once, depending on the specific operating system
> and executable format.

**A required, explicit boundary:**

> This lesson does not teach detailed ELF internals, PE internals, relocation algorithms,
> page-table construction, virtual-memory implementation, or loader source code. Later topic — not
> taught here (Module 0.2 and beyond).

---

## 6. The Process Address Space

**The newly started process gets an address space** — recalling Concept 16, Section 5's identical
introduction of process memory — in which its program can actually execute.

**Commonly-described conceptual regions, extending Concept 16, Section 5's list slightly:**

- **Code/text** — holds the process's actual machine-code instructions (Concept 7).
- **Initialized data** — holds program data with known, specific starting values.
- **Uninitialized data/BSS** — holds program data that starts out with a default (commonly zero)
  value, rather than an explicitly specified one.
- **Heap** — holds data requested more dynamically while the program runs (Concept 16, Section 5).
- **Stack** — holds function-call tracking and short-lived local values (Concept 16, Section 5) —
  this lesson does not teach stack-frame mechanics in depth; that's Concept 18's dedicated subject.

### Diagram — Conceptual Process Memory Layout

```text
        Process Address Space
   ┌─────────────────────────────┐
   │  Code/Text (instructions)    │
   ├─────────────────────────────┤
   │  Initialized Data             │
   ├─────────────────────────────┤
   │  Uninitialized Data / BSS      │
   ├─────────────────────────────┤
   │  Heap (grows as needed)         │
   ├─────────────────────────────┤
   │  ...                              │
   ├─────────────────────────────┤
   │  Stack (grows as needed)          │
   └─────────────────────────────┘
```

> Simplified conceptual diagram — not a claim about exact memory addresses, layout order, or
> growth direction on any specific real system; those vary by architecture and operating system.

**A required, explicit boundary, restated firmly:**

> This lesson does not teach page tables, the TLB, page faults, virtual-to-physical address
> translation, memory-mapping internals, or allocator internals. Later topic — not taught here.

### Comparison Table — Storage vs. Process Memory

| Property | Storage (Concept 11) | Process memory (this section) |
|---|---|---|
| What it holds | The executable file, persistently (Concept 14) | The process's active code/data/stack/heap while running |
| Persistent? | Yes | No — exists only while the process runs (Concept 16, Section 9) |
| Created when? | Independent of any particular launch | Established specifically as part of this lesson's startup sequence (Section 2) |
| Relationship | The source the loader (Section 5) reads from | The destination the loader prepares for the process to actually execute from |

---

## 7. Code, Data, and Runtime Dependencies

**An executable can contain more than instructions.** Recalling Concept 7's instruction/machine-
code vocabulary, an executable file (Concept 14) commonly contains, conceptually:

- **Executable instructions** — the actual machine code (Concept 7) the CPU will execute.
- **Initialized data** — data values built into the executable, ready to be placed into the
  process's memory (Section 6).
- **Metadata** — information *about* the executable itself (recalling Concept 14, Section 6's
  contents-vs-metadata distinction) — for example, the entry point information Section 9
  introduces, genuinely observed in this lesson's Section 14 practical work.
- **References to required components** — information indicating what other components this
  executable depends on in order to run correctly, introduced properly next.

**Some programs depend on runtime components or shared libraries** that are not physically part of
the executable file itself, but must be available for the program to actually run correctly.

**Examples, kept conceptual:**

- **Dynamically linked native programs** — programs (commonly written in languages like C) that
  rely on separate, shared library files, prepared and made available at startup time rather than
  being fully self-contained.
- **Language runtimes** — some languages require a runtime system to be present and initialized
  before program logic can execute (Section 13 develops this further).
- **Interpreter/runtime environments** — recalling Concept 8's compilation-vs-interpretation
  vocabulary directly; an interpreted or bytecode-based program depends on its interpreter/runtime
  being available.

**Why required components may need to be available before application code can execute normally.**
If a program's logic depends on functionality provided by a separate component (a shared library,
a runtime), that component generally needs to be located and made ready *before* the program's own
logic can correctly begin — otherwise, the program would attempt to use functionality that isn't
actually present yet.

**This lesson's own genuinely observed practical work (Section 14) demonstrates this directly** —
inspecting a real executable's dynamic library dependencies with `ldd`.

### Comparison Table — Code vs. Data vs. Runtime Dependencies

| Category | What it is | Example (conceptual) |
|---|---|---|
| Code | Machine-code instructions (Concept 7) | The compiled logic of the program itself |
| Data | Values built into the executable | A constant, a fixed configuration value |
| Runtime dependencies | Other components the program needs to run correctly | A shared library, a language runtime |

**A required, explicit boundary, firmly restated:**

> This lesson does not repeat Concept 7's full machine-code lesson, and does not teach dynamic
> linking internals, relocation processing, symbol resolution algorithms, PLT/GOT internals,
> loader implementation, or ABI internals. Later topic — not taught here (well beyond Stage 0).

---

## 8. Initial Execution State and Environment

**Before application code executes, the process needs an initial execution environment
established** — several pieces of information and state that must exist before the entry point
(this section's next topic, Section 9) can begin.

**Conceptual components of this initial state:**

- **Initial instruction location / entry point** — where execution should actually begin (Section
  9 develops this fully).
- **Initial stack** — the process's stack region (Section 6) must exist and be ready before
  execution begins.
- **Environment information** — data about the process's environment, made available to it
  (Section 11 develops this fully).
- **Command-line arguments** — values provided when the program was launched (Section 11).
- **Environment variables** — separate configuration-style values available to the process
  (Section 11).

**A required, explicit boundary:**

> This lesson does not teach calling conventions or detailed stack-frame mechanics — how,
> precisely, values are arranged on the stack, or how a function call physically works at the
> register/stack level. Later topic — not taught here (Concept 18).

---

## 9. The Entry Point

**Entry point — simple meaning:** the specific location in an executable's code where the CPU
begins executing instructions when the process starts.

**A required, explicit, central correction — one of the most important ideas in this lesson:**

> The CPU does not simply "start at the first line the programmer wrote." The executable has an
> entry point from which execution begins — and that entry point is not necessarily the
> programmer's familiar `main` function.

**This lesson's own genuinely captured practical evidence (Section 14) demonstrates this
concretely** — a real executable inspected with `readelf -h` shows an actual **"Entry point
address"** field, a real, concrete piece of metadata (Section 7) recorded in the executable itself,
confirming that "where execution starts" is a specific, defined property of the executable — not
simply "wherever the programmer's source code visually begins."

**Why language/runtime startup code may execute before the application's familiar `main`
function.** For many compiled languages, the actual entry point the CPU begins executing at
belongs to startup/runtime machinery (Section 10 develops this fully) — code responsible for
setting up the initial execution state (Section 8) — which, once finished, then calls the
programmer's `main` function. The entry point and `main` are related but are not necessarily the
same location.

### Comparison Table — Entry Point vs. Main Function

| Property | Entry point | `main` function (or equivalent) |
|---|---|---|
| What it is | The specific location where CPU execution actually begins (recorded as metadata, Section 7) | The programmer's familiar starting point for application logic |
| Always the same location? | Yes, for a given executable — it's a fixed property recorded in the executable | Depends on the language/execution model (Section 13) |
| Executes runtime setup first? | Often, for native/compiled programs (Section 10) | No — represents the application's own logic, generally after setup is complete |

**A required, explicit boundary:**

> This lesson does not teach detailed function-call mechanics. Later topic — not taught here
> (Concept 18).

---

## 10. Runtime Startup Before Application Code

**The conceptual difference this section establishes:**

```text
program startup machinery
      vs.
application-level code
```

**For a native (compiled) program**, there can be **startup/runtime initialization** — code that
runs at the entry point (Section 9), preparing the initial execution state (Section 8) — before
the programmer's own `main` application logic actually begins.

**For managed/interpreted languages**, the startup path can involve an **interpreter/runtime**
(Concept 8) that must itself start up and initialize before it can begin executing the program's
own source-level logic.

**A required, explicit example, carefully labeled — these are examples of different execution
models, not a claim that "language X always works this way":**

- **C** — commonly, an example of a compiled, native-executable language, where entry-point startup
  code runs before `main`.
- **Python** — commonly, an example where a Python implementation's runtime/interpreter (Concept
  8, Section 7-9's original discussion) must start up before your Python source-level code actually
  begins executing.
- **Java** — commonly, an example involving a virtual machine (Concept 8, Section 6's "Bytecode +
  Virtual Machine" model) that must start up before your Java application code begins.

**A required, explicit, firm correction:**

> Do not claim that all languages start identically. "Programming language" and "execution
> strategy" are not the same thing (recalling Concept 8, Section 8's identical principle: "the
> implementation determines how a language is executed"). Different implementations can use native
> machine code, bytecode, interpreters, JIT compilation, virtual machines, or combinations of
> these — and this affects exactly what "runtime startup" looks like for that specific
> implementation.

**This lesson does not teach JIT internals** — mentioned here only by name, recalling Concept 8's
identical boundary.

---

## 11. Arguments, Environment Variables, and Initial Input

**Building directly on Section 8's brief introduction of this initial state — now developed
fully, and connecting directly to Concept 15.**

**Command-line arguments** — values provided when the program was launched, commonly following the
program's name on a command line (for example, a filename or option the program should use). These
are a form of **program/API input**, recalling Concept 15, Section 3's input-category vocabulary
directly.

**Environment variables** — separate, named configuration-style values made available to a
process's environment (Section 8), independent of any arguments explicitly provided at launch.

**Initial input** — more generally, any data made available to the process as part of its startup
environment, before its own application logic begins reading further input (Concept 15) during
its ordinary execution.

**A required, explicit connection to Concept 15:** command-line arguments and environment
variables are both examples of **input** in Concept 15's general sense (data entering a
system/program) — they simply arrive at a different point (startup, as part of the initial
execution state, Section 8) than input a program might read later during its ordinary execution
(such as from stdin, a file, or a network connection, per Concept 15's fuller treatment).

### Comparison Table — Command-Line Arguments vs. Standard Input vs. Environment Variables

| Property | Command-line arguments | Standard input (stdin, Concept 15) | Environment variables |
|---|---|---|---|
| When provided | At launch time, as part of the launch request (Section 3) | During execution, as a stream the program reads from (Concept 15, Section 10) | At launch time, as part of the initial execution state (Section 8) |
| Typical use | Telling the program specifically what to do this run (e.g., a filename) | Providing data for the program to process | Providing broader configuration/context (e.g., system-wide or session-wide settings) |
| Is it a stream? | No — a fixed set of values provided once, at startup | Yes (Concept 15, Section 10) | No — a fixed set of named values provided once, at startup |

**A required, explicit correction:**

> "Command-line arguments are the same as stdin" is incorrect — they are two different input
> mechanisms (this table's explicit distinction). A program can receive a filename as a
> command-line argument while separately reading that file's actual content via stdin or file I/O
> (Concept 14, Concept 15) — two independent channels.

**A required, explicit correction:**

> "Environment variables are files automatically read by every program" is incorrect —
> environment variables are pieces of environment information made available to a process at
> startup (Section 8); they are not files, and not every program necessarily reads or uses them.

**A required, explicit boundary:**

> This lesson does not teach shell parsing in depth — exactly how a shell (Section 3) interprets
> and splits what you type into individual command-line arguments — or environment-variable
> implementation internals. Later topic — not taught here (Module 0.3 — Command Line, and Module
> 0.2).

---

## 12. From Startup to Application Execution

**The full transition, tying every previous section together into one coherent sequence:**

```text
stored executable (Section 1, Concept 11/14)
      ↓
launch (Section 3)
      ↓
process (Section 4; Concept 16)
      ↓
memory/environment setup (Section 6, Section 8, Section 11)
      ↓
entry point (Section 9)
      ↓
runtime initialization where applicable (Section 10)
      ↓
application execution
```

**Once execution reaches the program's application-level logic** — the programmer's own code,
whether that's C's `main`, Python's top-level script logic, or Java's `main` method — the startup
sequence this entire lesson has described is, conceptually, complete.

**A required, explicit, forward-looking connection:**

> Once execution reaches application-level logic, later concepts explain what happens when
> individual functions execute. Concept 18 — What Happens When a Function Executes — is not taught
> here; this lesson stops at the boundary where application execution begins, exactly as required.

---

## 13. Native vs Interpreted/Managed Startup Models

**Building directly on Section 11's C/Python/Java examples, now organized into a comparison.**

### Diagram — Native vs. Interpreted/Managed Conceptual Startup Paths

```text
Native (e.g., C), conceptually:

executable → entry point → runtime/startup code → main() → application logic


Interpreted/managed (e.g., Python), conceptually:

executable/launcher → runtime/interpreter starts → interpreter reads/executes
source-level code → application logic


Bytecode + VM (e.g., Java), conceptually:

executable/launcher → JVM starts → JVM loads/executes bytecode → main() → application logic
```

> Simplified conceptual diagrams — labeled examples of different execution models (recalling
> Concept 8's identical labeling requirement), not universal descriptions of "how C/Python/Java
> always work" in every possible implementation.

### Comparison Table — Native vs. Interpreted/Managed Startup

| Property | Native (e.g., C) | Interpreted/Managed (e.g., Python, Java) |
|---|---|---|
| What starts at the entry point | Compiled startup/runtime code (Section 10, 11) | A launcher, which starts an interpreter or virtual machine (Concept 8) |
| Is there an extra runtime layer? | Minimal — mostly direct machine-code execution after startup | Yes — an interpreter or VM mediates execution (Concept 8, Section 6) |
| Application code form | Already machine code (Concept 7) | Source or bytecode, executed/interpreted by the runtime (Concept 8) |

### Comparison Table — Startup Phase vs. Application Execution Phase

| Property | Startup phase | Application execution phase |
|---|---|---|
| What happens | Process creation, loading, memory/environment setup, entry point, runtime initialization (Sections 3–11) | The programmer's own logic actually running |
| Who/what is primarily responsible | Operating system, loader, runtime/interpreter (Section 3, 5, 11) | The application code itself |
| Covered in depth by | This lesson (Concept 17) | Concept 18 (function execution) and beyond — not taught here |

### Comparison Table — What the OS Does vs. What the CPU Does vs. What the Program Does

| Actor | Role during startup |
|---|---|
| Operating system | Receives the launch request (Section 3), creates the process (Section 4), arranges loading (Section 5) and the address space (Section 6), establishes initial execution state (Section 8) |
| CPU | Executes instructions (Concept 2, Concept 7) — beginning at the entry point (Section 9) once the OS has prepared everything, and continuing through runtime startup (Section 10) and into application code |
| Program (the executable itself) | Provides the actual instructions, data, and dependency information (Section 7) that the OS loads and the CPU executes |

---

## 14. Practical Linux/WSL2 Program-Startup Observation

As with every prior concept file, this section is safe, uses only harmless, read-only
observations plus one self-created, harmless background process for demonstration, requires no
`sudo`, never modifies system files, never kills arbitrary processes, and never fabricates output.
Reminder of your environment:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu
```

**Checking command availability first.** Every command below (`file`, `ldd`, `readelf`, `ps`,
`sleep`, `time`) was confirmed available in the environment used to prepare this lesson via
`which`. **The output shown below is genuinely observed** — captured by actually running these
commands. **Your own output will very likely differ (library paths, addresses, PIDs) — treat the
output below as this lesson's own observed example.**

**Step A — identify a harmless, already-installed executable to inspect.** `/bin/sleep` (the
standard Linux "wait for a given time" utility) is used here — a small, harmless, universally
available executable, ideal for safe observation.

**Step B — observe the file type.**

```bash
file /bin/sleep
```

*Observed output from this WSL2 environment:*

```text
/bin/sleep: symbolic link to ../lib/cargo/bin/coreutils/sleep
```

*What this demonstrates:* `file` (recalling Concept 14, Concept 11's identical use) confirms
what this path actually is — here, a symbolic link (a filesystem-level alias, mentioned only by
name) pointing to the real executable file. This is a small, real example of Section 1's point
that "program file" isn't always as simple as one single, direct file.

**Step C — observe dynamic library dependencies.**

```bash
ldd /bin/sleep
```

*Observed output from this WSL2 environment:*

```text
	linux-vdso.so.1 (0x00007183289ae000)
	libselinux.so.1 => /usr/lib/x86_64-linux-gnu/libselinux.so.1 (0x000071832896b000)
	libgcc_s.so.1 => /usr/lib/x86_64-linux-gnu/libgcc_s.so.1 (0x000071832893d000)
	libm.so.6 => /usr/lib/x86_64-linux-gnu/libm.so.6 (0x0000718327cda000)
	libc.so.6 => /usr/lib/x86_64-linux-gnu/libc.so.6 (0x0000718327a00000)
	/lib64/ld-linux-x86-64.so.2 (0x00007183289b0000)
	libpcre2-8.so.0 => /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 (0x0000718327c2e000)
```

*What this demonstrates:* `ldd` lists the shared libraries (Section 8's "dynamic dependencies")
this specific executable depends on — a direct, concrete, real confirmation that even a small
program like `sleep` relies on several separate library components being available at startup,
exactly matching Section 8's conceptual point. **This lesson does not explain what each specific
library does, or how this resolution mechanism works internally** — only that this dependency list
genuinely exists and is observable.

**Step D — observe executable metadata, including the entry point.**

```bash
readelf -h /bin/sleep
```

*Observed output from this WSL2 environment:*

```text
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              DYN (Position-Independent Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x107fe0
  Start of program headers:          64 (bytes into file)
  Start of section headers:          11350176 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         15
  Size of section headers:           64 (bytes)
  Number of section headers:         34
  Section header string table index: 33
```

*What this demonstrates, focusing only on the fields relevant to this lesson:* **ELF** is a common
Linux executable format (mentioned here only by name, per this lesson's Executable Format
Boundary). The **"Entry point address: 0x107fe0"** field is a direct, genuine, real confirmation of
Section 10's central point — this executable has a specific, recorded entry point address, a fixed
property of the file itself, not "wherever the source code visually starts." **This lesson does
not explain the other fields** (program headers, section headers, and so on) in any depth — those
belong to advanced executable-format material, explicitly out of scope.

**Step E — start a harmless background process and observe it.** Following this lesson's
recommended workflow, start a harmless, long-running command such as `sleep 60 &`:

```bash
sleep 60 &
echo "$!"
```

This captures the new process's PID (Concept 16, Section 4) immediately after creation — a direct,
practical link back to Concept 16's process-identity discussion, now observed at the exact moment
of creation this lesson's startup sequence describes.

*Observed output from this WSL2 environment (captured using an equivalent harmless, long-running
command for this specific demonstration — the observable concepts, PID/state/termination, are
identical regardless of which harmless command is used):*

```text
PID: 5218
```

```bash
ps -p 5218 -o pid,ppid,stat,etime,cmd
```

*Observed output:*

```text
    PID    PPID STAT     ELAPSED CMD
   5218    5216 Sl         00:00 tail -f /dev/null
```

*What this demonstrates:* this is Concept 16, Section 14's identical `ps` inspection, now framed
specifically as "the process this lesson's startup sequence just created" — its PID, its parent
PID (PPID), its state, how long it's existed, and its command — all consistent with what Section 4
and Section 9 described conceptually.

**Step F — measure a trivial command's execution, using `time`.**

```bash
{ time -p true; } 2>&1
```

*Observed output from this WSL2 environment:*

```text
real 0.00
user 0.00
sys 0.00
```

*What this demonstrates:* `time` measures how long a command takes to run overall — including,
conceptually, the startup sequence this entire lesson describes (process creation, loading,
initial state setup, entry point, and finally the trivial `true` command's own execution) before
the command completes. **This lesson does not teach detailed timing/benchmarking methodology** —
this is included only to give a small, safe, concrete sense that "starting a program" is real,
measurable work, however brief for a tiny program like `true`.

**Step G — clean up: terminate only the self-created process from Step E.**

```bash
kill 5218
```

**This lesson never kills arbitrary processes** — only the specific, harmless, self-created
process from Step E, identified by its exact PID, exactly matching Concept 16, Section 14's
identical safety practice.

**Required WSL2-specific caveats:**

- These observations were made inside WSL2's Ubuntu Linux environment — library paths, entry-point
  addresses, and PIDs reflect this specific virtualized environment, not necessarily what a native
  Linux installation or the Windows host would show.
- WSL2 exposes a virtualized Linux environment; these observations should not be assumed to
  directly reflect the underlying Windows host's own program-startup behavior, which uses an
  entirely different executable format and operating system (this lesson does not teach Windows
  program-startup specifics).
- Do not assume your own PID, entry-point address, or library paths will match this lesson's
  captured example — these values are specific to the exact environment and moment they were
  captured.

---

## 15. AI Engineering Relevance, Exercises, Review, and Production Context

### AI Engineering Relevance

**A simple conceptual workflow, connecting this lesson's startup sequence to a realistic AI
scenario:**

```text
AI application launch
      ↓
process creation                    (Concept 16; Section 4)
      ↓
configuration/environment setup      (Section 8, Section 11)
      ↓
model/runtime dependencies            (Section 7)
      ↓
model/data loading                     (Concept 11, Concept 14 — happens after
                                         the process itself has started, per Section 12)
      ↓
application initialization              (Section 12)
      ↓
inference/training execution             (application-level code, beyond this lesson's scope)
```

**Why startup time can include substantial work, kept conceptual — this lesson does not teach
Docker, Kubernetes, orchestration, distributed systems, model-serving frameworks, GPU
initialization internals, or CUDA startup internals:**

- **Loading program code** — the executable itself must be loaded (Section 5) before anything
  else can happen.
- **Initializing runtime** — for an AI application built on an interpreted/managed language
  (Section 10, Section 13), runtime startup happens before application code runs.
- **Loading configuration** — reading settings needed for the application to behave correctly
  (Section 8, Section 11; Concept 14).
- **Loading dependencies** — required runtime components (Section 7) must be available.
- **Loading models/data** — a step that happens *after* the process itself has started and
  reached application-level code (Section 12) — this is a separate, later activity from the
  program-startup sequence this lesson describes, not part of the startup sequence itself.

**Conceptual connections — kept at this level only:** AI inference services, training programs,
CLI AI tools, model-serving processes, and worker processes (Concept 16, Section 15's identical
examples) all begin their existence through exactly the startup sequence this lesson describes,
before any of their application-specific AI logic can run.

### Required AI-Engineering Reasoning

1. **Why can an AI application take time to start before processing a request?** Because startup
   involves real work (Sections 4–11) — process creation, loading, runtime initialization, and
   dependency preparation — all of which must complete before application-level code, including
   any request-handling logic, can even begin.
2. **Why is model loading different from starting the executable itself?** Model loading is
   application-level work (Section 12) — it happens *after* the process has been created, loaded,
   and reached its entry point/runtime-initialized state; starting the executable is the OS/loader
   work described in Sections 3–11, which precedes application logic entirely.
3. **Why can an application have a process before the model is fully loaded?** Because process
   creation (Section 4) and executable loading (Section 5) complete *before* application code
   begins running (Section 12) — and model loading is application-level work that happens only
   once that application code is actually executing; the process (Concept 16) exists throughout.
4. **Why can environment variables influence application startup?** Because environment
   information is part of the initial execution state (Section 8, Section 11) made available to a
   process at startup — application code (including runtime initialization, Section 10) can read
   and be configured by these values.
5. **Why can two launches of the same AI application create separate processes?** Because each
   launch triggers its own independent process-creation step (Section 4; Concept 16, Section 2's
   identical point) — each with its own PID and execution context, even though both originate from
   the same executable.
6. **Why can startup work involve both storage I/O and CPU computation?** Loading the executable
   and its dependencies (Section 5, Section 8) involves reading data from storage (Concept 11,
   Concept 15), while establishing execution state and beginning runtime initialization (Section 9,
   Section 11) involves actual CPU computation (Concept 2) — startup is not purely one or the
   other.
7. **Why can a program spend significant time initializing before doing useful application work?**
   Because the full conceptual chain (Section 2, Section 12) — process creation, loading, memory
   setup, dependency preparation, entry point, runtime initialization — must all complete before
   application-level logic (the "useful work" from the application's own perspective) begins at
   all.

### Exercises and Debugging Scenarios

Work through these in order, showing your reasoning for every explanation or comparison — not
just a final answer.

#### Level 1 — Recognition

1. What is a program, in the sense this lesson uses the term?
2. What is an executable?
3. What is a process?
4. What is a launch request?
5. What is a loader?
6. What is a process address space?
7. What is an entry point?
8. What is runtime initialization?
9. What is a command-line argument?
10. What is an environment variable?

#### Level 2 — Understanding

Answer each in your own words, in at least one or two full sentences.

11. Why is a program file not a process?
12. Why does process creation occur during startup?
13. Why is executable loading necessary?
14. Why does the process need an address space?
15. What does an entry point mean?
16. Why is `main` not necessarily the first instruction executed?
17. Why can runtime initialization occur before application code runs?
18. Why may dynamic dependencies need to be prepared before a program runs correctly?
19. Why does startup differ between execution models (native, interpreted, managed)?

#### Level 3 — Application

Apply this lesson's startup model to each scenario, explaining your reasoning.

20. Launching a native (compiled) application.
21. Launching a Python program.
22. Launching a Java program.
23. Launching a command-line tool.
24. Launching an AI application.
25. Starting an application that needs a model file.

#### Level 4 — Debugging

For each scenario, reason through what's happening and why.

26. "The executable exists, so why is there no process?"
27. "A process appears (confirmed via `ps`), but the application has not finished initializing."
28. A user assumes `main` is the first instruction executed by the CPU.
29. "The program starts slowly because dependencies/model files must be prepared" — explain why
    this is a reasonable, expected observation rather than a sign of a problem.
30. "Two launches of the same executable produce two different PIDs" — explain why this is
    expected.
31. "The application receives an environment variable but apparently not stdin" — explain how
    both of these can be true at once, referencing Concept 15.
32. "A native program and a Python program do not have identical startup paths" — explain why.
33. A user assumes the entire executable is simply copied into RAM as a single, complete step.
    Explain why this lesson does not support that specific claim.

#### Level 5 — Integration / AI Engineering

For each scenario, reason about the end-to-end startup sequence using this lesson's full
vocabulary.

34. **AI inference service startup.** Trace the conceptual sequence from launch request through to
    the point where the service is ready to receive requests.
35. **Model-loading startup sequence.** Explain why model loading is a distinct phase from the
    program-startup sequence this lesson describes, and where it fits relative to Section 12's
    "application execution" phase.
36. **Configuration/environment-driven startup.** Explain how environment variables and
    command-line arguments (Section 11) could influence how an AI application behaves once it
    reaches application-level code.
37. **Multiple AI worker processes starting.** Explain why launching several worker processes for
    the same AI application results in several independent processes, each going through its own
    startup sequence.
38. **Startup bottleneck caused by storage/model loading.** Explain, using Concept 12's HDD-vs-SSD
    vocabulary and this lesson's Section 5/8, why a slower storage device could noticeably affect
    how long an AI application takes to become ready.

**Solutions are not provided here.** See
[`exercises/17-what-happens-when-a-program-starts-answer-key.md`](./exercises/17-what-happens-when-a-program-starts-answer-key.md)
— open it only after attempting every question above.

### Common Mistakes and Misconceptions

```text
Misconception 1  → "Launching a program means the CPU immediately runs the first line of source
                    code."
Correct idea     → Execution begins at the executable's entry point (Section 9), which is often
                    not the programmer's first source line at all — startup/runtime code
                    frequently runs first (Section 10).
Example          → This lesson's genuinely observed `readelf -h /bin/sleep` output shows a
                    specific "Entry point address" — a fixed property of the file, unrelated to
                    where the programmer's source code visually begins.
```

```text
Misconception 2  → "A program file is the same thing as a process."
Correct idea     → A program file is stored, inert data (Section 1; Concept 14); a process is a
                    running instance (Concept 16, Section 1) that only exists once the program has
                    actually been launched (Section 2, Section 4).
Example          → `/bin/sleep` exists on storage whether or not any `sleep` process is currently
                    running — Section 14 showed a `sleep`-equivalent process being created and
                    later terminated, while the underlying file was never touched.
```

```text
Misconception 3  → "The executable is loaded directly into the CPU."
Correct idea     → The executable is loaded into the process's address space (Section 5, Section
                    6), which resides in RAM (Concept 10) — the CPU then fetches and executes
                    instructions from there (Concept 2, Concept 7); the executable is not "loaded
                    into" the CPU itself, which has no such large storage capacity (Concept 6's
                    registers are tiny, per Concept 6's own capacity discussion).
Example          → Section 6's memory-layout diagram shows code/data/stack/heap all residing in
                    the process's address space, not inside the CPU.
```

```text
Misconception 4  → "The operating system simply copies the entire executable into RAM."
Correct idea     → This lesson does not teach the detailed loading mechanism (Section 5's
                    explicit correction) — real loading may not involve copying the entire file
                    into RAM all at once; the exact mechanism is later material.
Example          → Section 5 explicitly flags this exact claim as an oversimplification this
                    lesson does not endorse.
```

```text
Misconception 5  → "The first instruction executed is always the programmer's main function."
Correct idea     → The entry point (Section 9), not necessarily `main`, is where execution
                    begins — startup/runtime code frequently executes first, then calls `main`
                    (Section 9's comparison table, Section 10).
Example          → Section 9's Entry Point vs. Main comparison table draws this distinction
                    explicitly.
```

```text
Misconception 6  → "Every program starts in exactly the same way."
Correct idea     → Startup details vary by operating system, executable format, and execution
                    model — native, interpreted, and managed/bytecode approaches all have
                    genuinely different startup paths (Section 13's comparison table), even
                    though they share the same overall conceptual shape (Section 2).
Example          → Section 13's C vs. Python vs. Java diagrams show three different, labeled
                    startup paths, not one universal sequence.
```

```text
Misconception 7  → "An executable contains only machine-code instructions."
Correct idea     → An executable can also contain initialized data, metadata (like the entry
                    point address), and references to required runtime components (Section 7's
                    explicit list).
Example          → Section 14's genuinely observed `readelf -h` output shows metadata (entry
                    point address, header sizes, and more) alongside — not instead of — the
                    actual machine code elsewhere in the file.
```

```text
Misconception 8  → "A process does not need an address space."
Correct idea     → A process requires an address space (Section 6; Concept 16, Section 5) to
                    hold its code, data, stack, and heap — without one, there would be nowhere
                    for its instructions and working data to actually reside for execution.
Example          → Section 6's memory-layout diagram is a direct requirement of any executing
                    process.
```

```text
Misconception 9  → "Program startup and function execution are the same process."
Correct idea     → Program startup (this lesson) is the sequence bringing a process into
                    existence and reaching application-level code (Section 12); function
                    execution (Concept 18, not taught here) is what happens once individual
                    functions within that application code are called and run. These are
                    related but distinct topics, covered in separate, sequential lessons.
Example          → Section 12's explicit forward-reference to Concept 18 marks exactly where
                    this lesson's scope ends and Concept 18's begins.
```

```text
Misconception 10 → "Python programs are directly executed as CPU machine code in the same way as
                    native C executables."
Correct idea     → This directly recalls Concept 8's central corrected oversimplification — a
                    Python implementation commonly involves a runtime/interpreter (Section 11,
                    Section 13) mediating execution, unlike a native C executable's more direct
                    machine-code execution after startup.
Example          → Section 13's native-vs-interpreted/managed comparison table draws this exact
                    distinction.
```

```text
Misconception 11 → "Dynamic libraries are part of the executable's source code."
Correct idea     → Dynamic libraries (Section 7) are separate components the executable depends
                    on and that must be available at startup — they are not compiled into or
                    part of the executable's own source code or file contents.
Example          → Section 14's genuinely observed `ldd /bin/sleep` output lists several
                    separate library files (e.g., `libc.so.6`) that are not part of the `sleep`
                    executable file itself.
```

```text
Misconception 12 → "Command-line arguments are the same as stdin."
Correct idea     → Command-line arguments (Section 11) are values provided at launch time,
                    directly recalling Concept 15, Section 3's "program/API input" category; stdin
                    (Concept 15, Section 10) is a separate stream a program can read from during
                    its execution. They are two different input mechanisms.
Example          → A program can receive a filename as a command-line argument while separately
                    reading its actual content from stdin — two independent input channels
                    (Level 4, debugging scenario 31).
```

```text
Misconception 13 → "Environment variables are files automatically read by every program."
Correct idea     → Environment variables (Section 8, Section 11) are pieces of environment
                    information made available to a process at startup — they are not files, and
                    not every program necessarily reads or uses them.
Example          → Section 8 lists environment information as one of several distinct components
                    of initial execution state, separate from files (Concept 14).
```

```text
Misconception 14 → "Starting a program means it immediately uses a CPU core continuously."
Correct idea     → Directly recalling Concept 16, Section 9's identical, central point: a
                    process can exist without continuously executing on a CPU core — including
                    right after startup, if it quickly enters a waiting/blocked state (Concept
                    16, Section 8).
Example          → Section 14's `time -p true` example shows a trivial program's actual CPU time
                    (`user`/`sys`) being extremely small — most real programs spend at least some
                    time not actively executing, even soon after starting.
```

```text
Misconception 15 → "The OS does not participate after the launch request."
Correct idea     → The operating system participates throughout the entire startup sequence —
                    process creation (Section 4), loading (Section 5), address-space setup
                    (Section 6), and establishing initial execution state (Section 8) — not just
                    at the initial moment the launch request is received (Section 3).
Example          → Section 13's "What the OS Does vs. CPU vs. Program" table shows the OS's role
                    spanning multiple steps of the sequence, not just the very first one.
```

### Review Questions

Answers are intentionally not provided directly below these questions.

1. What does it mean to "start a program," using this lesson's full conceptual sequence?
2. Why is a program file not automatically a process?
3. What role does the operating system play during program startup?
4. What happens during process creation?
5. What does executable loading conceptually involve?
6. What is a process address space, and what does it commonly contain?
7. What is an entry point, and how is it different from `main`?
8. What is runtime initialization, and why can it happen before application code runs?
9. What is the difference between command-line arguments, environment variables, and stdin?
10. Why do native, interpreted, and managed execution models have different startup paths?
11. Why is program startup distinct from function execution?
12. Why does program startup matter to an Applied AI Engineer?

### Production Relevance

You now understand the full conceptual sequence from a stored executable to actual application
execution: the launch request, the operating system's role, process creation, executable loading,
the process address space, code/data/runtime dependencies, initial execution state, the entry
point, runtime startup, and the transition into application-level code — along with how this
sequence varies between native, interpreted, and managed execution models.

**How this connects to your future work:**

- **What Happens When a Function Executes (Concept 18)** — the detailed mechanics of stack frames,
  calling conventions, and function-call execution that this lesson deliberately deferred (Section
  9, Section 10, Section 12).
- **Why RAM and Storage Are Different (Concept 19)** — building further on this lesson's use of
  RAM (process memory, Section 6) and storage (the executable's origin, Section 1, Section 5).
- **Why GPUs Matter for AI (Concept 20)** — building further on how an AI application process might
  eventually initialize and use GPU resources (mentioned only briefly here, per this lesson's
  Strict Boundary).
- **Operating System Fundamentals (Module 0.2)** — the detailed kernel mechanisms
  (`fork()`/`exec()`, page tables, dynamic linking) this lesson deliberately deferred throughout.
- **AI Engineering** — every AI application, service, or worker you build will go through exactly
  this startup sequence before any of its application-specific logic — including model loading —
  can begin (Section 15's AI-engineering relevance discussion).

**A required, final, explicit boundary:**

> This lesson does not teach kernel implementation, ELF/PE format internals, dynamic-linker
> internals, function-call mechanics, or the deeper RAM/storage or GPU/AI material reserved for
> Concepts 19 and 20. What this lesson provides is the conceptual foundation — the startup
> sequence from stored program to running application code — that all of that later material will
> build directly on top of.

---

_This file was written as the completed Concept 17 lesson for Module 0.1. It does not teach
system-call internals, kernel implementation, scheduler algorithms, context switching, interrupts,
virtual-memory implementation, page tables, the TLB, memory-mapping internals, device drivers,
VFS, filesystem internals, IPC, signals, process namespaces, or cgroups (Module 0.2); ELF
section-header internals, program-header internals, relocation tables, symbol-table algorithms,
GOT/PLT, ABI internals, linker implementation, or loader implementation (executable-format
internals); dynamic-linking internals, relocation processing, symbol-resolution algorithms, or
JIT internals; stack-frame internals, function-call mechanics, calling conventions, return-address
mechanics, or recursion internals (Concept 18); the deeper RAM/storage material reserved for
Concept 19; GPU architecture, CUDA, kernels, tensor cores, GPU memory hierarchy, or distributed
training (Concept 20); or Docker, Kubernetes, orchestration, distributed systems, or model-serving
frameworks — in depth. Those remain scaffolded, unwritten concept files (or entirely untouched, in
the case of later-stage or later-module material) until their own turn in the sequence. Concepts
18 through 20 specifically are the next lessons in this module, and none of them are taught here._
