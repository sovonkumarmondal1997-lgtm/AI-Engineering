# Stage 0 — Computer, Linux, and Developer Foundations

**Status:** In progress. Modules 01–04 have full lesson content and a hands-on Projects folder
each; the Stage 0 overview module (00) holds the learning plan and the Stage 0 capstone project.
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations (the audit-and-gap-closure
revision of the original Stage 0 — Computer & Digital Foundations scope). See
[`00-Stage-0-Overview/learning-plan.md`](./00-Stage-0-Overview/learning-plan.md) for the full,
authoritative plan.

## What Stage 0 is

Stage 0 is the foundation layer of the entire Applied AI Engineering roadmap. Before writing a
single line of application code, this stage builds an accurate mental model of what a computer
actually is and how it behaves: the hardware that does the work, the operating system that manages
it, the command line used to control it, and the developer environment used to build software on
it — plus the practical habits every later project depends on: version control with Git and GitHub,
local networking for development, reproducible Python workspaces, secrets and local security
hygiene, and evidence-based debugging.

This repository assumes **no prior computer science or IT background**. Every concept is
introduced from first principles.

## Why Stage 0 comes before programming

The roadmap's learning philosophy is:

> Fundamentals → implementation → systems → AI/ML → LLMs → agents → production → architecture → specialization

Programming, backend engineering, machine learning, and AI systems all sit on top of the same
underlying machine, operating system, and developer-environment behavior. Without Stage 0:

- Error messages, crashes, and performance problems are opaque.
- "Why is my program slow?", "why did it run out of memory?", and "why does permission matter?"
  have no grounding.
- Git, secrets, reproducibility, and debugging feel like separate "extra" skills instead of the
  same discipline applied everywhere.
- Later stages (OS internals, concurrency, GPU training, model serving, containers, cloud
  deployment) all assume this foundation already exists.

Stage 0 exists so every later stage can be understood mechanically, not just followed by rote.

## Modules 00–04

| Module | Folder | Focus |
|---|---|---|
| 00 | [`00-Stage-0-Overview/`](./00-Stage-0-Overview/README.md) | Planning and the Stage 0 capstone: the learning plan, the audit of Modules 01–04, Gaps 0A–0F, Projects 0.1–0.5, and the Stage 0 completion gate |
| 01 | [`01-How-Computers-Work/`](./01-How-Computers-Work/README.md) | Hardware and the physical/logical basis of computing: CPU, memory, storage, GPU, binary, machine code, processes — 20 topics, plus a program-execution-and-GPU-audit project |
| 02 | [`02-Operating-System-Fundamentals/`](./02-Operating-System-Fundamentals/README.md) | How an OS manages programs and resources, plus local networking for development: kernel, processes, threads, memory, filesystems, permissions, signals, shell, ports — 16 topics, plus a process/resource/port-diagnosis project |
| 03 | [`03-Command-Line/`](./03-Command-Line/README.md) | Practical command-line fluency, safe filesystem habits, quoting, and standard streams: navigation, file operations, search, text processing, pipes, redirection, scripting — 12 topics, plus a shell file-and-stream investigation project |
| 04 | [`04-Developer-Environment/`](./04-Developer-Environment/README.md) | A real developer environment: VS Code, the debugger, reproducible Python with `uv`, Git/GitHub/SSH basics, secrets and local security hygiene, evidence-based debugging — 13 topics, plus two projects (environment health check, Python workspace bootstrap) |

Together, these modules develop **computer, Linux/operating-system, command-line,
developer-environment, Git and version-control, local-networking, reproducibility, security and
secrets, and evidence-based-debugging** foundations — the complete Stage 0 scope.

## Learning sequence

Modules 01–04 are designed to be learned in order, since each builds on the previous one; Module 00
is planning and reference material you return to throughout, not a module to "finish" before
starting 01:

1. **01 — How Computers Work** — the physical machine (hardware, binary, execution model).
2. **02 — Operating System Fundamentals** — how software controls that machine (processes, memory,
   permissions, the shell), plus local networking for development.
3. **03 — Command Line** — the practical skill of operating the OS directly, plus safe filesystem
   habits, quoting, and standard streams.
4. **04 — Developer Environment** — setting up the tools used to write and run code going forward,
   plus Git/GitHub, reproducible Python workspaces, secrets hygiene, and evidence-based debugging.

Within each of Modules 01–04, work through the numbered topic files in order, then complete that
module's own `Projects/` folder before moving to the next module. Once all four are complete, finish
with Module 00's capstone project (Section "Project progression" below).

## Prerequisites

None. Stage 0 assumes zero prior computer science or IT background. A computer running Linux,
Ubuntu, or WSL2 (Windows Subsystem for Linux) is required for the hands-on projects, alongside
familiarity with Windows PowerShell for cross-platform comparison.

## Expected outcomes

By the end of Stage 0, the learner should be able to:

- Explain the major computer components and how they relate (CPU, RAM, storage, GPU), and explain
  binary, bits, bytes, and hexadecimal.
- Explain what happens when a program starts and when a function executes, and explain processes
  and basic OS behavior at a mechanical level.
- Use the Linux command line confidently for navigation, file management, search, text processing,
  quoting, and standard streams.
- Inspect running processes and system resources (CPU, memory, file descriptors), and diagnose a
  local port conflict.
- Work correctly with files and permissions, and understand and use environment variables.
- Set up and use a working Python developer environment (VS Code, the debugger, `uv`,
  `pyproject.toml`) reproducibly.
- Use Git and GitHub for basic version control without exposing secrets, and apply local security
  hygiene (`.env`, `.gitignore`, credential rotation).
- Diagnose a small local-environment failure methodically, using evidence rather than assumption,
  and document it.
- Connect all of the above to how a Python service or AI application will behave in later stages.

See [`00-Stage-0-Overview/learning-plan.md`](./00-Stage-0-Overview/learning-plan.md), Section 1 —
"Stage outcome," for the full, authoritative version of this list.

## Stage completion criteria

Stage 0 is **not** complete just because the material has been read. See
[`00-Stage-0-Overview/learning-plan.md`](./00-Stage-0-Overview/learning-plan.md), Section 8 —
"Stage 0 completion gate," for the explicit, demonstrable completion criteria.

## Project progression

Each module ends with its own `Projects/` folder — hands-on practice that turns concepts into
evidence:

- **01 — How Computers Work:**
  [`Projects/01-program-execution-and-gpu-audit.md`](./01-How-Computers-Work/Projects/01-program-execution-and-gpu-audit.md) —
  audit program execution from a launched Python command to its output, and explain GPU parallelism
  for tensor operations.
- **02 — Operating System Fundamentals:**
  [`Projects/01-process-resource-and-port-diagnosis.md`](./02-Operating-System-Fundamentals/Projects/01-process-resource-and-port-diagnosis.md) —
  Project 0.3: find, observe, and safely stop a test process, and diagnose a local port.
- **03 — Command Line:**
  [`Projects/01-shell-file-and-stream-investigation.md`](./03-Command-Line/Projects/01-shell-file-and-stream-investigation.md) —
  Project 0.2: investigate a synthetic log directory with `grep`, `sort`, `uniq -c`, and
  redirection.
- **04 — Developer Environment:**
  [`Projects/01-developer-environment-health-check.md`](./04-Developer-Environment/Projects/01-developer-environment-health-check.md) —
  Project 0.1 — and
  [`Projects/02-python-workspace-bootstrap.md`](./04-Developer-Environment/Projects/02-python-workspace-bootstrap.md) —
  Project 0.4: a documented environment baseline, and a minimal, reproducible `uv`-based Python
  project.
- **00 — Stage 0 Overview (capstone):**
  [`Projects/01-stage-0-incident-simulation.md`](./00-Stage-0-Overview/Projects/01-stage-0-incident-simulation.md) —
  Project 0.5: a complete, evidence-based incident investigation and postmortem drawing on Modules
  01–04 together.

## Overview and tracking

See [`00-Stage-0-Overview/`](./00-Stage-0-Overview/README.md) for the single authoritative learning
plan (stage outcome, audit, gaps, tools, projects, engineering-thinking practices, interview
preparation, and the completion gate) and the Stage 0 capstone project.
