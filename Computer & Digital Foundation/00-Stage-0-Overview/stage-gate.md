# Stage 0 Completion Gate

**Status:** Not passed — Stage 0 not started.

Reading the material is not sufficient to pass this gate. Every item below must be genuinely
**demonstrable** (explain out loud / in writing, or perform live at the terminal) before Stage 0
is considered complete and Stage 1 begins.

This gate is derived strictly from the roadmap's Stage 0 scope and the completion requirements
defined when this repository was set up. Do not check anything off automatically — each box is
checked only after real demonstration.

## Conceptual understanding

- [ ] Explain the major computer components and how they relate: CPU, cores, RAM, cache,
      storage, HDD vs SSD, GPU, motherboard, buses.
- [ ] Explain the CPU/RAM/storage/GPU relationship — what each does, why they're separate, and
      how data moves between them.
- [ ] Explain binary, bits, bytes, and hexadecimal, and convert between them by hand.
- [ ] Explain instructions, machine code, compilation, and interpretation, and how they differ.
- [ ] Explain what happens when a program starts, from launch to a running process.
- [ ] Explain what happens when a function executes (call stack, arguments, return).
- [ ] Explain why RAM and storage are different and why both are necessary.
- [ ] Explain why GPUs matter for AI workloads specifically.

## Operating system understanding

- [ ] Explain the difference between kernel and user space.
- [ ] Explain what a system call is and give an example.
- [ ] Explain processes vs threads, and how scheduling works at a basic level.
- [ ] Explain virtual memory at a conceptual level.
- [ ] Explain how filesystems and permissions work on Linux.
- [ ] Explain environment variables and where they come from.
- [ ] Explain signals and how a process can be interrupted or terminated.
- [ ] Explain standard input/output and pipes.
- [ ] Explain the process lifecycle from creation to exit, including exit codes.

## Command-line fluency

- [ ] Navigate the filesystem confidently (`pwd`, `ls`, `cd`).
- [ ] Create, copy, move, and delete files/directories (`mkdir`, `cp`, `mv`, `rm`) without
      hesitation or looking up syntax for basic cases.
- [ ] View and inspect file contents (`cat`, `less`, `head`, `tail`).
- [ ] Search file contents and the filesystem (`grep`, `find`).
- [ ] Use `sort`, `uniq`, `cut`, and `xargs` to process text.
- [ ] Chain commands with pipes and use redirection (`>`, `>>`, `<`).
- [ ] Read, set, and use environment variables from the shell.
- [ ] Write and run a basic shell script.
- [ ] Read and modify file permissions.

## Practical OS/process inspection

- [ ] Use `ps` and `top`/`htop` to inspect running processes.
- [ ] Send signals to a process and use `kill` correctly.
- [ ] Inspect a process's open file descriptors.
- [ ] Use `/proc` to inspect a running process.
- [ ] Inspect CPU and memory usage on the system.
- [ ] Read and interpret a process's exit code.
- [ ] Inspect and explain a process's resource limits.
- [ ] Complete the practical Linux/process lab
      (`02-Operating-System-Fundamentals/labs/linux-process-lab.md`).

## Developer environment

- [ ] Explain core IDE concepts: extensions, formatters, linters, debugger.
- [ ] Set up and use a Python virtual environment.
- [ ] Explain the difference between `uv`, `pip`, `venv`, and `pyproject.toml`, and use them to
      set up a project.
- [ ] Set up and navigate a clean, correctly structured Python project in VS Code.

## Practical builds

- [ ] Built and can explain a binary/decimal/hex converter.
- [ ] Built and can explain a memory-size calculator.
- [ ] Built and can explain a simple CPU-bound workload benchmark.
- [ ] Completed the command-line practice project (Module 0.3).
- [ ] Completed the first Python project setup (Module 0.4).

## Integration check

- [ ] Explain, end to end, what a running Python service is doing at the OS level (processes,
      memory, file descriptors, system calls) — the explicit goal of Module 0.2.
- [ ] Explain the relationship between Stage 0 concepts (hardware, OS, command line, dev
      environment) and the Python/AI engineering work that begins in Stage 1 and continues
      through later stages (e.g., why process/memory concepts matter for model serving, why
      binary/hex matters for debugging, why the shell matters for automation and deployment).

---

**Stage 0 is complete only when every box above is checked and can be demonstrated on request —
not merely recognized from having read the material.**
