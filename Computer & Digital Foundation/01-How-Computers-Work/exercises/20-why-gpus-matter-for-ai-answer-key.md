# Concept 20 — Why GPUs Matter for AI — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../20-why-gpus-matter-for-ai.md`](../20-why-gpus-matter-for-ai.md), Section 12. Attempt every
> question yourself first, with your own worked reasoning, before reading any answer below.

---

## Level 1 — Recognition

**1. Core architectural difference between CPU and GPU?** A CPU has few, powerful, flexible cores
built for general-purpose, sequential/branching work; a GPU has many simpler execution units built
for highly parallel computation (Section 1, Section 4).

**2. What does "sequential work" mean?** Work where each step depends on the result of the
previous step, and therefore cannot be effectively split across multiple execution units (Section
5).

**3. What does "parallel work" mean?** Independent work actually being executed at the same time,
across multiple execution units (Section 5).

**4. What does "data parallelism" mean?** Applying the same (or very similar) operation to many
different pieces of data, independently, at the same time (Section 5).

**5. Difference between system RAM and GPU memory (VRAM)?** System RAM is the CPU's main volatile
working memory; VRAM is memory dedicated to the GPU, physically separate in a discrete-GPU
configuration, built for the GPU's high-bandwidth, highly parallel access needs (Section 8, Table
4).

**6. Training vs. inference, in one sentence each?** Training is repeatedly adjusting a model's
internal numerical values using data; inference is using an already-trained model to produce a
result for new input (Section 6).

**7. What does "throughput" mean?** How much work can be completed overall, per unit of time
(Concept 13, Section 4; Section 6).

**8. What does "latency" mean?** How long a single operation takes to complete (Concept 13, Section
4; Section 6).

**9. What is a matrix, conceptually?** A rectangular arrangement of numbers — a grid or table of
values (Section 5).

**10. What is a tensor, conceptually?** A general term for a collection of numbers arranged in some
number of dimensions (a number, a list, a grid, or higher-dimensional arrangements) (Section 5).

---

## Level 2 — Understanding

**11. Why do GPUs fit AI workloads particularly well?** Because AI computation commonly involves
enormous numbers of similar, largely independent matrix/tensor operations (Section 5, 6) — a
data-parallel shape that matches GPU architecture's design (Concept 13) — a workload/architecture
match (Section 2, Section 6).

**12. Why is "GPU = faster CPU" incorrect?** Because a GPU is architecturally different, not a
sped-up CPU — many simple execution units for parallel work, versus a CPU's few, powerful,
flexible cores; a GPU is faster for suitable workloads specifically, not faster in general (Section
1, 4; Section 10, Misconception 1).

**13. Why is "more GPU cores automatically means faster AI" incorrect?** Because memory bandwidth,
memory capacity, and how well the workload's actual parallelism matches the GPU's design also
matter — raw execution-unit count is only one factor (Concept 13, Section 10; Section 10,
Misconception 3).

**14. Why does GPU suitability depend on the specific workload's characteristics?** Because only
workloads with genuine, substantial data parallelism and enough computation to justify transfer
overhead actually benefit (Section 6's "When GPUs Do Not Automatically Help," Table 7).

**15. Why can data movement between RAM and GPU memory matter for performance?** Because
transferring data into GPU memory and results back takes real, non-zero time (Section 8's data
movement diagram, Table 6) — for workloads with a poor computation-to-transfer ratio, this cost can
outweigh any parallel speedup.

**16. Why can both training and inference benefit from GPU acceleration?** Both involve
matrix/tensor computation with a data-parallel shape (Section 5, 6) — training due to enormous
repeated computation across a dataset, inference due to the same kind of computation per request,
generally in smaller amounts (Section 6, Table 5).

**17. Why is GPU acceleration not automatically beneficial for every workload?** Because small,
sequential, or branching-heavy workloads may have little genuine parallelism to exploit, and
transfer/setup overhead can exceed any benefit (Section 6, "When GPUs Do Not Automatically Help").

**18. Why do CPUs and GPUs need to cooperate, rather than one replacing the other?** Because a real
AI workflow requires orchestration, I/O, data preparation, and control decisions (CPU strengths)
alongside heavy parallel numerical computation (GPU strengths) — neither role substitutes for the
other (Section 6's workflow diagram, Section 7's examples, Section 10, Misconception 5/6).

---

## Level 3 — Application

**19. Same numerical transformation applied to every value in a very large dataset.** GPU —
classic data parallelism (Section 5): the same operation, repeated independently across a large
number of values.

**20. Reading a config file, deciding through several nested conditions which mode to run in.**
CPU — sequential, branching, decision-heavy logic (Section 4, Table 2) with essentially no
parallel numerical work.

**21. Full training loop over a large dataset, repeated for many passes.** CPU + GPU — CPU
orchestrates (loading batches, managing the loop, saving checkpoints); GPU performs the enormous,
repeated matrix/tensor computation (Section 6, 7, Example 2).

**22. Single, latency-sensitive prediction request for a lightweight model.** Likely CPU, or a
CPU-orchestrated fast GPU call, depending on model size — latency, not throughput, dominates
(Section 6's Training vs. Inference; Section 7, Example 4); for a genuinely lightweight model,
CPU-only inference can be entirely appropriate (Section 10, Misconception 12).

**23. Renaming a handful of files based on their contents.** CPU — small, sequential, I/O-bound
task with no meaningful parallel numerical computation (Section 7, Example 3/5).

**24. Large batch of similar matrix computations in a data-processing pipeline.** GPU — large
amount of similar, independent numerical computation, a strong data-parallel match (Section 5, 6).

**25. Coordinating the overall steps of an AI service (input, model call, logging, response).**
CPU — orchestration, I/O, and control flow (Section 6's workflow diagram, Table 3) — the GPU is
invoked *from* this CPU-orchestrated flow for the specific heavy-computation step.

**26. Very large image dataset, same transformation applied to every image.** GPU — large-scale
data parallelism, directly analogous to Concept 13's original graphics/pixel example, extended to
AI-style batch processing (Section 5).

---

## Level 4 — Debugging

**27. "The machine has a GPU, so this program must be using it."** Incorrect — having a GPU
present does not mean a given program routes computation to it; the workload must actually be
designed/configured to use the GPU (Section 11, Scenario 1; Section 10, Misconception 11).

**28. "Sending this small calculation to the GPU made it faster overall," given it did not.**
The error: assuming GPU involvement is automatically beneficial. For small workloads, data-transfer
and setup overhead can exceed any parallel-execution savings (Section 6's "When GPUs Do Not
Automatically Help"; Section 11, Scenario 2/3).

**29. "The GPU replaced the need for a CPU in this system."** Incorrect — every real workflow still
needs the CPU for orchestration, I/O, and control decisions (Section 6, 7, 8; Section 10,
Misconception 5).

**30. "The dataset didn't fit, so I should add more system RAM to fix it," given a GPU-memory
capacity issue.** The error: conflating system RAM with GPU memory/VRAM — they are separate pools
(Section 8, Table 4; Section 10, Misconception 7); the fix must address GPU memory capacity
specifically, not system RAM.

**31. "GPU utilization is low, so the GPU must be broken."** Incorrect — low utilization more
often means the heavy computation isn't actually being routed to the GPU, or the workload lacks
sufficient parallelism, not that the hardware is malfunctioning (Section 11, Scenario 6).

**32. "This workload should run faster on GPU because it's an AI workload."** Incorrect — being
"AI-labeled" does not guarantee sufficient computation or parallelism; GPU benefit depends on the
workload's actual characteristics, not its category (Section 10, Misconception 4/14).

**33. "My single request is slow, so the GPU must be underpowered."** The error: for a single,
low-computation request, the dominant cost may be data-transfer/setup overhead rather than raw GPU
compute power (Section 11, Scenario 7) — the bottleneck may not be the GPU's capability at all.

**34. "This algorithm didn't speed up on GPU, so the GPU driver must be misconfigured."**
Incorrect — a highly sequential or branching-heavy algorithm may simply lack the data-parallel
shape GPUs are built for (Section 5); no amount of correct configuration would make an unsuitable
algorithm benefit (Section 11, Scenario 8).

---

## Level 5 — AI Engineering Integration

**35. Choosing compute for a low-latency, lightweight-model inference service.** Since the model is
lightweight and latency (not throughput) is the strict requirement, CPU-only inference may be
entirely appropriate (Section 10, Misconception 12) — GPU acceleration adds data-transfer overhead
and infrastructure complexity (Section 6's decision framework, question 6 and 7) that may not be
justified for a small amount of per-request computation; the decision should weigh actual
computation volume, latency requirements, and cost/complexity against the modest gains a GPU would
provide here.

**36. Reasoning about a training workload with many repeated passes over a large dataset.** This
is a strong GPU candidate: enormous, repeated matrix/tensor computation (Section 6's decision
framework, questions 1–3), throughput-dominant (Section 6, Table 5), and the computation-to-transfer
ratio is favorable since each batch involves substantial computation relative to its transfer cost
(Section 8, Table 6).

**37. Deciding whether modest GPU gains justify added cost/complexity.** Weigh: how much actual
performance improvement is achieved (Section 6, Table 7), whether the workload's computation volume
genuinely benefits from parallelism, whether the added infrastructure cost and operational
complexity (Section 3, Section 6's decision framework question 7) are proportionate to that gain,
and whether a simpler CPU-only approach would meet requirements adequately — GPU use must be
justified by the workload, not assumed by default (Section 10, Misconception 4/14).

**38. Diagnosing a conceptual CPU/GPU bottleneck in a pipeline slower than expected despite using a
GPU.** First inspect whether the heavy computation is actually reaching the GPU (utilization,
Section 11 Scenario 1/6) and whether data-transfer overhead is disproportionate to the computation
being done (Section 8, Table 6; Section 6's "When GPUs Do Not Automatically Help") — without using
any specific profiling tool, reason through the same decision-framework questions (Section 6) used
to decide GPU suitability in the first place, since a mismatch there is a common root cause.

**39. Designing a high-level AI data/computation flow for a training scenario.** Stored dataset
(Concept 11) → loaded and prepared by the CPU into system RAM (Concept 10, 19; Section 6's
workflow diagram) → relevant batches transferred into GPU memory (Section 8's data-movement
diagram) → GPU performs the repeated matrix/tensor computation for that batch (Section 5, 6) →
results/updated values return to system RAM → CPU manages the next batch/pass and periodically
saves checkpoints to storage (Concept 19's checkpoint example, Section 7 Example 2) — each
storage/RAM/GPU-memory transition named explicitly, matching Section 8's and Section 15's
integration diagrams.

---

_This answer key covers Concept 20 (Why GPUs Matter for AI) only. Concept 20 is the final concept
of Module 0.1 — this answer key does not contain, reference, or anticipate answers for any Module
0.2 material._
