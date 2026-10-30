# CPU Cores

**Module:** Stage 0 — Computer & Digital Foundation
**Topic:** How Computers Work

This lesson explains what CPU cores are, why CPUs contain multiple cores, how they improve performance, and why understanding them matters for Data Engineering and AI Engineering.

---

## 1. What Is a CPU Core?

A **CPU core** is an independent execution unit inside a CPU that can fetch, decode, and execute instructions.

- **CPU:** The overall processing component.
- **Core:** An individual instruction-executing unit inside the CPU.
- **Single-core CPU:** Contains one physical core.
- **Multi-core CPU:** Contains multiple physical cores that can execute independent work simultaneously.

A CPU is not the same as a core. One CPU can contain several cores.

---

## 2. Why Do CPUs Have Multiple Cores?

Making one core increasingly faster requires more power and generates more heat. Eventually, increasing its speed becomes inefficient.

CPU designers therefore began placing multiple cores on one chip to increase the amount of work a computer can perform at once.

Multiple cores can improve performance, run separate programs simultaneously, improve responsiveness, support parallel processing, and sometimes improve energy efficiency.

However, four cores do not automatically make every program four times faster. The program must have work that can be divided, and the benefits must outweigh the overhead of splitting and coordinating that work.

---

## 3. Physical Cores, Logical Processors, Concurrency and Parallelism

- **Physical core:** An actual execution unit manufactured into the CPU chip.
- **Logical processor:** An execution context that the operating system can schedule work onto. One physical core may expose multiple logical processors through a technology called **Simultaneous Multi-Threading (SMT)**, known as **Hyper-Threading** in Intel implementations.

For example, four physical cores may appear as eight logical processors.

- **Concurrency:** Multiple tasks are managed and make progress over time, but they do not necessarily execute at the same instant.
- **Parallelism:** Multiple streams of work execute simultaneously.

A single core can switch rapidly between tasks, creating concurrency without true parallel execution. Multiple cores provide separate physical execution resources, although actual speedup still depends on the workload.

---

## 4. How Do Multiple Cores Work?

Independent tasks can run on separate cores at the same time. For example, four cores can resize four independent image files simultaneously.

But if Task B needs Task A's result before starting, the tasks must run in sequence. Additional cores cannot eliminate that dependency.

The operating system and software determine how work is assigned to cores. Scheduling, threads, processes, and synchronization are covered in later lessons.

---

## 5. Practical Examples for Data and AI Engineering

Multiple cores can help with:

- **Data preprocessing:** Cleaning and transforming independent records or files.
- **Data loading:** Preparing multiple batches of data.
- **API services:** Handling independent user requests.
- **AI orchestration:** Coordinating multiple pipeline activities.
- **Background tasks:** Running logging, monitoring, and maintenance.
- **Model-serving infrastructure:** Managing requests and resources around an AI model.

The benefit depends on whether the work is independent and divisible. More CPU cores may have little effect on heavy numerical computations running on a GPU.

---

## 6. Practical Linux Commands in WSL2

The lesson introduces safe, read-only commands to inspect CPU topology:

| Command | Purpose |
|---|---|
| `lscpu` | Shows logical CPU count, sockets, cores, and threads per core. |
| `nproc` | Shows processing units available to the current process. |
| `grep -c "^processor" /proc/cpuinfo` | Counts logical-processor entries visible to Linux. |
| `lscpu \| grep -E '^(CPU\(s\)\|On-line CPU\(s\) list\|Core\(s\) per socket\|Socket\(s\)\|Thread\(s\) per core)'` | Displays selected CPU topology fields. |
| `which lscpu` | Checks whether `lscpu` is available. |

A useful approximate relationship for a simple, symmetrical CPU topology is:

**Logical processors ≈ sockets × cores per socket × threads per core.**

For example, one socket × four cores × two threads per core = eight logical processors.

> **WSL2 note:** WSL2 runs in a virtualized environment, so its reported CPU counts may differ from Windows. This is not necessarily a hardware problem.

---

## 7. Common Mistakes and Troubleshooting

The lesson explains why:

- CPU and core are different.
- More cores do not guarantee proportional speedup.
- A single core can support concurrency without parallelism.
- Logical processors are not always physical cores.
- GHz alone cannot determine performance.
- More CPU cores do not automatically improve every AI workload.

If a benchmark fails to speed up when additional cores are used, possible reasons include sequential dependencies, coordination overhead, shared memory limitations, small workloads, or software that cannot use multiple cores. Different CPU counts in WSL2 may result from virtualization or processor-availability settings.

---

## 8. Exercises, Review and Production Relevance

The module includes recognition, understanding, command-based observation, debugging, and integration exercises. You practise interpreting CPU topology, explaining unexpected processor counts, and deciding whether additional cores would help image processing, sequential calculations, API requests, or AI preprocessing. A separate answer key is provided.

The expected learning outcome is to explain CPU cores, distinguish physical from logical processors, understand concurrency versus parallelism, inspect your system, and reason about performance.

For production AI systems, core capacity affects throughput, latency, resource utilization, background processing, and model-serving infrastructure. Before adding hardware, engineers should ask: What is the workload? Where is the bottleneck? Can the work be parallelized? What are the overhead and cost?

Advanced profiling, distributed systems, autoscaling, Kubernetes, and detailed CPU architecture remain outside this lesson.

---

## Main Takeaway

More cores provide more potential computing capacity, but actual performance depends on how effectively software can use them.
