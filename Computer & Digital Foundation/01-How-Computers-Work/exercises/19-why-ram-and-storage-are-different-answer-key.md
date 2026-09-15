# Concept 19 — Why RAM and Storage Are Different — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../19-why-ram-and-storage-are-different.md`](../19-why-ram-and-storage-are-different.md),
> Section 14. Attempt every question yourself first, with your own worked reasoning, before
> reading any answer below.

---

## Level 1 — Recognition

**1. What does RAM stand for, and what is its defining property?** Random Access Memory — its
defining property is that it is volatile, active working memory used by running programs
(Section 1).

**2. What is the defining property of persistent storage?** It is non-volatile — it retains data
even when power is removed, and holds data whether or not it is currently being used (Section 1).

**3. What does "volatile" mean?** Contents are lost when power is removed (Section 1).

**4. What does "non-volatile" (or "persistent") mean?** Contents survive without continuous power
(Section 1).

**5. What is a process, in one sentence?** A running instance of a program, with its own memory
and execution state, managed by the operating system (Section 7, recalling Concept 16).

**6. What is a program file, in one sentence?** Persistent, inert data on storage that defines
what a program does, but which is not itself currently executing (Section 7).

**7. Name the four layers in this lesson's storage-to-CPU hierarchy, in order from farthest to
closest to the CPU.** Storage → RAM → Cache → Registers (Section 5, Section 9).

**8. What does `VmRSS` report about a process?** How much RAM (resident memory) that specific
running process is actually using right now (Section 11).

---

## Level 2 — Understanding

**9. Why does a computer need both RAM and storage, rather than just one?** Because no single
technology is simultaneously extremely fast to access and reliably persistent without power at
reasonable cost — RAM provides speed for active work, storage provides persistence, and neither
substitutes for the other (Section 2, Misconception 12/13).

**10. Why can't a single technology optimize for both extreme speed and reliable long-term
persistence at once?** Because the physical mechanisms that achieve extreme speed generally do not
reliably retain state without continuous power, and vice versa — this is a genuine engineering
trade-off, not an arbitrary design choice (Section 2).

**11. Why is "RAM is faster than storage" an incomplete statement?** Because "faster" could mean
lower latency, higher bandwidth, or both, and these are separate, independently-varying properties
— a full comparison must specify which one is meant (Section 8, Misconception 11).

**12. Why is a program file not the same thing as a process?** A program file is persistent, inert
data on storage; a process is a running instance with its own memory in RAM, its own PID, and its
own execution state (Section 7, Misconception 7).

**13. Why does storage capacity not equal RAM capacity?** They are independent hardware
specifications, sized and purchased separately, with no fixed mathematical relationship (Section 1,
Misconception 4/10).

**14. Why does RAM capacity not equal storage capacity?** Same reasoning in reverse — adding RAM
does not change storage capacity, and vice versa (Misconception 5).

**15. Why can the same executable file produce multiple, independent processes?** Because each
launch creates a separate process with its own separate RAM-resident memory and PID — the file on
storage stays the same, unaffected, across any number of launches (Section 7, diagram).

**16. Why is cache positioned between RAM and registers in the hierarchy, rather than replacing
either one?** Because it trades off capacity for speed at a middle point — smaller and faster than
RAM, larger and slower than registers — reducing how often the CPU must wait on RAM, without
replacing RAM's larger capacity or registers' immediate CPU-level access (Section 9).

---

## Level 3 — Application

**17. Trace double-clicking a document icon to seeing its contents on screen.** File exists on
storage → launch/open request → OS creates a process → the relevant file data is loaded into that
process's RAM → the CPU executes instructions (using RAM, cache, registers) to render the content
→ the result is displayed (Section 6's six-step scenario).

**18. Loading a dataset — storage's role, RAM's role, CPU's role.** Storage: the dataset
persistently resides there as one or more files. RAM: loading brings the relevant bytes into the
process's active working memory. CPU: executes the instructions that perform the read and any
initial processing (Section 10, Example 3).

**19. Saving a checkpoint — storage's role, RAM's role.** RAM holds the current model state
(active working memory) immediately before the write; storage is the destination, where the
checkpoint file will persistently exist once the write completes (Section 10, Example 6).

**20. A system reports 64 GB storage and 4 GB RAM — what does this tell you and not tell you?**
It tells you the system can persistently retain up to 64 GB of data, and can actively work with up
to roughly 4 GB at once. It does not tell you anything about how fast either resource is (Section
8), nor does either number constrain the other (Misconception 4/5/10).

**21. Why could a storage device have high bandwidth but still feel slow for a specific
workload?** Because bandwidth (data per unit time) and latency (delay per access) are separate
measurements (Table 3) — a device might transfer a single large sequential file quickly (high
bandwidth) while still taking a relatively long time to begin many small, scattered accesses (high
latency), which is what many real workloads actually stress (Section 8).

**22. Why doesn't a text file's existence on storage mean it is "loaded" anywhere?** Because
storage holds data whether or not anything is currently using it (Section 1, Misconception 9) —
being loaded specifically means its bytes have been brought into a process's RAM, which is a
separate event from merely existing on storage.

**23. What does the difference between `df -h`'s output and `free -h`'s output represent?** `df -h`
reports storage capacity/usage (persistent); `free -h` reports RAM capacity/usage (active,
volatile) — two entirely different resources, reported by two entirely different commands (Section
11).

**24. Why can a process's `VmRSS` change over time even though its executable file's size on
storage doesn't change?** Because `VmRSS` reflects the process's current active RAM usage, which
varies as the process allocates and releases working memory during execution — this is entirely
separate from the fixed, unchanging size of the executable file sitting on storage (Section 7,
Section 11).

---

## Level 4 — Debugging

**25. "My program can't be out of memory — I have 500 GB of free disk space."** This conflates
storage capacity with RAM capacity (Misconception 4/10) — running out of memory is a RAM-capacity
problem; free disk space does not provide additional RAM (Section 13, Scenario 5).

**26. Assuming a 2 GB dataset file will use exactly 2 GB of RAM when loaded.** This assumption may
not hold because loading, parsing, or representing data in memory can use more (or sometimes less)
RAM than the file's on-disk size, depending on how the data is structured once loaded — the file's
storage size and its in-memory footprint are related but not guaranteed to be identical (Section
13, Scenario 2).

**27. Deleting a large file to "free up RAM."** This action frees storage capacity, not RAM
(Misconception 4/5) — unless that file happened to also be actively loaded into some process's
memory, deleting it has no effect on RAM availability (Section 13, Scenario 7).

**28. Assuming changing `VmRSS` means the executable file on storage is being modified.** This is
incorrect because `VmRSS` reflects the running process's active RAM usage, entirely separate from
the unchanging executable file on storage (Section 7's core distinction, Section 11).

**29. Assuming a closed program's saved data is "gone forever."** This conflates a process ending
(which frees its RAM, Concept 16's "Terminated" state) with a file's persistence on storage
(Section 7) — anything the program actually saved to storage before closing remains there,
unaffected by the process ending.

**30. Assuming RAM and swap are the same thing.** This is incorrect — swap is storage being used as
a fallback for RAM under memory pressure (Section 11's observed `[SWAP]` device, Section 13,
Scenario 6); it is much slower than RAM and is a distinct resource, not RAM itself.

**31. Assuming two processes with the same program name share the same RAM.** This is incorrect
per Section 7 — each independently-launched process has its own separate memory in RAM, its own
PID, and its own execution state, even when running from the identical executable file.

**32. Assuming storage being "big enough" means a program can process an arbitrarily large file
without RAM concerns.** The flaw is that processing generally requires relevant data to be active
in RAM (Section 6), which has its own, typically much smaller, capacity (Section 1) — storage
capacity does not guarantee sufficient RAM is available to actively work with that much data at
once (Section 13, Scenario 1/2).

---

## Level 5 — Integration / AI-Engineering Reasoning

**33. 50 GB dataset on disk, 16 GB RAM available.** The practical implication is that the entire
dataset cannot be brought into RAM as active working memory all at once (Section 1's capacity
comparison, Section 13 Scenario 1/2) — the storage-persisted size (50 GB) and the RAM-active
capacity (16 GB) are separate numbers, and the mismatch between them is the exact tension Section 3
and Section 8 describe. (This lesson does not propose a specific technical solution — that is later
material.)

**34. Trace a model checkpoint file on storage to an actively producing inference result.**
Checkpoint file persistently exists on storage (Concept 11, 12) → the serving application is
launched (Concept 17) and creates a process (Concept 16) → the checkpoint's data is read from
storage and loaded into that process's RAM (Section 6, Section 10 Example 4) → during inference,
the model's parameters and input data are held in RAM (and cache/registers as the CPU/GPU computes,
Section 5) → the CPU (or GPU, Concept 13) performs the computation using that RAM-resident data
(Section 10, Example 5) → a result is produced, entirely from data that was, at that moment, active
in memory, not being re-read from storage for every step.

**35. Why is saving training progress to storage (rather than relying only on RAM) essential for
an interruptible/resumable training run?** Because RAM is volatile (Section 1, Misconception 8) —
if a training run is interrupted (power loss, crash, restart) before saving, everything held only
in RAM is lost; writing a checkpoint to storage (Section 6, Section 10 Example 6) preserves
progress so it can be read back into RAM later to resume, exactly as this lesson's overall
RAM/storage cooperation model requires.

**36. RAM-to-storage relationship for continuously produced logs; why would logs be lost if never
written to storage?** Log entries are generated as active data in the running process's RAM
(Section 6); if that data is never written out to storage (Concept 14's "write" operation, Concept
15's "output" vocabulary), it exists only as long as the process (and its RAM) does — since RAM is
volatile (Section 1), any log data never persisted to storage is lost the moment the process ends
or power is removed (Misconception 8, Section 10 example of logs).

**37. Multiple worker processes running the same AI application executable — why does each have
independent RAM usage?** Per Section 7's core distinction: the executable file on storage is one
persistent, unchanged piece of data, but each worker's *launch* creates its own separate process,
with its own separate RAM-resident execution state and its own PID (Section 7 diagram) — sharing
the same originating file on storage does not mean sharing RAM; each process's memory usage is
independent, exactly as this lesson's Section 11 `VmRSS` observation demonstrated for one specific
process.

---

_This answer key covers Concept 19 (Why RAM and Storage Are Different) only. It does not contain,
reference, or anticipate answers for Concept 20 (Why GPUs Matter for AI) or any later concept._
