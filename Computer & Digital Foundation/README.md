# Stage 0 — Computer & Digital Foundations

**Status:** Repository scaffolded. Teaching has not started.
**Roadmap source:** `Applied_AI_Engineering_Roadmap_Updated.md`, Section 3 — "Stage 0 — Computer &
Digital Foundations"

## What Stage 0 is

Stage 0 is the foundation layer of the entire Applied AI Engineering roadmap. Before writing a
single line of application code, this stage builds an accurate mental model of what a computer
actually is and how it behaves: the hardware that does the work, the operating system that
manages it, the command line used to control it, and the developer environment used to build
software on it.

This repository assumes **no prior computer science or IT background**. Every concept is
introduced from first principles.

## Why Stage 0 comes before programming

The roadmap's learning philosophy is:

> Fundamentals → implementation → systems → AI/ML → LLMs → agents → production → architecture → specialization

Programming, backend engineering, machine learning, and AI systems all sit on top of the same
underlying machine and operating system behavior. Without Stage 0:

- Error messages, crashes, and performance problems are opaque.
- "Why is my program slow?", "why did it run out of memory?", and "why does permission matter?"
  have no grounding.
- Later stages (OS internals, concurrency, GPU training, model serving, containers, cloud
  deployment) all assume this foundation already exists.

Stage 0 exists so every later stage can be understood mechanically, not just followed by rote.

## The four modules

| Module | Folder | Focus |
|---|---|---|
| 0.1 | [`01-How-Computers-Work/`](./01-How-Computers-Work/README.md) | Hardware and the physical/logical basis of computing: CPU, memory, storage, GPU, binary, machine code, processes |
| 0.2 | [`02-Operating-System-Fundamentals/`](./02-Operating-System-Fundamentals/README.md) | How an OS manages programs and resources: kernel, processes, threads, memory, filesystems, permissions, signals, shell |
| 0.3 | [`03-Command-Line/`](./03-Command-Line/README.md) | Practical command-line fluency: navigation, file operations, search, text processing, pipes, redirection, scripting |
| 0.4 | [`04-Developer-Environment/`](./04-Developer-Environment/README.md) | Setting up and using a real development environment: VS Code, IDE concepts, virtual environments, Python tooling |

## Learning sequence

Modules are designed to be learned in order, since each builds on the previous one:

1. **0.1 How Computers Work** — the physical machine (hardware, binary, execution model).
2. **0.2 Operating System Fundamentals** — how software controls that machine (processes, memory,
   permissions, the shell).
3. **0.3 Command Line** — the practical skill of operating the OS directly.
4. **0.4 Developer Environment** — setting up the tools used to write and run code going forward.

Within each module, work through the numbered concept files in order, then complete that
module's `labs/`, `exercises/`, and `project/` material before moving to the next module.

## Prerequisites

None. Stage 0 assumes zero prior computer science or IT background. A computer running Linux,
Ubuntu, or WSL2 (Windows Subsystem for Linux) is required for the hands-on labs.

## Expected outcomes

By the end of Stage 0, the learner should be able to:

- Explain the major computer components and how they relate (CPU, RAM, storage, GPU).
- Explain binary, bits, bytes, and hexadecimal.
- Explain what happens when a program starts and when a function executes.
- Explain processes and basic OS behavior at a mechanical level.
- Use the Linux command line confidently for navigation, file management, search, and text
  processing.
- Inspect running processes and system resources (CPU, memory, file descriptors).
- Work correctly with files and permissions.
- Understand and use environment variables.
- Set up and use a working Python developer environment (VS Code, virtual environments, uv/pip,
  pyproject.toml).
- Connect all of the above to how a Python service or AI application will behave in later stages.

## Stage completion criteria

Stage 0 is **not** complete just because the material has been read. See
[`00-Stage-0-Overview/stage-gate.md`](./00-Stage-0-Overview/stage-gate.md) for the explicit,
demonstrable completion gate. Progress toward each item is tracked in
[`00-Stage-0-Overview/progress-tracker.md`](./00-Stage-0-Overview/progress-tracker.md).

## Project/lab progression

Each module ends with hands-on practice, increasing in practical weight:

- **0.1** — build a binary/decimal/hex converter, a memory-size calculator, and a simple
  CPU-bound workload benchmark.
- **0.2** — complete the practical Linux/process lab (`ps`, `top`/`htop`, `kill`, signals, file
  descriptors, `/proc`, CPU/memory inspection, exit codes, permissions, resource limits) and be
  able to explain what a running Python service is doing at the OS level.
- **0.3** — apply the command-line toolset together in a small scripted practice task.
- **0.4** — set up a real, correctly structured Python project as the environment used going
  forward into Stage 1.

## Overview and tracking

See [`00-Stage-0-Overview/`](./00-Stage-0-Overview/README.md) for the learning plan, progress
tracker, stage-completion gate, and glossary.
