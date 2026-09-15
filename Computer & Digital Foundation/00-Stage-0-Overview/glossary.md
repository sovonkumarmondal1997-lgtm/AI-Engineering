# Stage 0 Glossary

**Status:** Not Started — no terms defined yet.

This is a running glossary of every term introduced across Stage 0's four modules, listed here so
definitions can be added progressively as each concept is actually taught. Definitions are added
here only once they've been covered in the corresponding concept file — this list is a term
index, not a substitute for the full concept files.

Terms are grouped by the module that introduces them.

## Module 0.1 — How Computers Work

Definitions are intentionally not filled in yet — see the note at the top of this file. Each row
below only records where the term is taught and what must be understood first. The full
dependency reasoning (not just the list) lives in
[`../01-How-Computers-Work/concept-dependencies.md`](../01-How-Computers-Work/concept-dependencies.md).

| Term | Where it appears | Prerequisite concept(s) |
|---|---|---|
| Motherboard | [`01-motherboard-and-buses.md`](../01-How-Computers-Work/01-motherboard-and-buses.md) | — |
| Buses | [`01-motherboard-and-buses.md`](../01-How-Computers-Work/01-motherboard-and-buses.md) | Motherboard |
| CPU | [`02-cpu.md`](../01-How-Computers-Work/02-cpu.md) | Motherboard, Buses |
| Cores | [`03-cores.md`](../01-How-Computers-Work/03-cores.md) | CPU |
| Binary | [`04-binary-bits-and-bytes.md`](../01-How-Computers-Work/04-binary-bits-and-bytes.md) | — |
| Bits and bytes | [`04-binary-bits-and-bytes.md`](../01-How-Computers-Work/04-binary-bits-and-bytes.md) | Binary |
| Hexadecimal | [`05-hexadecimal.md`](../01-How-Computers-Work/05-hexadecimal.md) | Binary, Bits and bytes |
| Registers | [`06-registers.md`](../01-How-Computers-Work/06-registers.md) | Binary, CPU |
| Instructions | [`07-instructions-and-machine-code.md`](../01-How-Computers-Work/07-instructions-and-machine-code.md) | Registers, Binary |
| Machine code | [`07-instructions-and-machine-code.md`](../01-How-Computers-Work/07-instructions-and-machine-code.md) | Registers, Binary |
| Compilation | [`08-compilation-and-interpretation.md`](../01-How-Computers-Work/08-compilation-and-interpretation.md) | Instructions, Machine code |
| Interpretation | [`08-compilation-and-interpretation.md`](../01-How-Computers-Work/08-compilation-and-interpretation.md) | Instructions, Machine code |
| Cache | [`09-cache.md`](../01-How-Computers-Work/09-cache.md) | Compilation, Interpretation, Registers |
| RAM | [`10-ram.md`](../01-How-Computers-Work/10-ram.md) | Cache |
| Storage | [`11-storage.md`](../01-How-Computers-Work/11-storage.md) | Cache, RAM |
| HDD vs SSD | [`12-hdd-vs-ssd.md`](../01-How-Computers-Work/12-hdd-vs-ssd.md) | Storage |
| GPU | [`13-gpu.md`](../01-How-Computers-Work/13-gpu.md) | Storage, HDD vs SSD, CPU, Cores |
| Files | [`14-files.md`](../01-How-Computers-Work/14-files.md) | (sequence position after GPU; no technical dependency) |
| Input/output | [`15-input-output.md`](../01-How-Computers-Work/15-input-output.md) | Files |
| Processes | [`16-processes.md`](../01-How-Computers-Work/16-processes.md) | Files, Input/output |
| What happens when a program starts | [`17-what-happens-when-a-program-starts.md`](../01-How-Computers-Work/17-what-happens-when-a-program-starts.md) | Processes, Instructions, Machine code, Compilation, Interpretation |
| What happens when a function executes | [`18-what-happens-when-a-function-executes.md`](../01-How-Computers-Work/18-what-happens-when-a-function-executes.md) | What happens when a program starts, Registers |
| Why RAM and storage are different | [`19-why-ram-and-storage-are-different.md`](../01-How-Computers-Work/19-why-ram-and-storage-are-different.md) | RAM, Storage, What happens when a program starts |
| Why GPUs matter for AI | [`20-why-gpus-matter-for-ai.md`](../01-How-Computers-Work/20-why-gpus-matter-for-ai.md) | GPU, What happens when a function executes |

## Module 0.2 — Operating System Fundamentals

kernel · user space · system calls · processes · threads · scheduling · virtual memory ·
filesystems · permissions · environment variables · signals · standard input/output · pipes ·
shell · process lifecycle · Linux · Ubuntu · WSL2 · Bash · PowerShell

## Module 0.3 — Command Line

`pwd` · `ls` · `cd` · `cp` · `mv` · `rm` · `mkdir` · `cat` · `less` · `head` · `tail` · `grep` ·
`find` · `sort` · `uniq` · `cut` · `xargs` · pipes · redirection · environment variables ·
shell scripts · permissions · Bash · Git Bash · WSL2 · PowerShell

## Module 0.4 — Developer Environment

VS Code · terminal · IDE concepts · extensions · formatters · linters · debugger · virtual
environments · package managers · project structure · `uv` · `pip` · `venv` · `pyproject.toml`

---

Each term above will get a short definition here (with a link to its full concept file) as it is
taught. Until then, this file exists only as an index of what Stage 0 will define.
