# Stage 0 Learning Plan

**Status:** Not Started

This is the recommended sequence through Stage 0. It follows the module order in the roadmap
(0.1 → 0.2 → 0.3 → 0.4), since each module depends on concepts introduced in the previous one.

## Sequence

### Step 1 — Module 0.1: How Computers Work

Path: [`../01-How-Computers-Work/`](../01-How-Computers-Work/README.md)

Work through the numbered concept files in order, following the 9-stage beginner sequence defined
in the module's own README (physical computer → information representation → CPU execution →
memory → storage → GPU → program execution → software execution concepts → AI relevance):

```text
01-motherboard-and-buses.md → 02-cpu.md → 03-cores.md
    → 04-binary-bits-and-bytes.md → 05-hexadecimal.md
    → 06-registers.md → 07-instructions-and-machine-code.md → 08-compilation-and-interpretation.md
    → 09-cache.md → 10-ram.md
    → 11-storage.md → 12-hdd-vs-ssd.md
    → 13-gpu.md
    → 14-files.md → 15-input-output.md → 16-processes.md
    → 17-what-happens-when-a-program-starts.md → 18-what-happens-when-a-function-executes.md
    → 19-why-ram-and-storage-are-different.md → 20-why-gpus-matter-for-ai.md
```

See [`../01-How-Computers-Work/concept-dependencies.md`](../01-How-Computers-Work/concept-dependencies.md)
for why this specific order was chosen. After the concept files, complete the module's `labs/`
(system information, memory and storage, CPU observation, program execution observation), then
`exercises/` (Levels 1–5), then the `project/` folder (binary/decimal/hex converter, memory-size
calculator, CPU-bound benchmark).

### Step 2 — Module 0.2: Operating System Fundamentals

Path: [`../02-Operating-System-Fundamentals/`](../02-Operating-System-Fundamentals/README.md)

Work through the numbered concept files in order, then complete the practical Linux/process lab
in `labs/linux-process-lab.md`. This module's goal — explaining what a running Python service is
doing at the OS level — depends directly on Module 0.1's understanding of processes, memory, and
execution.

### Step 3 — Module 0.3: Command Line

Path: [`../03-Command-Line/`](../03-Command-Line/README.md)

Work through the numbered concept files in order. This module is heavily hands-on — most of the
learning happens by running commands, not reading about them. Complete the practice project at
the end.

### Step 4 — Module 0.4: Developer Environment

Path: [`../04-Developer-Environment/`](../04-Developer-Environment/README.md)

Work through the numbered concept files in order, then set up a real Python project using the
project folder as a guide. This produces the working development environment that Stage 1
(Programming Foundations) will be built in.

## After Stage 0

Once every item in [`stage-gate.md`](./stage-gate.md) can genuinely be demonstrated, Stage 0 is
complete and Stage 1 — Programming Foundations can begin, with its own root folder created inside
`AI Engineering/` at that time.

## Notes

- Do not skip ahead to later modules before earlier ones are understood — each module in Stage 0
  assumes the previous one.
- Concept files, labs, exercises, and the project are tracked individually in
  [`progress-tracker.md`](./progress-tracker.md).
