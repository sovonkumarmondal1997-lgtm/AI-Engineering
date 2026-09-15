# Concept 11 — Storage — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../11-storage.md`](../11-storage.md), Section 13. Attempt every question yourself first, with
> your own worked reasoning, before reading any answer below.

---

## Level 1 — Recognition

**1. What is storage?** Non-volatile technology used to retain data and programs persistently,
including when the computer is powered off.

**2. What is persistent storage?** Another name for storage, emphasizing that information survives
beyond the current execution or power cycle.

**3. What does non-volatile mean?** Data is retained without requiring continuous power — the
technical opposite of RAM's volatile property.

**4. What is a storage device?** The actual physical hardware component that provides storage
(e.g., an SSD or HDD).

**5. What is a storage medium?** The actual physical material or technology a storage device uses
to hold data.

**6. What does storage capacity mean?** How much data a storage device can hold at once, commonly
measured in GB or TB.

**7. What is latency, in the context of storage?** How long an individual storage operation takes
to complete/begin producing a result.

**8. What is throughput, in the context of storage?** How much data can be transferred over time —
the storage-specific term for bandwidth.

**9. What does IOPS stand for?** Input/output operations per second — how many individual
read/write operations a storage device can handle per second.

**10. What is a file?** A logical representation of stored data — a document, image, source code
file, etc.

**11. What is a filesystem?** Software that organizes and manages files and storage, providing
structure (like directories/file names) that lets the OS and applications work with stored data in
an organized way — introduced here only conceptually; full treatment belongs to Module 0.2.

**12. How is storage different from RAM?** Storage is persistent/non-volatile and generally
slower/larger-capacity; RAM is volatile, faster, and serves as active working memory (Concept 10).

**13. How is storage different from cache?** Cache is small, extremely fast, hardware memory close
to the CPU, used to reduce wait time for RAM access (Concept 9); storage is much larger, slower,
and persistent — serving an entirely different role.

**14. How is storage different from registers?** Registers are tiny, extremely fast storage inside
the CPU core, holding immediate operands/state (Concept 6); storage is vastly larger, much slower,
and persistent — the opposite end of the memory/storage hierarchy.

**15. Why does storage matter to an Applied AI Engineer?** Because source code, datasets, model
files, checkpoints, logs, configuration, and other AI-project artifacts all require persistent
storage to exist reliably between sessions (Section 3).

---

## Level 2 — Understanding

**16. Why does storage exist?** Because RAM is volatile — without a separate, persistent mechanism,
all data and programs would be lost every time the computer loses power. Storage exists
specifically to retain data and programs across power cycles (Section 2).

**17. Why can't RAM replace persistent storage?** Because RAM loses its contents when power is
removed (Concept 10) — a computer relying only on RAM would lose everything every time it powered
off, making it unusable for any lasting purpose.

**18. What does non-volatile mean?** Data is retained without requiring continuous power — the
defining property that makes storage suitable for long-term retention.

**19. What does persistence mean?** Information surviving beyond the current execution or power
cycle.

**20. What does storage capacity mean?** How much data a given storage device can hold at once.

**21. What does latency mean?** How long a single storage operation takes to begin/complete — a
delay measure.

**22. What does throughput mean?** How much data can move to/from storage per unit of time — a
"how much moves" measure, distinct from latency.

**23. What does IOPS mean?** How many individual input/output operations a storage device can
handle per second — particularly relevant for workloads involving many small operations rather
than one large transfer.

**24. Why doesn't more storage automatically improve performance?** Because capacity and
performance (latency, throughput, IOPS) are separate, independently-varying properties (Section
8) — a high-capacity device is not guaranteed to also be fast.

**25. Why are files not the same thing as physical storage devices?** A file is a logical
representation of specific stored data; a storage device is the physical hardware providing the
underlying capacity that can hold enormous numbers of separate files (Section 1, Misconception 5).

**26. Why does storage matter to AI engineering specifically?** Because AI systems commonly
involve large amounts of data and artifacts (datasets, model files, logs) that must be reliably
retained between sessions, and understanding storage as a real, finite resource is foundational to
reasoning about real AI projects (Section 3).

**27. Why do WSL2 storage observations need context?** Because WSL2 is a virtualized environment,
and the storage information it reports may reflect virtualization-specific configuration rather
than a direct, complete representation of the physical host's actual disk hardware (Section 10).

---

## Level 3 — Application

### Exercise A — Memory hierarchy

**28.**

```text
Registers → immediate CPU operands/state (Concept 6)
Cache     → keeps frequently/recently needed data/instructions close to the CPU (Concept 9)
RAM       → active working memory for a running program (Concept 10)
Storage   → persistent, long-term retention of data and programs (this lesson)
```

### Exercise B — Program lifecycle

**29.** A Python program's source code exists persistently on storage. When the program is run,
the relevant code/data is brought into RAM (active working memory), and the CPU then executes the
resulting instructions, working with data that may pass through cache along the way (Concept 9,
Concept 10). Storage is where the program lives when not running; RAM and the CPU are where it
actually executes.

### Exercise C — Storage capacity: 1 TB

**30. What this tells you:** The maximum total amount of persistent data this storage can hold at
once.

**31. What this does NOT tell you:** How fast that storage is (latency, throughput, IOPS are
separate properties, Section 8); how much of that 1 TB is already used; or whether this capacity
is "enough" for any particular workload without knowing that workload's actual requirements.

### Exercise D — AI artifacts

**32.** A dataset, model checkpoint, Python source code, logs, and configuration all require
persistent storage because each represents information that must survive beyond the current
program execution or power cycle: the dataset and code need to exist before/after any given run;
the checkpoint preserves training progress for later reuse; logs record what happened for later
review; and configuration must persist between runs to control consistent behavior. None of these
would still exist after a power cycle if they only existed in RAM (Section 2, Section 9's
examples).

### Exercise E — Linux observation

**33–36.** Answers will vary based on the learner's own system, but should include the specific
values observed from `df -h` (filesystem size/used/available), `lsblk` (block-device
names/sizes/mountpoints, if available), and `du -sh .` (current directory's disk usage). Each
command measures something different: `df` measures filesystem-level capacity/usage; `lsblk`
measures block-device-level layout; `du` measures specific files/directories' space consumption.
None of them, individually or together, definitively prove the exact physical hardware
specifications of the host machine — especially inside WSL2, where the virtualization layer may
present a scoped or adjusted view of the underlying physical disk (Section 10's explicit caveats).

---

## Level 4 — Debugging

**37. "Storage is just slower RAM."**

Wrong: this oversimplifies a structural difference. Storage's defining property is non-volatility
(persistence across power cycles) — a property RAM entirely lacks, regardless of storage's speed
relative to RAM. Speed is one difference among several, not the defining one (Misconception 10).

**38. "1 TB storage means the computer is faster than a computer with 512 GB."**

Wrong: capacity and performance are separate properties (Section 8) — a larger-capacity device is
not guaranteed to be faster; performance depends on latency, throughput, and IOPS, which vary
independently of capacity (Misconception 3, Misconception 9).

**39. "df -h tells me the physical SSD model and capacity."**

Wrong: `df` reports filesystem space as currently configured/exposed to the environment — not a
direct specification of the physical SSD's model or exact hardware capacity, especially inside a
virtualized environment like WSL2 (Misconception 6).

**40. "du tells me how much physical disk exists."**

Wrong: `du` measures how much space specific files/directories currently occupy — not the total
capacity of the underlying storage device (Misconception 7).

**41. "Programs execute directly from SSD."**

Wrong: relevant program/data must first be loaded into RAM before the CPU can work with it
(Concept 10's foundational point) — and further, source code isn't executed directly at all; it
goes through compilation/interpretation first (Concept 7, Concept 8). Storage is only the starting
point of a longer chain, not where execution directly happens (Section 12, Scenario 5).

---

## Level 5 — Integration

### Scenario A — Python project

**42. Which information requires persistent storage, and why?** Source code, the virtual
environment's installed packages, datasets, and generated artifacts all require persistent
storage — each needs to survive beyond any single execution or power cycle so the project remains
usable across sessions (Section 2, Section 9 examples).

**43. What information may later be loaded into RAM?** The source code (once run), portions of the
datasets actively being processed, and any data structures created during execution — all become
active working data in RAM while the program runs (Section 5's conceptual chain).

**44. Why are storage and RAM both needed here?** Storage provides reliable, persistent retention
between sessions; RAM provides fast, active working memory while the program actually runs — a
project relying on only one of these would either lose everything on power-off (RAM only) or run
far too slowly to be usable (storage only) (Section 2, Concept 10).

### Scenario B — AI dataset

**45. Why does dataset size affect storage requirements?** Because the dataset's actual data
volume, measured in the units from Section 7 (KB/MB/GB/TB), directly determines how much storage
capacity is needed to hold it persistently.

**46. Why does storage capacity not directly determine model performance?** Because storage
capacity and storage/system performance are separate properties (Section 8) — having enough
capacity to store a dataset says nothing about how quickly it can be read, or about the CPU/RAM
resources actually used during model training or inference, which depend on entirely different
factors covered in earlier concept files.

**47. What distinction exists between storing the dataset and processing it?** Storing the dataset
means it persistently resides on a storage device (Section 1, Section 2); processing it requires
loading the relevant portions into RAM (Concept 10) so the CPU (and cache, Concept 9) can actually
work with it — storage and active processing are two distinct stages, not the same activity.

### Scenario C — Model checkpoint

**48. Why does the checkpoint need persistent storage?** So the trained model's progress/state
survives beyond the current program execution or power cycle, allowing it to be reused later
without retraining from scratch (Section 9, Example 5).

**49. Why is it also loaded into working memory when used?** Because the CPU cannot work directly
with data sitting in storage (Section 5, Section 12 Scenario 5) — the checkpoint's relevant data
must first be brought into RAM (active working memory, Concept 10) before it can actually be used
for inference.

**50. Why should storage and RAM not be treated as interchangeable?** Because they serve
structurally different roles: storage provides reliable, persistent retention but is far slower
for active use; RAM provides fast active working memory but loses everything on power-off. The
checkpoint scenario itself demonstrates why both are needed together, not interchangeably (Section
2, Misconception 1).

### Scenario D — WSL2 storage observation

**51. What do these commands reveal?** `df -h` reveals filesystem-level capacity, usage, and mount
points as reported to the WSL2 Linux environment; `lsblk` reveals block-device-level layout as
presented to that same environment.

**52. What can they not prove about the physical host?** They cannot prove the exact physical
disk's model, true total capacity, or precise hardware layout — WSL2 may present virtualized or
scoped storage information rather than a direct, complete mirror of the physical host's actual
hardware (Section 10's explicit caution, echoing the identical caveats from Concept 3, Concept 6,
Concept 9, and Concept 10 for CPU/memory observations).

**53. Why does virtualization matter here?** Because a virtualization layer (WSL2) sits between the
Linux environment and the physical hardware, and can present a configured, adjusted, or partial
view of that hardware to the guest — exactly the same principle already established repeatedly
throughout this module for CPU cores, cache, and RAM observations.

---

_This answer key covers Concept 11 (Storage) only. It does not contain, reference, or anticipate
answers for Concept 12 (HDD vs SSD) or any later concept._
