# Concept 9 — Cache — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../09-cache.md`](../09-cache.md), Section 13. Attempt every question yourself first, with your
> own worked reasoning, before reading any answer below.

---

## Level 1 — Recognition

**1. What is CPU cache?** A small, fast hardware memory system built into or close to the CPU,
used to keep frequently or recently needed data and instructions closer to the CPU, reducing the
time the CPU spends waiting for slower memory.

**2. What is a cache hierarchy?** The overall organization of multiple cache levels (commonly
L1, L2, L3) within a CPU, each with different size and speed characteristics, sitting between
registers and RAM.

**3. What is L1 cache?** Generally the smallest and fastest cache level, closest to the CPU's
execution circuitry.

**4. What is L2 cache?** Generally larger and somewhat slower than L1.

**5. What is L3 cache?** Generally larger and slower than L2.

**6. What is a cache hit?** When the requested data or instruction is found at the cache level
being checked.

**7. What is a cache miss?** When the requested data or instruction is not found at the cache
level being checked, requiring the search to proceed to a lower, slower level.

**8. What is temporal locality?** The tendency for the same piece of data to be used again soon
after it was just used.

**9. What is spatial locality?** The tendency for data near a recently-accessed memory location to
be accessed soon as well.

**10. What is latency?** How long a single request for data takes to be fulfilled — a delay
measure, not a capacity measure.

**11. What is capacity?** How much data a given storage location can hold at once.

**12. How is cache different from registers?** Registers are inside the CPU core itself, hold an
extremely small amount of data used immediately by the CPU, and are explicitly referenced by
machine instructions. Cache is larger than registers, still very fast but somewhat farther/slower,
and is managed automatically by hardware rather than being explicitly referenced by ordinary
instructions.

**13. How is cache different from RAM?** Cache is smaller, faster, and closer to the CPU. RAM is
much larger, slower to access than cache, and serves as the computer's main working memory.

**14. How is cache different from storage?** Cache is fast, temporary hardware memory near the
CPU. Storage (a later concept) is persistent, long-term data storage, much larger and much slower
than cache, designed to retain data reliably over time rather than serve as immediate CPU working
memory.

**15. How is CPU hardware cache different from a browser/application cache?** CPU cache is a
physical hardware component managed automatically by the CPU. A browser/application cache is
software-managed storage, explicitly controlled by program code, implemented entirely differently
and for different purposes — they only share the same word.

---

## Level 2 — Understanding

**16. Why does CPU cache exist?**

Because there's a real speed mismatch between how fast the CPU can execute instructions and how
long it takes to access RAM for the data those instructions need. If the CPU had to reach all the
way to RAM for every single value, it would spend a large proportion of its time simply waiting.
Cache exists to reduce that waiting by keeping frequently/recently needed data and instructions
closer to the CPU.

**17. Why is cache smaller than RAM?**

Because of the general capacity/speed/proximity trade-off (Section 5): storage that's kept
extremely close to the CPU and made extremely fast is, as an engineering reality, kept small —
similar to the trade-off Concept 6 established for registers. Making cache as large as RAM while
keeping it as fast and close as cache is not how the trade-off works in practice.

**18. Why do smaller cache levels tend to be faster than larger ones?**

Smaller levels (like L1) are positioned closer to the CPU's execution circuitry and engineered
specifically for minimal latency, at the cost of holding less. Larger levels (L2, L3) trade some
speed for more capacity — this mirrors the same general trade-off pattern established for
registers vs. cache vs. RAM.

**19. What does a cache hit mean, and why is it beneficial?**

A cache hit means the requested data/instruction was found at the cache level checked. It's
beneficial because the CPU can use that data quickly, without the additional time cost of
searching farther, slower levels or reaching all the way to RAM.

**20. What does a cache miss mean, and why is it not a program failure?**

A cache miss means the requested data/instruction was not found at the level checked, so the
search proceeds to a lower level. It is not a failure because it's a normal, routine, expected part
of how the memory hierarchy works — it simply means an additional retrieval step is needed; the
data itself is never lost or damaged.

**21. What does temporal locality mean?**

The same piece of data tends to be reused again soon after it was just accessed — e.g., a variable
being updated repeatedly in a loop.

**22. What does spatial locality mean?**

Data near a just-accessed memory location tends to be accessed soon afterward — e.g., iterating
through consecutive elements of an array.

**23. Why doesn't cache replace RAM?**

Cache's capacity is far too small to hold everything a running program needs (Section 5's
capacity trade-off) — RAM's much larger capacity is still necessary to hold the broader set of
active program data. Cache reduces reliance on RAM; it doesn't eliminate the need for it
(Misconception 12).

**24. Why doesn't cache increase CPU clock frequency?**

Cache and clock frequency (Concept 2) address entirely different things — clock frequency governs
how many execution cycles per second the CPU performs; cache reduces how long the CPU waits for
data between those cycles. They're separate mechanisms affecting performance through different
means (Misconception 9).

**25. Why does cache behavior matter to software performance?**

Because how a program accesses memory (its locality characteristics, Section 8) affects how often
the CPU finds what it needs already in fast cache (a hit) versus how often it must wait for a
slower retrieval (a miss) — and since cache hits/misses affect how much time the CPU spends
waiting versus computing, a program's access pattern can meaningfully affect its real-world
execution speed.

---

## Level 3 — Application

### Exercise A — Hierarchy

**26. Data found in L1.** This is an L1 hit (Section 7, Example A) — the CPU retrieves the data
quickly from the fastest, closest cache level, with minimal delay.

**27. Data missing in L1 but found in L2.** This is an L1 miss followed by an L2 hit (Section 7,
Example B) — the search proceeds from L1 to L2, where the data is found; this takes somewhat
longer than an L1 hit, since L2 is farther/slower, but is still faster than reaching RAM.

**28. Data missing in all cache levels.** This is a miss through L1, L2, and L3, with the request
ultimately reaching RAM (Section 7, Example C) — this takes the longest of the three scenarios,
since the data must be retrieved from the farthest, slowest level in this simplified hierarchy.

### Exercise B — Locality comparison

**29.** `array[0], array[1], array[2], array[3]` demonstrates stronger spatial locality. These
memory locations are consecutive/nearby, exactly matching spatial locality's definition (Section
8) — accessing one location and then soon accessing a nearby one. A pattern that jumps widely and
unpredictably through memory has weak or no meaningful spatial locality, since there's no
consistent "nearness" relationship between successively accessed locations.

### Exercise C — Temporal locality

**30.** `counter += 1` repeated three times demonstrates temporal locality — the *same* variable
(`counter`) is accessed (read and written) repeatedly, in quick succession, matching temporal
locality's definition (Section 8) exactly: data used now being used again soon.

### Exercise D — Hardware observation

**31–33.** Answers will vary based on the learner's own system, but should include: the specific
cache levels reported (e.g., L1d, L1i, L2, L3), their sizes and types (data/instruction/unified),
observed via `lscpu | grep -i cache` and/or the `/sys/devices/system/cpu/cpu0/cache/` interface.
The observation *means* that the system reports these cache characteristics as visible to the
current environment (Section 10) — it does *not* prove anything about live hit/miss behavior,
does not expose tag/associativity/replacement-policy details, and — critically, per Section 10's
WSL2 caveats — does not guarantee this is an exact, unmodified reflection of the physical host's
actual hardware cache configuration, since WSL2 is a virtualized environment.

---

## Level 4 — Debugging

**34. "Cache miss means failure."**

Wrong: a cache miss is a normal, routine event meaning the requested data wasn't found at the
checked level, requiring an additional retrieval step from a lower level. It has no relationship
to program errors or crashes (Section 7, Misconception 3).

**35. "L3 is always faster than L1."**

Wrong, and backwards: L1 is generally the fastest, smallest level; L3 is generally larger and
slower than L1 and L2. Higher numbers indicate levels farther from the CPU, not faster ones
(Misconception 5).

**36. "Programs directly control cache levels."**

Wrong: cache is automatically managed by hardware mechanisms; ordinary program instructions do not
typically specify which cache level to use for a given value (Section 5, Misconception 7).

**37. "Cache is permanent."**

Wrong: cache is temporary, volatile working memory whose contents constantly change — it is not
designed for long-term retention the way persistent storage is (Misconception 2).

**38. "More cache always means more performance."**

Wrong: whether additional cache capacity helps depends on the workload's locality characteristics
— a workload with poor locality, or one that already fits within existing cache capacity, may see
little or no benefit. "Always" overstates a workload-dependent relationship (Misconception 4,
Misconception 11).

---

## Level 5 — Integration

### Scenario A — CPU-bound application: repeatedly accessing the same small amount of data

**39. What type of locality may exist?** Temporal locality — the same small amount of data being
accessed repeatedly is exactly the pattern temporal locality describes (Section 8).

**40. Why might cache help?** Because the repeatedly-used data is small enough to likely fit
within a fast cache level, subsequent accesses after the first have a good chance of being hits
rather than requiring repeated trips to slower memory.

**41. What cannot be concluded without measurement?** The exact hit/miss rate, the exact
performance improvement (if any), and whether this specific program on this specific hardware
actually benefits as expected — locality creates *opportunity* for cache to help, but actual
benefit requires real measurement to confirm, not just a plausible conceptual pattern.

### Scenario B — Large sequential dataset: processing an array sequentially

**42. What type of locality is relevant?** Spatial locality — sequential array access is the
canonical example (Section 8, Section 9 Example 2).

**43. Why might cache matter?** Because sequential access to nearby memory locations is the kind
of pattern cache (and the way it brings in nearby data) is well-suited to help with, potentially
reducing the effective cost of retrieving each subsequent element compared to scattered,
unpredictable access.

### Scenario C — AI preprocessing: repeatedly accessing nearby numerical data

**44. Why might cache behavior matter here?** Because this access pattern (repeated/nearby access
to numerical data) resembles both temporal and spatial locality patterns this lesson described —
patterns cache is generally well-suited to help with, potentially reducing memory-wait time during
preprocessing.

**45. What relationship exists between data access patterns and locality?** The specific way a
program accesses memory (repeated use of the same data, or access to nearby locations) *is* what
locality describes — a program's actual access pattern determines whether it exhibits good or poor
temporal/spatial locality, which in turn determines how much opportunity cache has to help.

**46. Why avoid assuming cache alone explains performance?** Because real performance depends on
many factors together — computation itself, memory access patterns, the specific hardware's
actual cache behavior, and other elements this lesson explicitly did not teach (Section 3's
compute-bound vs. memory-bound distinction) — attributing performance to cache alone, without
measurement, risks an incomplete or incorrect explanation (echoing Section 9's explicit caution
against unverified claims about specific AI framework cache behavior).

### Scenario D — WSL2: different cache topology between WSL2 and host

**47. What might explain this difference?** WSL2 is a virtualized environment; the CPU/cache
topology it presents to the guest (Ubuntu) is not guaranteed to be identical to what the physical
host (Windows) reports directly — this is expected virtualization behavior (Section 10, Section
12 Scenario 5), not a malfunction.

**48. Why avoid treating guest-visible information as a perfect representation of the physical
hardware?** Because a virtualization layer can present a scoped, adjusted, or incomplete view of
the underlying physical hardware to the guest environment — exactly as previously established for
CPU core counts (Concept 3, Concept 6) — so guest-observed values should be understood as "what
this environment reports," not automatically as "the exact, complete physical hardware
specification."

---

_This answer key covers Concept 9 (Cache) only. It does not contain, reference, or anticipate
answers for Concept 10 (RAM) or any later concept._
