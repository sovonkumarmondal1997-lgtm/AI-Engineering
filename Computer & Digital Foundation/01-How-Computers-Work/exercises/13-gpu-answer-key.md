# Concept 13 — GPU — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../13-gpu.md`](../13-gpu.md), Section 14. Attempt every question yourself first, with your own
> worked reasoning, before reading any answer below.

---

## Level 1 — Recognition

**1. What does GPU stand for?** Graphics Processing Unit.

**2. What is the difference between a GPU and a graphics card?** A GPU is the processor chip
itself; a graphics card is the complete product containing a GPU chip plus VRAM, cooling, power
delivery, and interfaces.

**3. What is VRAM?** Video RAM — memory dedicated specifically to a GPU, typically on the graphics
card, used to hold data the GPU is actively working with.

**4. What is an integrated GPU?** A GPU built directly into the same chip/package as the CPU,
generally sharing system RAM rather than having its own dedicated VRAM.

**5. What is a discrete GPU?** A GPU that exists as its own separate chip, typically on its own
graphics card, physically distinct from the CPU, commonly with its own dedicated VRAM.

**6. What does "data parallelism" mean?** Applying the same (or very similar) operation to many
different pieces of data, independently, at the same time.

**7. What is the difference between latency and throughput?** Latency is how long a single
operation takes to complete; throughput is how much work can be completed overall, per unit of
time.

**8. What does "compute throughput" mean, in the context of a GPU?** How much computational work
the GPU can complete per unit of time.

**9. What does "memory bandwidth" mean, in the context of a GPU?** How much data can move between
the GPU and its memory (VRAM) per unit of time.

**10. What does GPU utilization mean?** How much of the GPU's available compute capacity is
actually being used by a given workload at a given moment.

**11. What is a GPU compute unit?** A larger organizational grouping within a GPU containing many
lightweight execution units, working together on a portion of the overall workload.

**12. What are "thread," "block," and "grid"?** Conceptually: a thread is the smallest individual
strand of work (e.g., the calculation for one data element); a block is a group of many threads; a
grid is a larger collection of blocks representing the entire workload. These are GPU-programming
terms introduced only conceptually here — actually programming with them is a later topic.

---

## Level 2 — Understanding

**13. Why were GPUs originally built?** To handle the specialized computational work of producing
images on screen — specifically, performing an enormous number of similar calculations (like
determining every pixel's color) very quickly and repeatedly, a shape of work general-purpose CPUs
were not architecturally well-suited to.

**14. Why is a GPU architecturally different from a CPU?** A CPU is built with few, powerful,
flexible cores optimized for varied, sequential, branching work; a GPU is built with many simpler
execution units optimized for large amounts of similar, independent (data-parallel) work — a
different engineering trade-off suited to a different shape of workload.

**15. Why does data parallelism matter for GPU performance?** Because GPUs are architecturally
built around dividing large amounts of similar, independent work across many execution units
simultaneously — a workload without genuine data parallelism cannot take advantage of this
architecture's core strength.

**16. Why doesn't a GPU replace the CPU?** Because a real system still needs orchestration, control
logic, and general-purpose sequential/branching work — exactly what a CPU is built for — while the
GPU handles the highly parallel computational portions; they serve complementary, not competing,
roles.

**17. Why is VRAM different from system RAM?** Both are volatile working memory, but VRAM is
specifically built and positioned for the GPU's very high-bandwidth, highly parallel access needs,
and is physically separate from system RAM in a discrete-GPU configuration.

**18. Why does data sometimes need to move between system RAM and VRAM?** Because data a GPU needs
to compute with commonly starts out in system RAM (having been loaded from storage) — before the
GPU can actually use it, it generally must be transferred into VRAM, a real data-movement step
taking real time.

**19. Why doesn't more VRAM automatically mean a faster GPU?** Because VRAM capacity (how much data
can be held) and GPU performance (compute throughput, memory bandwidth) are separate,
independently-varying dimensions — more VRAM allows larger workloads to fit, but does not itself
make computation faster.

**20. Why doesn't 100% GPU utilization automatically mean a workload is optimal?** Because
utilization measures how busy the execution units are, not whether the underlying work is being
done efficiently or whether the workload was well-matched to the GPU's strengths in the first
place.

**21. Why are some workloads poorly suited to GPU execution?** Because they lack genuine data
parallelism — sequential, heavily branching, or very small workloads don't have enough independent,
similar work to divide across many execution units, and may not justify the overhead of moving
data to VRAM and organizing parallel execution.

**22. Why do AI workloads commonly benefit from GPU execution?** Because AI computation
(matrix/tensor operations) commonly involves an enormous number of similar, largely independent
individual calculations — exactly the data-parallel shape GPU architecture is built to handle
efficiently.

---

## Level 3 — Application

### Exercise A — CPU vs. GPU responsibilities

**23.** Reading the dataset from storage and preparing/organizing it are more naturally CPU
responsibilities — this involves orchestration, I/O coordination, and general-purpose logic
(Section 12's CPU role). The large amount of matrix computation is more naturally a GPU
responsibility — it's exactly the data-parallel, large-scale numerical work GPU architecture is
built for (Section 5, Section 12's GPU role). This division matches Section 12's "CPU +GPU
cooperation" diagram directly.

### Exercise B — GPU-friendly or not?

**24. Applying the same transformation to every element of a very large array.** GPU-friendly:
this is a textbook example of data parallelism (Section 5) — the same operation, applied
independently across many data elements.

**25. Making a single, complex, branching decision based on several unrelated conditions.** Not
GPU-friendly: this is exactly the kind of complex, branching, low-parallelism logic a CPU handles
more efficiently (Section 4, Section 12).

**26. Rendering a complex 3D scene with millions of similarly-processed pixels.** GPU-friendly:
this is the GPU's original, motivating use case (Section 1, Section 2) — large numbers of similar,
independent per-pixel calculations.

**27. Running a small script that reads one configuration file and prints a message.** Not
GPU-friendly: this is a small, sequential, low-parallelism task where GPU setup/data-transfer
overhead would likely outweigh any benefit (Section 12's "workloads too small to justify GPU
overhead" point).

### Exercise C — VRAM capacity reasoning

**28.** When a workload's data exceeds available VRAM capacity, it cannot simply proceed as if
VRAM were unlimited — this is a genuine, practical constraint (Section 8, Section 10's
"more of a resource ≠ automatically faster/better" caution applied to capacity specifically). This
lesson does not teach the exact technical mechanisms systems use to handle this situation (that's
later, more advanced material) — the key conceptual point is that VRAM capacity is finite and real,
directly analogous to Concept 9's cache capacity limit and Concept 10's RAM capacity limit.

### Exercise D — Throughput vs. latency

**29.** For a workload processing a very large batch of similar, independent items, the overall
time to complete the *entire batch* (throughput) matters far more than how quickly any single item
in isolation is processed (latency) — because the workload's value comes from completing the whole
batch, and a GPU's architecture (Section 4, Section 5) is specifically optimized to maximize
overall throughput across many similar operations, even if it wouldn't necessarily minimize the
latency of any one operation viewed alone.

---

## Level 4 — Debugging

**30. "A GPU is just a graphics card."** Wrong: a GPU is the processor chip; a graphics card is the
complete product (GPU chip + VRAM + cooling + power delivery + interfaces) — related but not
identical (Misconception 1).

**31. "GPUs are only useful for rendering graphics."** Wrong: GPU architecture is broadly useful
for any data-parallel workload, including AI computation, not only graphics (Misconception 2).

**32. "A GPU is always faster than a CPU, for any task."** Wrong: a GPU is generally faster for
suitable, highly parallel workloads, but a CPU is often faster/more appropriate for sequential,
branching, or low-latency work (Misconception 3).

**33. "A GPU with more cores than another GPU is always faster."** Wrong: core count is only one
factor; memory bandwidth, VRAM capacity, and workload suitability also matter (Misconception 4).

**34. "Since I have a powerful GPU, I don't need a CPU."** Wrong: the CPU handles orchestration,
control logic, and general-purpose work that the GPU does not replace (Misconception 5).

**35. "VRAM and system RAM are interchangeable."** Wrong: both are volatile working memory, but
VRAM is specifically built for the GPU's high-bandwidth needs and is physically separate in a
discrete-GPU configuration (Misconception 6).

**36. "A GPU can make any program run faster."** Wrong: only workloads with genuine data
parallelism benefit substantially — sequential or small-scale workloads may see no benefit, or even
run slower due to overhead (Misconception 7).

**37. "More VRAM always means better GPU performance."** Wrong: VRAM capacity and GPU performance
(compute throughput, memory bandwidth) are separate, independently-varying dimensions
(Misconception 8).

**38. "100% GPU utilization means my program is running as efficiently as possible."** Wrong:
utilization measures busy-ness, not whether the work being done is actually efficient or
well-matched to the GPU's strengths (Misconception 9).

**39. "My WSL2 GPU observation proves exactly what physical GPU is installed on my Windows host."**
Wrong: as this lesson's own captured example showed (a "Basic Render Driver" from "Microsoft
Corporation" via `dxgkrnl`), WSL2 can expose a virtualized rendering interface rather than a
complete, accurate picture of the physical GPU (Misconception 12).

---

## Level 5 — Integration / AI Engineering Reasoning

### Scenario A — Choosing CPU or GPU

**40. A small script that renames a handful of files based on their content.** CPU: this is a
small, sequential, I/O-oriented task with little to no data parallelism — GPU overhead would not
be justified (Section 12's overhead factor).

**41. A large-scale numerical computation applied identically across millions of data points.**
GPU: this is a textbook data-parallel workload (Section 5) — large amounts of similar, independent
computation, exactly matching GPU architecture's strengths, assuming the data fits in available
VRAM (memory requirements factor) and a suitable GPU is available (availability factor).

**42. An interactive application that must respond to a single user action as quickly as
possible.** CPU: this is a latency-sensitive task (Section 4) — minimizing the time for one
specific response matters more than throughput across many similar operations, which is a CPU's
strength.

**43. An AI workload that loads a large dataset, prepares it, and then performs extensive matrix
computation on it.** A combination of both: the CPU handles loading/preparation (orchestration,
Section 12), and the GPU handles the extensive matrix computation (data-parallel numerical work,
Section 5, Section 12) — reasoning through all seven decision-making factors (workload
characteristics, parallelism, data movement, memory requirements, latency requirements, GPU
availability, overhead) supports this split rather than a single-technology answer.

### Scenario B — Interpreting a GPU observation

**44.** This output tells the learner that WSL2's virtualization layer is exposing a
virtualized/basic rendering interface (via the `dxgkrnl` driver) to the Linux environment — it does
**not** tell the learner what actual physical GPU (make, model, manufacturer) is installed in their
Windows host machine. The "Microsoft Corporation" vendor and "Basic Render Driver" product name are
both artifacts of the virtualization layer itself, not a description of real GPU hardware
(Section 11, Misconception 12).

### Scenario C — Why AI benefits from GPU parallelism

**45.** AI computation involving large amounts of matrix/tensor operations consists of an enormous
number of similar, largely independent individual calculations (e.g., many multiplication-and-
addition steps applied across large collections of numbers) — exactly the data-parallel shape
(Section 5) that GPU architecture is built around: many simpler execution units working through
similar operations across many data elements simultaneously, rather than a CPU's smaller number of
powerful cores working through a more varied, sequential mix of tasks. Because this matches GPU
architecture's core strength so directly, GPUs can process this kind of computation with much
higher throughput than a CPU would for the same volume of similar work — without requiring any
specific neural-network mathematics to understand *why* the underlying computational shape favors
GPU execution.

---

_This answer key covers Concept 13 (GPU) only. It does not contain, reference, or anticipate
answers for Concept 14 (Files) or any later concept, and it does not anticipate Concept 20's
("Why GPUs Matter for AI") deeper AI-GPU material._
