# GPU (Graphics Processing Unit)

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 13

---

## 1. What Is a GPU?

A **GPU (Graphics Processing Unit)** is a processor originally designed to render graphics. It is now widely used for AI because it can perform many similar mathematical calculations simultaneously.

A GPU chip is the processor itself, while a graphics card is the complete board containing the GPU, memory, cooling, power delivery, and connectors.

---

## 2. CPU vs. GPU

| CPU | GPU |
|---|---|
| Has relatively few, powerful, flexible cores | Has many parallel execution units |
| Handles varied tasks, decisions, and sequential logic | Excels at many similar, independent calculations |
| Often suited to low-latency tasks | Often suited to high-throughput workloads |
| Primarily uses system RAM | Often uses dedicated VRAM |

Neither processor is universally better. They perform different roles and commonly work together.

---

## 3. Parallelism and GPU Execution

- **Concurrency:** Multiple tasks are managed or progressed.
- **Parallelism:** Multiple tasks execute simultaneously.
- **Data parallelism:** Applying the same or similar operation to many independent data elements at once.

For example, calculating the brightness of millions of image pixels is well suited to GPU parallelism.

GPU work can be conceptually organized into threads, blocks, and grids. These are programming-model concepts, such as those used in CUDA, not universal names for physical GPU components.

---

## 4. GPU Architecture and Memory

GPUs contain many execution resources, registers, and fast nearby memory. Their internal organization varies by manufacturer—for example, NVIDIA uses Streaming Multiprocessors, while AMD uses Compute Units.

- **System RAM:** Main working memory primarily used by the CPU.
- **VRAM (Video RAM):** Memory typically dedicated to a discrete GPU.
- **Memory bandwidth:** How much data can move per unit of time.
- **VRAM capacity:** How much data can fit in GPU memory.

With a discrete GPU, data may need to move from system RAM into VRAM before computation. Transfer time and limited VRAM can become bottlenecks.

Integrated GPUs share system memory in many configurations. Discrete GPUs are separate chips that typically have dedicated VRAM, greater compute capacity, and higher power and cost requirements.

---

## 5. GPU Performance

Important measurements include compute throughput, memory bandwidth, VRAM capacity, latency, and utilization.

More GPU cores or VRAM does not automatically mean faster performance. Likewise, 100% utilization means the GPU is busy, not necessarily that the workload is optimal.

---

## 6. Practical Linux/WSL2 Observation

The module introduces safe, read-only commands:

- `uname -a` — inspect the environment.
- `which lspci`, `which nvidia-smi`, `which lshw`, `which glxinfo` — check tool availability.
- `lshw -C display` — inspect exposed display hardware.
- `ls /sys/class/drm` — inspect graphics-related kernel interfaces.

Do not install missing tools just for this lesson. WSL2 may expose virtualized GPU information rather than a complete description of the physical Windows GPU.

---

## 7. GPUs in AI Engineering

AI training, inference, embeddings, and tensor operations often involve extensive matrix and numerical calculations that benefit from parallel execution.

A simplified workflow is:

```
Storage → system RAM → CPU prepares data → GPU VRAM → GPU computation → results return to system RAM
```

Choose CPU, GPU, or both by considering workload parallelism, data-transfer overhead, memory requirements, latency, hardware availability, and cost.

---

## 8. Exercises, Production Relevance, and Scope

The module contains 45 exercises, including recognition, conceptual understanding, workload selection, debugging misconceptions, VRAM constraints, and AI engineering scenarios. Answers are in `exercises/13-gpu-answer-key.md`. Review questions reinforce the key concepts.

These fundamentals support future decisions about model training and inference, hardware selection, memory limits, and cost-performance trade-offs.

**Out of scope:** CUDA programming, PyTorch/TensorFlow GPU programming, neural-network mathematics, Tensor Cores, GPU optimization, profiling, multi-GPU systems, and distributed training. These are later topics.

---

## Next Concept

**Concept 14 — Files.** Concept 20 — Why GPUs Matter for AI will explore AI-specific GPU concepts in greater depth.
