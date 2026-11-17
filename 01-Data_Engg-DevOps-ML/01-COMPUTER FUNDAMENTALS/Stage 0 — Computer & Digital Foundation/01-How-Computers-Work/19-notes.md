# Concept 19: Why RAM and Storage Are Different

**Module:** Stage 0 — Module 0.1: How Computers Work

This lesson connects earlier concepts—CPU, cache, RAM, storage, files, processes, program startup, and function execution—to explain why computers need both RAM and storage.

---

## 1. RAM vs. Storage

| Property | RAM | Storage (SSD/HDD) |
|---|---|---|
| Purpose | Holds data actively being used | Saves data for long-term use |
| Persistence | Volatile; loses contents when power is removed | Non-volatile; retains data without power |
| Typical speed | Faster access | Slower access |
| Capacity | Generally smaller | Generally larger |
| Examples | Active program data, working model state | Files, datasets, installed programs, model checkpoints |

Both hold bytes, but they serve different purposes. Performance comparisons are general tendencies: actual latency and bandwidth depend on the hardware and workload.

---

## 2. Why Computers Need Both

One technology cannot practically optimize equally for extreme speed, long-term persistence, large capacity, and low cost. RAM prioritizes fast working access; storage prioritizes persistence and capacity.

Think of a filing cabinet as storage and a desk as RAM. The cabinet keeps documents for the long term, while the desk holds what you are currently working on. Cache is like a nearby tray, and CPU registers are like items in your hands. This is an analogy, not how the hardware literally operates.

---

## 3. How They Work Together

The simplified data hierarchy is:

```
Storage → RAM → Cache → Registers → CPU execution
```

- A program or file exists persistently on storage.
- When launched, the operating system creates a process with its own virtual address space.
- The relevant instructions and data become available in memory as needed.
- The CPU performs calculations using memory, cache, and registers.
- Results that must survive shutdown are written back to storage.

A program file is not the same as a running process. One executable can launch multiple independent processes, each with its own execution state and memory usage. Not every file or executable must be copied entirely into RAM at startup.

---

## 4. Why This Matters in AI Engineering

- **Datasets:** Stored on disk, then made available in memory for processing. Large datasets do not necessarily need to fit entirely in RAM; processing can be incremental.
- **Models:** Checkpoint files live on storage, while actively used model parameters need to be available in RAM and, for GPU workloads, typically GPU memory.
- **Training and inference:** Require active data and model state in memory.
- **Checkpoints and logs:** Must be written to persistent storage to remain available after a process ends or a machine loses power.
- **Configuration files:** Are stored persistently and read into a running process when needed.

---

## 5. Capacity, Performance, and Common Mistakes

**Capacity** measures how much data a resource can hold. **Latency** measures access delay, while **bandwidth** measures how much data can be transferred per unit of time. Therefore, "RAM is faster" is a useful generalization, but the workload and performance measure matter.

Remember:

- More storage does not mean more RAM, and vice versa.
- Free disk space cannot automatically solve an out-of-RAM problem.
- Deleting a file frees storage, not necessarily RAM.
- Closing a program ends its process but does not delete its executable or saved files.
- Swap can use storage as a fallback under memory pressure, but storage does not become equivalent to RAM.

---

## 6. Practical Exercises and Production Relevance

The module demonstrates safe Linux/WSL2 observations using `free -h` for RAM, `df -h` for filesystem space, `lsblk` for visible block devices, `du -sh` for directory usage, and `/proc/PID/status` to inspect a process's approximate resident memory (`VmRSS`). Its example environment showed roughly 3.8 GiB RAM versus nearly 1 TB of storage; these are example readings, not universal specifications.

It includes 37 exercises covering basic definitions, conceptual understanding, practical workflows, debugging, and AI-engineering scenarios, followed by 17 review questions. The production focus is diagnosing RAM-versus-storage constraints, understanding model and dataset workflows, and preserving checkpoints and logs. Advanced virtual-memory internals, filesystem implementation, hardware physics, CUDA, and GPU memory optimization are outside this lesson's scope.

---

## Next Concept

**Concept 20 — Why GPUs Matter for AI**
