# Concept 20: Why GPUs Matter for AI

**Module:** Stage 0 — Module 0.1: How Computers Work | Final concept of Module 0.1

This lesson explains why GPUs are useful for AI, how CPUs and GPUs cooperate, when GPU acceleration helps, and why it is not always the best choice. It builds on the previous concepts, especially Concept 13 (GPU) and Concept 19 (Why RAM and Storage Are Different).

---

## 1. Why AI Benefits from GPUs

A CPU has a smaller number of powerful, flexible cores, making it well suited to sequential tasks, decision-making, branching logic, and application coordination.

A GPU has many execution units designed to handle large amounts of similar work in parallel. AI frequently performs repeated numerical calculations on large collections of numbers, so this architecture can accelerate many AI workloads.

The key idea is **data parallelism**: applying the same or similar operation to many independent pieces of data at once. AI often uses matrix and tensor operations, which can contain many such calculations.

---

## 2. How CPUs and GPUs Work Together

A typical AI workflow looks like this:

```
Storage → System RAM → CPU preparation → GPU memory → GPU computation → CPU/application → Output
```

- **Storage:** Keeps datasets, model files, configuration files, and checkpoints persistently.
- **RAM:** Holds active data for the running application.
- **CPU:** Starts and coordinates the application, reads data, prepares inputs, makes decisions, and manages output.
- **GPU memory (VRAM):** Holds data needed for GPU computation in a typical discrete-GPU system.
- **GPU:** Performs suitable, compute-intensive parallel operations.
- **Output and storage:** Results are returned, displayed, logged, or saved.

Data transfer between RAM and GPU memory takes time and can affect overall performance. GPU memory, system RAM, and storage are distinct resources.

---

## 3. Training vs. Inference

| Activity | Main purpose | Common performance priority |
|---|---|---|
| Training | Repeatedly adjusts a model using data | Throughput—processing large amounts of work efficiently |
| Inference | Uses a trained model to generate a result | Latency for individual requests, or throughput for large batches |

Both can benefit from GPUs, but GPU acceleration is not guaranteed to help every workload.

---

## 4. When Should You Use a GPU?

A GPU is more likely to help when computation is substantial, highly parallel, repeated across large amounts of data, and worth the transfer cost.

CPU-only execution may be better for small scripts, file operations, complex branching, lightweight models, or latency-sensitive individual requests.

Before choosing a GPU, assess:

- How much computation is required?
- Can operations run independently in parallel?
- How much data must move between memory pools?
- Is latency or throughput more important?
- Is suitable GPU hardware available, and does the performance justify its cost and complexity?

More GPU cores do not automatically mean faster AI. A GPU does not understand AI; its benefit comes from the match between the workload and its architecture.

---

## 5. Practical Learning, Exercises, and Production Relevance

The module demonstrates read-only Linux/WSL2 checks using `uname -a`, `which`, `lscpu`, `free -h`, `lshw -C display`, and `ls /sys/class/drm`. The example environment did not have `nvidia-smi` or `lspci` installed and exposed a virtualized rendering interface. This is an environment-specific observation, not proof that every WSL2 machine lacks GPU access.

The lesson contains five worked examples: image-classification inference, model training, data cleaning, voice-assistant inference, and a small configuration script. It also includes 39 exercises across five levels, 14 review questions, eight troubleshooting scenarios, and expected learning outcomes.

For production AI engineering, these concepts help with compute selection, performance troubleshooting, memory-capacity planning, data-transfer costs, latency and throughput decisions, and infrastructure cost control.

The lesson intentionally leaves CUDA, neural-network mathematics, GPU profiling, distributed training, PyTorch/TensorFlow internals, and production GPU deployment for later stages.

---

## 6. Final Takeaway: The Complete Module

Module 0.1 connects the motherboard, CPU, machine instructions, memory hierarchy, storage, files, input/output, processes, program execution, and GPU acceleration into one mental model:

> An AI application runs as software in processes, receives data, moves it through storage and memory, uses CPUs and sometimes GPUs for computation, and produces outputs.

Concept 20 completes Module 0.1. The next material moves to Module 0.2 — deeper operating-system concepts.
