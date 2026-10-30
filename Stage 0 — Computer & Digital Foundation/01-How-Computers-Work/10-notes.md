# RAM

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 10

---

## 1. What Is RAM?

**RAM (Random Access Memory)** is the computer's main working memory. It temporarily holds programs and data that are actively being used.

"Random access" means the computer can access a memory location directly without reading all the locations before it. RAM is **volatile**, meaning its contents are lost when power is removed.

Important terms:

- **Capacity:** How much data RAM can hold, commonly measured in GB.
- **Bandwidth:** How much data can move to or from RAM per unit of time.
- **Latency:** How long an individual memory access takes to begin producing a result.

---

## 2. Why Does RAM Exist?

Persistent storage, such as an SSD or HDD, retains data long-term but is slower to access. RAM provides faster working space for active programs and data.

The simplified memory hierarchy is:

```
Storage → RAM → Cache → Registers → CPU
```

Moving closer to the CPU generally means smaller capacity and faster access.

---

## 3. Why RAM Matters for Applied AI Engineers

RAM is a limited resource used by:

- Python programs and their execution state.
- Datasets being processed.
- Preprocessing steps that create additional data structures.
- Model loading and inference services.
- Multiple applications or jobs running concurrently.

AI workloads may be **memory-bound** (limited by memory capacity or data access) rather than **compute-bound** (limited by computational capacity). More RAM does not automatically make every workload faster.

---

## 4. How RAM Works

When a program runs, relevant instructions and data are made available through the memory system. When the CPU needs data, the cache hierarchy may satisfy the request; otherwise, the request reaches RAM.

A **memory address** identifies a particular location in memory. This lesson introduces addresses conceptually, not virtual addressing or address translation.

---

## 5. RAM, Cache, Registers and Storage

| Component | Main purpose |
|---|---|
| Registers | Hold immediate CPU values and state |
| Cache | Keep useful data and instructions close to the CPU |
| RAM | Hold active programs and working data |
| SSD/HDD | Retain data persistently |

RAM is volatile; storage generally retains data without power. Neither replaces the other.

---

## 6. Capacity, Bandwidth and Latency

These are separate properties. High capacity does not guarantee high bandwidth or low latency. More RAM helps primarily when insufficient memory is limiting the workload.

Installed RAM is not all available to one program because the operating system and other applications also consume memory.

---

## 7. Practical Linux/WSL2 Commands

```bash
uname -a
free -h
free
cat /proc/meminfo
lscpu
```

- `free -h` displays memory figures in human-readable units.
- `free` shows raw values.
- `/proc/meminfo` provides detailed memory information.
- `MemTotal` is visible total memory; `MemFree` is completely unused memory; `MemAvailable` estimates memory available for new workloads.
- `buff/cache` and `Cached` refer to OS-level file caching in RAM, not CPU hardware cache.
- Swap uses storage as a memory-pressure fallback; it is not equivalent to physical RAM.

> WSL2 may report different memory values from Windows because it runs in a virtualized environment. These commands are read-only observations, not advanced performance measurements.

---

## 8. Common Mistakes and Troubleshooting

RAM is not permanent storage, cache is faster than RAM, and free memory is not the only useful availability measure. More RAM does not guarantee better performance, and losing RAM contents when power is removed is normal. Differences between Windows and WSL2 memory reports may be expected.

---

## 9. Exercises and Practical Task

The module includes recognition, understanding, application, debugging and integration exercises, including Python datasets, AI preprocessing, memory pressure and WSL2 observations. There are 57 numbered exercise questions and 15 review questions.

Inspect your system with the commands above, record total/free/available memory, cache-related fields and swap values, and explain what the results do and do not prove. Do not stress-test memory or modify repository projects.

---

## 10. Production Relevance and Scope

RAM knowledge supports reasoning about datasets, preprocessing, Python applications, model loading, inference and concurrent workloads. Advanced memory optimization, virtual memory internals, paging, allocators, garbage collection, DRAM circuitry, GPU memory and distributed memory are outside this lesson's scope.

---

## Next Concept

**Concept 11 — Storage**
