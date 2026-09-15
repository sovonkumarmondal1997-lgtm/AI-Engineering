# Module 0.1 — How Computers Work

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.1 — "How
Computers Work"

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

## 5. Why this module matters for AI engineering

Every later stage of the roadmap — operating systems, the command line, Python, backend services,
databases, model training, model serving, and agent engineering — runs on top of the mechanics
this module introduces. Concretely:

- **CPU, cores, and instructions** explain why some workloads (data preprocessing, tokenization)
  are CPU-bound and why single-threaded Python code doesn't automatically use every core.
- **Cache, RAM, and storage** explain why loading a large model or dataset is slow the first time,
  why out-of-memory errors happen, and why RAM and disk are not interchangeable.
- **The GPU** explains, at a mechanical level, why training and running neural networks is fast on
  a GPU and slow on a CPU — the basis for every later discussion of model training and inference
  cost.
- **Binary, hexadecimal, files, and I/O** explain how data is actually represented and moved,
  which underlies file formats, serialization, and network payloads used throughout AI systems.
- **Program start-up and function execution** give you the mental model needed to read a stack
  trace, understand a crash, or reason about why a Python script behaves the way it does before you
  have learned to write Python yourself.

Without this module, later error messages, memory limits, and performance problems have no
mechanical explanation — you would be memorizing fixes instead of understanding causes.

## 6. Practical verification and projects

This module no longer keeps its own local `labs/`, `exercises/`, `examples/`, `project/`, or
`concept-dependencies.md` — the practical, verifiable work for all of Stage 0, including this
module, is now consolidated in the Stage 0 roadmap. See
[`../00-Stage-0-Overview/learning-plan.md`](../00-Stage-0-Overview/learning-plan.md) for:

- the audit evidence used to verify Module 0.1 is operational, not just read (Section 2 —
  "Audit of the original four modules");
- Projects 0.1–0.5, which build the practical, version-controlled proof of this foundation
  (Section 5 — "Practical projects"); and
- the Stage 0 completion gate that this module feeds into (Section 8 — "Stage 0 completion gate").

## 7. Projects

This module has one local, hands-on project: a practical audit of program execution and GPU
relevance. See [`Projects/README.md`](./Projects/README.md) for the index, and
[`Projects/01-program-execution-and-gpu-audit.md`](./Projects/01-program-execution-and-gpu-audit.md)
to run a small Python example, observe it as a real process, and explain — from launching a Python
command to seeing output — why GPUs help with parallel tensor operations.

---

_This README defines structure and sequence only. No lesson content has been written. Each
numbered concept file is a scaffold — see the file itself for its current status._
