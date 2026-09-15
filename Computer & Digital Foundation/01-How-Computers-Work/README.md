# Module 0.1 — How Computers Work

**Status:** Not Started
**Roadmap source:** `Applied_AI_Engineering_Roadmap_Updated.md`, Stage 0 — Module 0.1 — "How Computers Work"

This README is a **roadmap and navigation document only**. It defines what this module covers, in
what order, and why — it does not contain the lessons themselves. Lesson content is written later,
inside each numbered concept file, during the actual teaching phase.

---

## 1. Module purpose

Module 0.1 builds an accurate mental model of what a computer physically is and how it turns
electricity into running software. It is the first module of Stage 0 and assumes **zero prior
computer science, IT, or programming background**.

Everything in later stages — operating systems, the command line, programming, backend systems,
databases, machine learning, and LLM/agent engineering — sits on top of the concepts introduced
here. Without this module, error messages, crashes, memory limits, and performance problems have
no mechanical explanation.

## 2. Prerequisites

None. This module is the entry point of the entire roadmap. A computer running Linux, Ubuntu, or
WSL2 (Windows Subsystem for Linux) is required for the hands-on labs and projects, but no prior
knowledge of it is assumed.

## 3. Learning objectives

By the end of Module 0.1, the learner should be able to:

- Describe the physical components of a computer (motherboard, buses, CPU, cores) and how they
  are connected.
- Explain binary, bits, bytes, and hexadecimal, and convert between them by hand.
- Explain what a CPU instruction is, what machine code is, and the difference between compiled
  and interpreted execution.
- Explain the memory hierarchy: cache, RAM, and how they relate to CPU speed.
- Explain storage (including HDD vs SSD) and why it is distinct from memory.
- Explain what a GPU is and how it differs structurally from a CPU.
- Explain files, input/output, and processes at a conceptual level.
- Narrate, end to end, what happens when a program starts and when a function executes.
- Explain why RAM and storage are different and why both are necessary.
- Explain why GPUs matter specifically for AI workloads.

## 4. Learning sequence

Concepts are ordered in **9 stages**, moving from the physical machine to abstract software
behavior to AI relevance. Each stage assumes only what came before it — nothing later in the list
is required to understand something earlier.

```text
Physical Computer
      ↓
Information Representation
      ↓
CPU Execution
      ↓
Memory
      ↓
Storage
      ↓
GPU
      ↓
Program Execution
      ↓
Software Execution Concepts
      ↓
AI Relevance
```

### Stage 1 — Physical Computer

The machine as physical hardware — what it's made of, before explaining how it "thinks."

| # | File | Concept(s) covered |
|---|---|---|
| 1 | [`01-motherboard-and-buses.md`](./01-motherboard-and-buses.md) | motherboard, buses |
| 2 | [`02-cpu.md`](./02-cpu.md) | CPU |
| 3 | [`03-cores.md`](./03-cores.md) | cores |

### Stage 2 — Information Representation

How computers represent information at all. Required before CPU execution can make sense, because
instructions and data are both just numbers in a specific base.

| # | File | Concept(s) covered |
|---|---|---|
| 4 | [`04-binary-bits-and-bytes.md`](./04-binary-bits-and-bytes.md) | binary, bits and bytes |
| 5 | [`05-hexadecimal.md`](./05-hexadecimal.md) | hexadecimal |

### Stage 3 — CPU Execution

Now that binary/hex are understood, explain how the CPU actually executes: where it stores
working values, what an instruction is, and how source code becomes something the CPU can run.

| # | File | Concept(s) covered |
|---|---|---|
| 6 | [`06-registers.md`](./06-registers.md) | registers |
| 7 | [`07-instructions-and-machine-code.md`](./07-instructions-and-machine-code.md) | instructions, machine code |
| 8 | [`08-compilation-and-interpretation.md`](./08-compilation-and-interpretation.md) | compilation, interpretation |

### Stage 4 — Memory

The fast, volatile layer the CPU works from directly.

| # | File | Concept(s) covered |
|---|---|---|
| 9 | [`09-cache.md`](./09-cache.md) | cache |
| 10 | [`10-ram.md`](./10-ram.md) | RAM |

### Stage 5 — Storage

The slower, persistent layer, and why it's built differently from memory.

| # | File | Concept(s) covered |
|---|---|---|
| 11 | [`11-storage.md`](./11-storage.md) | storage |
| 12 | [`12-hdd-vs-ssd.md`](./12-hdd-vs-ssd.md) | HDD vs SSD |

### Stage 6 — GPU

A structurally different processor, introduced after the CPU/memory/storage model is solid so it
can be understood by contrast.

| # | File | Concept(s) covered |
|---|---|---|
| 13 | [`13-gpu.md`](./13-gpu.md) | GPU |

### Stage 7 — Program Execution

The OS-adjacent concepts needed to describe a running program: what it reads/writes and what a
process is. (Full OS depth is Module 0.2 — only the foundational concepts belong here.)

| # | File | Concept(s) covered |
|---|---|---|
| 14 | [`14-files.md`](./14-files.md) | files |
| 15 | [`15-input-output.md`](./15-input-output.md) | input/output |
| 16 | [`16-processes.md`](./16-processes.md) | processes |

### Stage 8 — Software Execution Concepts

Two narrative "walkthroughs" that tie every prior concept together end to end.

| # | File | Concept(s) covered |
|---|---|---|
| 17 | [`17-what-happens-when-a-program-starts.md`](./17-what-happens-when-a-program-starts.md) | what happens when a program starts |
| 18 | [`18-what-happens-when-a-function-executes.md`](./18-what-happens-when-a-function-executes.md) | what happens when a function executes |

### Stage 9 — AI Relevance

Why this entire module matters specifically for AI/ML engineering work later in the roadmap.

| # | File | Concept(s) covered |
|---|---|---|
| 19 | [`19-why-ram-and-storage-are-different.md`](./19-why-ram-and-storage-are-different.md) | why RAM and storage are different |
| 20 | [`20-why-gpus-matter-for-ai.md`](./20-why-gpus-matter-for-ai.md) | why GPUs matter for AI |

## 5. Concept dependencies

A full dependency graph (which concepts must be understood before which) is maintained separately
in [`concept-dependencies.md`](./concept-dependencies.md). Read it alongside this sequence if the
reasoning behind the ordering above isn't obvious.

## 6. Practical labs

Located in [`labs/`](./labs/README.md). Labs give hands-on, observational practice with real
hardware/OS information (inspecting CPU, memory, and storage on an actual machine) without
requiring programming knowledge yet.

| Lab | Focus |
|---|---|
| [`01-system-information-lab.md`](./labs/01-system-information-lab.md) | Identifying real hardware (CPU, cores, RAM, storage, GPU) on your own machine |
| [`02-memory-and-storage-lab.md`](./labs/02-memory-and-storage-lab.md) | Observing memory vs storage behavior and capacity |
| [`03-cpu-observation-lab.md`](./labs/03-cpu-observation-lab.md) | Observing CPU activity under load |
| [`04-program-execution-observation-lab.md`](./labs/04-program-execution-observation-lab.md) | Observing a program launch and run as a process |

## 7. Exercises

Located in [`exercises/`](./exercises/README.md). Organized into 5 increasing levels (Recognition
→ Understanding → Application → Debugging → Integration), covering every concept in this module.

## 8. Examples

Located in [`examples/`](./examples/README.md). An index of beginner-friendly real-world
scenarios (opening an app, saving a file, running a Python program, GPU-based AI inference) that
will be used to illustrate concepts during teaching.

## 9. Projects

Located in [`project/`](./project/). Three practical builds required by the roadmap:

| Project | Builds on |
|---|---|
| [`01-binary-decimal-hex-converter/`](./project/01-binary-decimal-hex-converter/README.md) | Binary, bits/bytes, hexadecimal |
| [`02-memory-size-calculator/`](./project/02-memory-size-calculator/README.md) | Binary/bytes, RAM, cache, storage |
| [`03-cpu-bound-benchmark/`](./project/03-cpu-bound-benchmark/README.md) | CPU, cores, instructions, processes |

## 10. Completion criteria

Module 0.1 is complete only when every item in Stage 0's
[`stage-gate.md`](../00-Stage-0-Overview/stage-gate.md) under "Conceptual understanding" and the
first three "Practical builds" rows can be genuinely demonstrated — not merely read. Progress
toward each concept, lab, exercise group, and project is tracked in
[`00-Stage-0-Overview/progress-tracker.md`](../00-Stage-0-Overview/progress-tracker.md).

---

_This README defines structure and sequence only. No lesson content has been written. Each
numbered concept file is a scaffold — see the file itself for its current status._
