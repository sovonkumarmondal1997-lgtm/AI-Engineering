# Module 0.1 — Concept Dependency Map

**Status:** Reference document. Not a lesson.

This file exists so the learner always knows: *"learn this concept first because it makes the
next concept easier to understand."* It is a map of prerequisites, not a summary of content — see
[`README.md`](./README.md) for the numbered learning sequence these dependencies produce.

An arrow (`↓`) means "must be reasonably understood before the concept below it will make sense."
Concepts on the same horizontal tier have no dependency on each other and can be learned in either
order.

---

## Full dependency graph

```text
Motherboard & Buses
        ↓
       CPU
        ↓
      Cores
        ↓
Bits, Bytes & Binary
        ↓
   Hexadecimal
        ↓
    Registers
        ↓
Instructions & Machine Code
        ↓
Compilation & Interpretation
        ↓
   ┌────┴────┐
  Cache      RAM
   └────┬────┘
        ↓
   ┌────┴────┐
 Storage   HDD vs SSD
   └────┬────┘
        ↓
       GPU
        ↓
   ┌────┴────┬────────┐
 Files    Input/Output  │
   └────┬────┴────────┘
        ↓
     Processes
        ↓
What Happens When a Program Starts
        ↓
What Happens When a Function Executes
        ↓
   ┌────┴────────────────────┐
Why RAM & Storage Are Different   Why GPUs Matter for AI
```

## Why each dependency exists

| Concept | Depends on | Reason |
|---|---|---|
| CPU | Motherboard & Buses | The CPU is one component connected to everything else via the motherboard's buses — understanding the whole board first gives the CPU a physical context. |
| Cores | CPU | A core is a physical execution unit *inside* a CPU — cores cannot be explained before the CPU itself. |
| Bits, Bytes & Binary | (none — first abstract concept) | The starting point for all information representation; nothing later in this module can be explained numerically without it. |
| Hexadecimal | Bits, Bytes & Binary | Hex is a compact notation *for* binary — it only makes sense as shorthand once binary itself is understood. |
| Registers | Bits, Bytes & Binary, CPU | Registers store binary values inside the CPU — both binary and the existence of a CPU are required first. |
| Instructions & Machine Code | Registers, Bits, Bytes & Binary | An instruction is a binary-encoded operation that reads/writes registers — cannot be explained before either exists conceptually. |
| Compilation & Interpretation | Instructions & Machine Code | Both are processes that turn source code into (or execute it as) machine code/instructions — meaningless before "machine code" is defined. |
| Cache | Compilation & Interpretation, Registers | Cache sits between registers and RAM in the memory hierarchy; understanding registers first makes "faster than RAM, slower than registers" concrete. |
| RAM | Cache | RAM is introduced as the next, larger, slower tier after cache — the hierarchy is easiest to grasp in that order. |
| Storage | Cache, RAM | Storage is contrasted directly against memory (cache/RAM) — the contrast is the point, so memory must come first. |
| HDD vs SSD | Storage | This is a comparison *within* the storage concept — general storage must be understood before comparing two implementations of it. |
| GPU | Storage, HDD vs SSD, CPU, Cores | The GPU is best understood by contrast with the CPU (many simple cores vs few complex cores) and after the full memory/storage picture exists. |
| Files | GPU | Not a technical dependency — files are introduced here because the module now shifts from *hardware* to *what software operates on*, right after hardware is complete. |
| Input/Output | Files | I/O is the general mechanism of moving data in and out of a program; files are the most concrete/familiar example of I/O, so introducing files first grounds the abstraction. |
| Processes | Files, Input/Output | A process is a running program that reads/writes files and performs I/O — both must exist as concepts first. |
| What Happens When a Program Starts | Processes, Instructions & Machine Code, Compilation & Interpretation | This is a narrative walkthrough that uses processes, machine code, and compilation/interpretation together — all three must already be understood. |
| What Happens When a Function Executes | What Happens When a Program Starts, Registers | Function execution (call stack, arguments, return) is a zoomed-in view of what's already running as a process, and uses registers to pass/return values. |
| Why RAM and Storage Are Different | RAM, Storage, What Happens When a Program Starts | This is a synthesis question — it requires both concepts individually plus an understanding of how a running program actually uses them. |
| Why GPUs Matter for AI | GPU, What Happens When a Function Executes | Requires understanding what the GPU physically is, plus enough of the execution model to explain *why* parallel execution helps AI workloads specifically. |

## How to use this map

1. Follow the numbered sequence in [`README.md`](./README.md) — it already respects every
   dependency above.
2. If a concept feels confusing, check this table for what it depends on and confirm that
   prerequisite is actually solid before continuing.
3. Concepts in the same tier (e.g. Cache/RAM, Storage/HDD vs SSD, Files/Input-Output) can be
   studied in either order relative to each other, but both must precede the tier below.

---

_This is a planning document, produced during repository preparation. It contains no lesson
content._
