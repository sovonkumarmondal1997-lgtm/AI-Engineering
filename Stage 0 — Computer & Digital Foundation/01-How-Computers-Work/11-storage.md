# Storage

**Module:** How Computers Work
**Roadmap reference:** Stage 0 — Module 0.1 — How Computers Work
**Concept(s) covered:** storage
**Status:** Not Started

---

## 1. What is it?

**Starting from what you already know.** Concept 10 established RAM as the computer's main
*working* memory — active, fast, but volatile (its contents disappear when power is removed).
That lesson repeatedly referenced "storage" as the other half of a necessary pair, without teaching
it. This lesson finally introduces it properly.

**Storage — simple meaning:** Storage is the part of a computer that holds data and programs
long-term — designed to retain them even when the computer is turned off.

**Storage — technical meaning:** Computer storage is non-volatile technology used to retain data
and programs persistently, including when the computer is powered off.

**Persistent storage:** "Persistent" describes exactly this quality — information that survives
beyond the current moment, the current program's execution, or even a full power cycle. "Persistent
storage" and "storage" (as this lesson uses the term) mean the same thing; the word "persistent" is
often added explicitly to emphasize the contrast with RAM's temporary nature. Persistence should
not be presented as an absolute guarantee that every individual write is immediately durable on
the physical medium: actual durability depends on the operating system, filesystem, caching, the
storage device, and synchronization/flush behavior.

**Non-volatile storage:** "Non-volatile" is the precise technical opposite of RAM's "volatile"
property (Concept 10, Section 4). Non-volatile means data is retained without requiring continuous
power — exactly the defining characteristic that makes storage suitable for long-term retention in
a way RAM fundamentally is not.

**Storage device:** A storage device or storage resource is hardware or a virtualized storage
resource that provides persistent storage capacity — for example, an SSD, an HDD, or a virtual
disk (named here only as examples; Concept 12, the next lesson,
is specifically dedicated to comparing them — not taught here).

**Storage medium:** "Medium" refers to the actual physical material or technology a storage device
uses to hold data. This lesson does not teach what any specific storage medium is made of or how it
physically works (that's explicitly Concept 12's territory) — the term is introduced here only so
you recognize it.

**Capacity — simple meaning (recalled from Concept 9 and Concept 10):** How much data a storage
device can hold at once — commonly measured in gigabytes (GB) or terabytes (TB) today.

**File — simple meaning:** A file is a logical way of representing a specific piece of stored
data — a document, an image, a program's source code, and so on. Section 4 of this lesson's
required core concepts develops this properly.

**Filesystem — conceptual preview only:** A filesystem is software that organizes and manages
files and storage, providing the structure (like folders/directories, file names, and so on) that
lets an operating system and applications work with stored data in an organized way.

**A required, explicit scope boundary for "filesystem," stated immediately:** This lesson
introduces "filesystem" only as a conceptual preview — enough to understand *that* something
organizes files on top of raw storage. **Detailed filesystem behavior belongs to Stage 0 — Module
0.2 — Operating System Fundamentals**, not to this lesson. This is not this lesson choosing to
simplify arbitrarily — the roadmap itself explicitly places filesystems in Module 0.2, so teaching
filesystem internals here would step outside this concept's designated scope.

**A required terminology map, before going further — do not let these blur together (echoing
Concept 10, Section 1's identical approach):**

```text
Storage            → persistent, non-volatile data retention (this lesson)
RAM                 → active, volatile working memory (Concept 10)
CPU cache            → small, fast memory close to the CPU (Concept 9)
Registers             → tiny, extremely fast storage inside the CPU core (Concept 6)
File                   → a logical representation of stored data (this lesson, Section 4)
Filesystem              → software that organizes files/storage (conceptual preview only —
                           full treatment is Module 0.2)
Virtual memory            → an OS technique, not physical RAM or storage itself (mentioned
                            only briefly, as in Concept 10, not taught in depth)
Swap                        → related to virtual memory, using storage as a RAM extension
                             (mentioned only briefly, as in Concept 10, not taught in depth)
Application/software cache    → software-managed caching implemented by a program (Concept 9
                                already distinguished this from CPU hardware cache; storage is
                                not this either)
```

This lesson is specifically about **persistent, physical computer storage** — the "storage" box in
Concept 10's original conceptual hierarchy diagram, now properly explained on its own terms.

---

## 2. Why does it exist?

**Building directly from Concept 10.** RAM is active working memory — fast, but volatile:

```text
RAM
=
active working memory
```

```text
Storage
=
persistent long-term data
```

Concept 10 established that RAM's contents disappear the instant power is removed. **This creates
an obvious, serious problem: without some other mechanism, everything a computer does would be
permanently lost every single time it's turned off.** No saved documents, no installed programs,
no operating system to even start up again next time. A computer that only had RAM would be
completely unusable in any lasting sense.

**Storage solves this problem directly, by existing specifically to survive what RAM cannot:**

```text
Power ON
→ RAM contains active working state

Power OFF
→ RAM contents are lost

Storage
→ retains persistent data
```

Data and programs held in storage are designed to be retained whether or not the computer is
currently powered on — this is precisely storage's defining purpose and the reason it exists at all.

**Why a computer cannot rely only on RAM:** Beyond the obvious data-loss problem above, there's
also a practical continuity problem: **when the computer starts again, it needs somewhere to load
software and data *from*.** Storage is exactly that source:

```text
Computer restarts
        ↓
software/data is loaded from storage
        ↓
back into RAM (active working memory)
```

This lesson does **not** teach the complete boot process (how a computer actually starts up from
nothing to a running operating system) — that is a substantially more advanced, later topic. The
only point established here is the basic, foundational logic: **storage is what makes a computer
useful across power cycles, and RAM is what makes it fast while actually running** — each solving
a problem the other cannot solve alone, which is exactly why computers need both.

---

## 3. Why does an Applied AI Engineer need to understand it?

Nearly everything you'll produce as an Applied AI Engineer exists, at some point, as something
that must be reliably stored.

**Concrete connections, kept conceptual here:**

- **Source code** — the Python files you write need to persist between sessions; without storage,
  every line of code you write would vanish the moment you closed your terminal or lost power.
- **Python environments** — the tools, libraries, and specific Python installation your projects
  depend on are themselves substantial collections of files, occupying real storage space.
- **Datasets** — data used for training or evaluating AI systems is typically far too large to
  keep only in RAM at all times; it needs to live in storage and be made available to the running system through the memory
  system (often by being loaded or mapped into memory as needed) only when actively being
  processed (Section 5's conceptual flow).
- **Model files** — a trained AI model's learned parameters need to be saved somewhere persistent
  so the model can be reused later without retraining from scratch.
- **Checkpoints** — intermediate saves of a model's progress (mentioned here only by name — not
  taught in depth) are themselves files that must be stored persistently.
- **Logs** — records of what a program or system did over time (Example 6 in Section 9 develops
  this) are written to storage so they can be reviewed later.
- **Configuration** — settings files that control how an application behaves need to persist
  between runs.
- **Artifacts** — a general term for any output a development or AI process produces and needs to
  keep (a trained model, a processed dataset, a report) — all requiring storage.
- **Local development** — your entire day-to-day work as a developer, including everything in this
  very repository you're learning from, depends on storage to exist reliably between sessions.
- **AI pipelines** — a sequence of steps that process data end-to-end typically reads from and
  writes to storage at multiple points along the way.

**Why this matters conceptually, stated plainly:** AI systems, more than many other kinds of
software, commonly involve **large amounts of data and artifacts** — sizable datasets, large model
files, accumulated logs across many runs. Understanding storage as the persistent foundation
underneath all of this — separate from, but working alongside, RAM (Concept 10) — is a
foundational habit for reasoning about real AI projects, well before you reach the more advanced
stages of the roadmap where storage and data engineering become explicit, practical skills.
**This lesson does not teach distributed storage** — systems that store data across many separate
machines — that is a substantially later, more advanced topic, named here only to show where this
foundation eventually connects.

---

## 4. Beginner Explanation

**A five-part analogy, extending Concept 10's warehouse/table/tray/hands analogy with storage now
properly in its rightful place:**

```text
Storage = filing cabinet
RAM = work desk
Cache = small tray
Registers = things currently in your hands
CPU = worker
```

The **filing cabinet** holds documents reliably, indefinitely — you can close the office, turn off
the lights, come back weeks later, and everything is still exactly where you left it (matching
storage's persistence). The **work desk** holds what you're actively working on right now — much
less than the filing cabinet holds overall, but far more convenient to use while working (matching
RAM). The **small tray** and your **hands** repeat Concept 10's exact cache and register mapping,
unchanged.

**The key relationship this analogy is meant to convey:** the filing cabinet (storage) is where
things *live* long-term; the desk (RAM) is where things go *while you're actively using them*. You
generally wouldn't try to do active, ongoing work directly inside a closed filing cabinet drawer —
and you also wouldn't expect papers scattered across your desk to still be neatly organized and
accessible after the office has been closed and reopened many times without ever filing anything
away.

**Where this analogy is useful:** it reinforces, one more time, the same capacity/speed/proximity
trade-off pattern established across registers, cache, RAM, and now storage — and it adds a new,
essential dimension this lesson specifically introduces: **persistence**. The filing cabinet isn't
just "farther away and holds more" — critically, unlike the desk, tray, or your hands, its contents
remain intact even when nobody is in the office at all.

**Where this analogy must break down, explicitly and immediately:** a filing cabinet is a passive
container a human actively opens, searches through, and files things into by hand. **Storage does
not physically behave like a filing cabinet** — it does not involve literal drawers, folders, or
physical browsing. Section 5 (Technical Explanation) explains what actually happens instead: an
operating system and files/directories organize stored data in an entirely different, digital way,
which this lesson only introduces conceptually (full filesystem detail is Module 0.2's territory,
as stated in Section 1). Do not carry the analogy's literal physical mechanics — cabinet doors,
paper folders, manual searching — into your understanding of how real storage actually organizes
and retrieves data.

---

## 5. Technical Explanation

**The general conceptual chain, connecting storage to an actual running application:**

```text
Application
      ↓
Operating-system / filesystem interfaces
      ↓
Storage system
      ↓
Storage device
      ↓
Persistent media
```

Data physically resides on a storage device (Section 1). The operating system (a term you'll study
properly in Module 0.2 — not taught here) manages that storage and presents it to the rest of the
system in an organized way — specifically, through **files and directories** (the conceptual
preview from Section 1). An application (like a Python program) then works with that stored data
by interacting with files, rather than directly manipulating the physical storage hardware itself.

**A required, explicit statement of this lesson's exact boundary here:**

> Applications generally interact with files through operating-system interfaces rather than
> directly controlling the physical storage hardware.

This is an important foundational fact: when your Python code opens a file, it isn't reaching down
and directly manipulating a physical disk — it's making a request that the operating system
handles on its behalf. **This lesson does not teach system calls or file descriptors** — the
specific mechanisms an operating system uses to handle these requests — those are genuine,
important topics belonging to later material (Module 0.2, and Concept 15 — Input/Output, later in
this very module), explicitly out of scope here.

**A brief, conceptual note on memory addresses, connecting back to Concept 10:** just as RAM
locations are identified by memory addresses (Concept 10, Section 5), storage locations are
organized and identified through the filesystem's own structures — but this lesson does not teach
exactly how that identification works internally, consistent with filesystem internals being
explicitly deferred to Module 0.2.

---

## 6. How It Works Internally

A high-level conceptual walkthrough — directly extending the pattern established in Concept 9 and
Concept 10's own "How It Works Internally" sections:

```text
Application requests data
        ↓
Operating system handles the request
        ↓
Storage system/device participates
        ↓
Data is read or written
        ↓
Application receives/updates data
```

Walking through this: when an application needs to read or write persistent data (for example,
opening a file), it doesn't interact with the storage hardware directly — it makes a request that
the operating system handles. The operating system, in turn, works with the actual storage
device to carry out that request — either reading existing data from storage, or writing new/
updated data to it. Once that read or write completes, the application receives the data it asked
for (in the case of a read) or can proceed knowing its data has been written (in the case of a
write).

**An explicit, required caution, matching the pattern established by every prior concept file's
own internal-mechanism section:**

> This is a simplified model. Real systems involve substantially more detail.

For example, real systems may use operating-system, filesystem, and device caches or buffers
between the application and persistent storage.

This lesson does **not** teach: filesystem internals, kernel I/O internals, block devices, device
drivers, DMA (Direct Memory Access), page cache internals, or storage-controller internals. Each of
these is a genuine, real aspect of how storage access actually works — all explicitly out of scope
for this foundational lesson (see the Critical Scope Boundary at the top of this file), belonging
instead to Module 0.2 (Operating System Fundamentals) and other, later, more advanced material.
This lesson's five-step model remains the correct conceptual foundation those later topics
eventually build on.

---

## 7. Storage Capacity and Units

**Building directly on Concept 4.** Storage capacity uses the exact same unit system Concept 4
introduced for describing digital information size:

```text
bit
byte
KB
MB
GB
TB
```

Recall from Concept 4: a bit is the smallest unit of digital information; a byte is 8 bits; and
KB, MB, GB, and TB are progressively larger practical units built from bytes, used constantly to
describe real-world data sizes — including, specifically, storage device capacities.

**Example capacity figures, purely as illustrations of scale — not universal or prescriptive
values:**

```text
1 KB   — roughly enough for a short paragraph of plain text
1 MB   — roughly enough for a small number of photos or documents
1 GB   — roughly enough for a modest collection of documents, or a short video
1 TB   — roughly enough for a very large personal media/document collection
```

**Decimal vs. binary unit conventions, at a beginner-friendly level — the exact same distinction
Concept 4 flagged briefly and Concept 10 revisited for RAM, now specifically relevant to storage
as well:**

```text
KB vs KiB
MB vs MiB
GB vs GiB
TB vs TiB
```

At the beginner level this lesson requires: **storage device manufacturers commonly advertise
capacity using decimal prefixes** (where 1 GB = 1,000,000,000 bytes), **while operating systems
may display related quantities using a different, binary-based convention** (where 1 GiB =
1,073,741,824 bytes) — even when the operating system's display still uses the label "GB" rather
than "GiB." This is precisely why a storage device advertised as, say, "1 TB" can sometimes appear
as a smaller number when an operating system reports its capacity — the two are using related but
numerically different conventions, not because any storage capacity has gone missing. **This
lesson does not turn this into an advanced unit-conversion lesson** — the goal is only to prevent
the common confusion of assuming advertised capacity and operating-system-reported capacity should
always match exactly.

---

## 8. Storage Performance

Storage, like RAM (Concept 10) and cache (Concept 9) before it, has more than one relevant
property — capacity is not the only thing that matters.

**Three properties, defined conceptually:**

```text
Capacity
=
how much data can be stored

Latency
=
how long an individual operation takes

Throughput
=
how much data can be transferred over time
```

Capacity and latency are directly recalled from Concept 9 and Concept 10 — the same concepts,
applied here specifically to storage. **Bandwidth** (Concept 1 and Concept 10) is the available
or potential data-transfer capacity/rate, while **throughput** is the actual data-transfer rate
achieved by a workload — how much data really moves per unit of time, as distinct from how long
any single operation takes to begin (latency).

**A fourth property, introduced specifically for storage:**

```text
IOPS
=
input/output operations per second
```

IOPS measures how many individual read/write operations a storage device can handle per second —
relevant specifically when a workload involves **many small operations**, rather than one large,
continuous transfer. **This lesson introduces IOPS only at this conceptual level** — it does not
teach how to measure, benchmark, or optimize for IOPS; that is genuinely later, more advanced
storage-performance-engineering material.

**Why different workloads care about different properties:**

```text
Large sequential transfer
→ throughput matters

Many small operations
→ latency/IOPS may matter
```

Copying one very large file is primarily a throughput-sensitive task — what matters most is how
much data can move per second, overall. By contrast, a workload that performs many small,
individual reads or writes (for example, accessing many small separate files in quick succession)
is more sensitive to latency and IOPS — how quickly each individual small operation can be
completed matters more than the total data volume moved. **This lesson does not teach storage
benchmarking** — how to actually measure these properties on real hardware — nor does it teach
HDD/SSD architecture (that is specifically Concept 12's subject, the very next lesson).

**A required, explicit statement, directly extending this lesson's Primary Learning Objective:**

> More capacity does not automatically mean faster storage.

A storage device with a very large capacity is not guaranteed to have low latency, high
throughput, or strong IOPS performance — these are separate, independently-varying properties,
exactly as Concept 9 and Concept 10 already established for cache size and RAM capacity
respectively. Section 11 (Misconception 3 and Misconception 9) returns to this point directly.

---

## 9. Real-World Examples

### Example 1 — Saving a document

Clicking "save" on a document requests that its data be written to persistent storage, so that
it can still exist the next time the computer is turned on, unlike anything that only ever existed
in RAM during that editing session. The operating system and storage stack may buffer writes, so
"saved" should not be read as meaning that every byte has necessarily already reached the physical
storage medium at that exact instant.

### Example 2 — Installing a Python package

When you install a Python package (a topic not taught in technical depth here — mentioned only as
a familiar example), the package's files — code, resources, and other supporting material —
occupy real storage space on your system, persisting until you remove them.

### Example 3 — Python source code

The Python source files you write for any project are, themselves, persistently stored data —
exactly like this repository's own lesson files. Without storage, none of your written code would
survive being closed or losing power.

### Example 4 — Dataset

A dataset used for AI work — potentially very large — occupies storage space proportional to its
size (Section 7's capacity units directly apply here). A large dataset can require substantial
storage capacity, well beyond what would ever fit comfortably in RAM alone at once.

### Example 5 — AI model files

A trained AI model's saved parameters (its "weights," a term not taught in this lesson) constitute
a model file or checkpoint that must be stored persistently to be reusable later without retraining
from scratch. **This lesson does not provide any specific claim about how large a particular AI
model's files actually are** — real model sizes vary enormously and depend on many
implementation-specific factors well outside Stage 0's scope.

### Example 6 — Logs

When a program or system writes a record of what it did — errors encountered, actions taken, and
so on — to a file, that record becomes persistently stored data, available for review even after
the program that generated it has stopped running. **This lesson does not teach logging systems**
— specific tools or practices for managing logs — only that logs, once written to a file, are an
example of persistently stored data like any other.

---

## 10. Practical Linux/WSL2 Work

As with previous concepts, this section is safe, entirely read-only, normally requires no `sudo`
(some environments may restrict access to certain block-device information), and does
not modify system configuration, partitions, or files. Reminder of your environment:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu
```

**First, establish your environment:**

```bash
uname -a
```

**Inspect filesystem space:**

```bash
df -h
```

*What this shows:* A human-readable summary of filesystem space — for each mounted filesystem, its
total size, how much is used, how much is available, the use percentage, and where it's mounted.

*Illustrative example output from one specific WSL2/Ubuntu environment used while preparing this
lesson — actual WSL2 output varies by installation and configuration, so your own output will
differ and should be treated as your own system's specific values, not a universal expectation:*

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdd       1007G  5.3G  951G   1% /
C:\             193G   80G  113G  42% /mnt/c
D:\             282G  583M  282G   1% /mnt/d
```

Reading this using this lesson's vocabulary: **Filesystem** identifies which underlying
filesystem/device is being reported on; **Size** is that filesystem's total capacity (Section 7);
**Used** and **Avail** show how much of that capacity is currently occupied versus free; **Use%**
is the same information as a percentage; **Mounted on** shows where in the directory structure
that filesystem is accessible from — notice `/mnt/c` and `/mnt/d`, which is exactly how WSL2
exposes Windows drives (C: and D:) to the Linux environment, per this lesson's required WSL2
caveats below.

**A required, explicit caution:**

> `df` reports filesystem space, not a raw physical-drive specification.

`df` tells you about the *filesystem's* reported size and usage — which, especially inside a
virtualized environment like WSL2, is not automatically the same thing as your physical storage
hardware's exact specifications (Section 11, Misconception 6 and Section 12, Scenario 2 both
return to this directly).

**Inspect block-device information, if available:**

```bash
which lsblk
```

If available:

```bash
lsblk
```

*What this shows:* A listing of block devices (a lower-level view of storage than `df`'s
filesystem-level view) — device names, sizes, and mount points, where applicable.

*Example output from the same system referenced above:*

```text
NAME MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda    8:0    0 356.9M  1 disk
sdb    8:16   0 159.4M  1 disk
sdc    8:32   0     1G  0 disk [SWAP]
sdd    8:48   0     1T  0 disk /mnt/wslg/distro
                               /
```

Notice `sdc` is marked `[SWAP]` — a direct, concrete example of Section 1's brief mention of swap:
this is storage space set aside for swap use, not ordinary file storage, and — exactly as Concept
10 cautioned — this is not the same thing as physical RAM.

**A required, explicit caution:** WSL2 may present **virtualized** storage devices here — these
device names and sizes describe what the virtualized environment reports, not necessarily a
direct, one-to-one representation of your physical host's actual disk layout.

**Inspect directory disk usage:**

```bash
du -sh .
```

*What this does:* Reports the total disk space used by the current directory and everything
inside it, in human-readable form.

*What this means:* `du` measures disk usage associated with files/directories in the current
filesystem context — it tells you how much space *this specific set of files* occupies, which is
a completely different question from "how large is the underlying storage device" (Section 11,
Misconception 7).

**Optionally, break this down further — with an important safety caution:**

```bash
du -sh ./*
```

This shows the size of each item directly inside the current directory, rather than only a single
combined total. **A required, explicit safety instruction:**

> Do NOT run this blindly in huge system directories.

Run this only inside your own learning repository, or another directory you know is small and
safe — never inside a large system directory (like `/` or `/usr`), where it could produce an
enormous, slow, and unhelpful amount of output. This command does not modify anything regardless
of where it's run, but choosing a sensible, manageable directory keeps the observation useful and
fast.

**Required WSL2 storage caveats, stated explicitly — matching the pattern from every prior concept
file's practical section:**

- WSL2 uses a virtualized Linux environment — storage visible to Linux inside WSL2 is not
  necessarily a direct representation of the host's physical disk layout.
- Windows drives may be exposed through paths such as `/mnt/c` (as seen directly in this lesson's
  own `df -h` example above) — this is a WSL2-specific mechanism for bridging the Linux and
  Windows filesystems, not a separate, additional physical drive.
- Linux filesystem storage and Windows-mounted paths (like `/mnt/c`) can behave differently —
  this lesson does not teach the specific performance or behavioral differences between them.
- Storage measurements inside WSL2 (from `df`, `lsblk`, or `du`) describe the environment visible
  to Linux specifically — not automatically a complete, unmodified description of the physical
  host's exact hardware.
- **Do not infer exact physical SSD/HDD hardware specifications from `df` or `lsblk` alone** — as
  this lesson's own examples show, WSL2 may report device sizes and layouts that reflect
  virtualization choices, not necessarily your physical drive's exact make, model, or precise
  capacity.

**This lesson does not teach WSL2 storage architecture in depth** — these caveats exist only so
you correctly interpret what you observe.

---

## 11. Common Mistakes

```text
Misconception 1  → "Storage and RAM are the same thing."
Correct idea     → Storage and RAM are structurally different, serving different roles
                    (Concept 10, Section 9; this lesson's Section 2) — storage is persistent
                    and non-volatile; RAM is fast, volatile, active working memory. Both are
                    necessary, for different reasons.
Why it happens   → Both hold "data" a computer works with, which can obscure the fundamental
                    difference in persistence and purpose between them.
```

```text
Misconception 2  → "Storage loses everything when power is removed."
Correct idea     → This is backwards — storage's entire defining purpose (Section 1, Section
                    2) is to retain data specifically *despite* power being removed. RAM is
                    what loses its contents when power is removed; storage is designed
                    specifically not to.
Why it happens   → Confusing storage with RAM (Misconception 1) naturally leads to also
                    confusing their opposite volatility properties.
```

```text
Misconception 3  → "More storage means a faster computer."
Correct idea     → Storage capacity and storage/computer speed are separate properties
                    (Section 8's explicit statement: "more capacity does not automatically
                    mean faster storage") — this is the same "more of one resource
                    automatically means better overall performance" oversimplification Concept
                    2, Concept 3, Concept 9, and Concept 10 have each already corrected for
                    their own respective resources.
Why it happens   → Larger numbers on a spec sheet intuitively suggest "better" across the
                    board, obscuring that capacity and performance are genuinely independent
                    properties.
```

```text
Misconception 4  → "Storage is only for files."
Correct idea     → While files are the logical unit storage is commonly discussed in terms of
                    (Section 1, Section 4), storage holds far more than what a casual user
                    might think of as "files" — programs, datasets, model artifacts,
                    configuration data, and logs (Section 9) can all occupy storage, all of
                    which are, technically, also stored as files at the conceptual level this
                    lesson teaches.
Why it happens   → "Files" often calls to mind documents or photos specifically, obscuring
                    that program code, data, and system information are also organized and
                    stored as files.
```

```text
Misconception 5  → "A file is the same thing as a physical storage device."
Correct idea     → A file is a logical representation of stored data (Section 1's required
                    distinction); a storage device is the actual physical hardware that
                    provides the underlying capacity. A single storage device can hold an
                    enormous number of separate files.
Why it happens   → Casual language ("save it to the drive") can blend the logical concept
                    (a file) with the physical concept (the device it resides on).
```

```text
Misconception 6  → "df -h tells me the exact physical SSD capacity."
Correct idea     → `df` reports filesystem space (Section 10's explicit caution), which,
                    especially inside a virtualized environment like WSL2, is not guaranteed
                    to be an exact, direct representation of the physical storage device's
                    actual specifications.
Why it happens   → `df`'s output looks precise and authoritative, which can obscure the layer
                    of filesystem/virtualization abstraction sitting between it and the raw
                    physical hardware.
```

```text
Misconception 7  → "du tells me how much physical disk hardware exists."
Correct idea     → `du` measures how much space specific files/directories currently occupy
                    (Section 10) — a completely different question from "how large is the
                    underlying storage device," which is closer to what `df` (filesystem
                    capacity) or `lsblk` (block-device size) address instead.
Why it happens   → Both `du` and questions about "how much storage do I have" involve the
                    word "disk"/"storage," which can blur the distinction between "space used
                    by specific files" and "total device capacity."
```

```text
Misconception 8  → "All storage has the same performance."
Correct idea     → Storage devices vary considerably in latency, throughput, and IOPS (Section
                    8) — different storage technologies and devices can have very different
                    performance characteristics, even at the same capacity. Concept 12 (the
                    next lesson) specifically develops this further for HDD vs. SSD.
Why it happens   → Storage is often discussed casually only in terms of capacity ("I have a
                    1 TB drive"), which can obscure that performance is a separate, equally
                    real dimension.
```

```text
Misconception 9  → "More GB always means better storage."
Correct idea     → As Section 8 establishes, capacity and performance (latency, throughput,
                    IOPS) are independent properties — a higher-capacity device is not
                    guaranteed to also be faster, and "better" depends on what a specific
                    workload actually needs, not capacity alone.
Why it happens   → This is a specific instance of Misconception 3's broader "bigger number =
                    better" oversimplification, applied here specifically to storage capacity.
```

```text
Misconception 10 → "Storage is just slower RAM."
Correct idea     → This oversimplifies a real, structural difference, not just a speed
                    difference. Storage and RAM differ fundamentally in volatility (Section 2,
                    Section 5) — storage is specifically designed for persistence across power
                    cycles, a property RAM does not have at all, regardless of how fast or slow
                    any particular RAM or storage device happens to be. Speed is one difference
                    among several, not the defining one.
Why it happens   → Since storage is generally slower than RAM in typical access patterns
                    (Section 8's table, Section 8 of Concept 10), it's tempting to reduce the
                    entire relationship to "just a speed difference," rather than recognizing
                    persistence as the more fundamental, defining distinction.
```

```text
Misconception 11 → "Saving a file means the CPU permanently stores it."
Correct idea     → The CPU does not itself permanently store data — exactly as Concept 6 and
                    Concept 2 established, the CPU executes instructions and works with
                    registers/cache/RAM as temporary working resources. Saving a file involves
                    the CPU issuing/coordinating the operation (per Section 6's walkthrough),
                    but the actual persistent storage happens on the storage device itself, not
                    inside the CPU.
Why it happens   → Because the CPU is central to "making things happen" (a point Concept 2
                    already had to correct once, in its own Misconception 1), it's easy to
                    over-attribute unrelated capabilities — like long-term data retention — to
                    the CPU as well.
```

```text
Misconception 12 → "Deleting a file is the same thing as physically destroying the storage
                    device."
Correct idea     → Deleting a file is a logical operation — it normally changes filesystem
                    metadata/references so that the file is no longer treated as present and
                    its storage space can eventually be reused (Section 1's file/storage
                    distinction) — it does not physically destroy, damage, or remove any part
                    of the underlying storage device itself, which remains intact and reusable
                    for other data.
Why it happens   → "Delete" can sound drastic or destructive in everyday language, which can
                    create a false impression that something physical has been damaged or
                    removed, rather than a purely logical change to what data is currently
                    represented as present.
```

---

## 12. Debugging/Troubleshooting

**Scenario 1 — the learner runs `df -h` and sees `Size`, `Used`, `Avail`, `Use%`, `Mounted on`.**

Each field means, per Section 10: **Size** is the filesystem's total reported capacity; **Used**
is how much of that capacity is currently occupied; **Avail** is how much remains free; **Use%**
expresses used/total as a percentage; **Mounted on** shows where in the directory structure this
particular filesystem is accessible. None of these fields, on their own, describe the exact
physical hardware underneath — they describe the filesystem as the operating system currently
reports it (Section 11, Misconception 6).

**Scenario 2 — the learner says: "My WSL2 `df -h` says 200 GB, so my physical SSD must be exactly
200 GB."**

This requires correction, per Section 10's explicit caution. `df` reports filesystem space, which
inside a virtualized environment like WSL2 reflects what's configured/exposed to that environment
specifically — not necessarily an exact, one-to-one match with the physical SSD's actual, full
capacity. The physical drive could be larger (with only part of it exposed to WSL2 for this
filesystem) or organized differently than a single `df` line suggests.

**Scenario 3 — the learner runs `du -sh .` and thinks the result is the total physical disk
capacity.**

This requires correction, per Section 10 and Misconception 7. `du -sh .` reports how much space
the current directory's *contents* occupy — a measurement of specific files, not of the total
capacity of the underlying storage device. A small `du` result (for example, this lesson's own
repository, likely just a few megabytes of text files) says nothing about how large the overall
storage device it resides on actually is.

**Scenario 4 — the learner says: "I have 1 TB storage, so every application will run faster."**

This requires correction, per Section 8 and Misconception 3/9. Storage capacity and storage
*performance* (latency, throughput, IOPS) are separate properties — having a large amount of
capacity available says nothing about how quickly that storage can actually read or write data,
and even fast storage doesn't uniformly make "every application" faster, since many applications'
performance depends on entirely different factors (CPU speed, RAM, and more, per every prior
concept file in this module).

**Scenario 5 — the learner says: "A Python file exists on storage, therefore the CPU executes the
file directly from the SSD."**

This requires correction, per Section 5's conceptual chain and Concept 7/Concept 8's established
foundation. A CPU cannot execute a file "directly from" storage in the sense this statement
implies — the relevant program/data must first be brought into RAM (Section 2's original
justification for RAM's existence, and Concept 10's entire subject), and, further back, Concept 7
and Concept 8 already established that Python source code isn't directly executed by the CPU at
all — it goes through compilation/interpretation first. Storage holding the file is only the
starting point of a much longer chain this lesson and its predecessors have been building.

**Scenario 6 — the learner says: "RAM is unnecessary because I already have storage."**

This requires correction, per Concept 10 and this lesson's Section 2. RAM and storage serve
different, complementary roles — storage is too slow to serve as the CPU's direct, fast-access
working memory (Concept 10's original justification for RAM's existence), so a computer relying
only on storage (with no RAM at all) would be severely limited in execution speed, even though it
could still retain data persistently. Both are genuinely necessary, for different reasons.

**Scenario 7 — the learner sees `/mnt/c` in WSL2 and assumes it is a separate physical drive.**

This requires correction, per Section 10's WSL2 caveats. `/mnt/c` is how WSL2 exposes your
Windows `C:` drive to the Linux environment — it is a bridging mechanism between Windows and
Linux, not evidence of an entirely separate, additional physical drive existing. This lesson's own
Section 10 example showed `/mnt/c` and `/mnt/d` alongside `/`, reflecting how WSL2 presents both
its own Linux filesystem and Windows drives together, within one unified Linux directory
structure.

---

## 13. Exercises

Work through these in order, showing your reasoning for every explanation or comparison — not
just a final answer.

### Level 1 — Recognition

1. What is storage?
2. What is persistent storage?
3. What does non-volatile mean?
4. What is a storage device?
5. What is a storage medium?
6. What does storage capacity mean?
7. What is latency, in the context of storage?
8. What is throughput, in the context of storage?
9. What does IOPS stand for?
10. What is a file?
11. What is a filesystem, at the conceptual level this lesson introduces it?
12. How is storage different from RAM?
13. How is storage different from cache?
14. How is storage different from registers?
15. Why does storage matter to an Applied AI Engineer?

### Level 2 — Understanding

Answer each in your own words, in at least one or two full sentences.

16. Why does storage exist?
17. Why can't RAM replace persistent storage?
18. What does non-volatile mean?
19. What does persistence mean?
20. What does storage capacity mean?
21. What does latency mean?
22. What does throughput mean?
23. What does IOPS mean?
24. Why doesn't more storage automatically improve performance?
25. Why are files not the same thing as physical storage devices?
26. Why does storage matter to AI engineering specifically?
27. Why do WSL2 storage observations need context before drawing conclusions?

### Level 3 — Application

**Exercise A — Memory hierarchy.** Given `Registers → Cache → RAM → Storage`:

28. Explain the purpose of each layer, in your own words.

**Exercise B — Program lifecycle.** Given:

```text
Python program on storage
        ↓
program runs
        ↓
RAM
        ↓
CPU
```

29. Explain this conceptual flow in your own words, without requiring detailed OS knowledge.

**Exercise C — Storage capacity.** A machine has 1 TB storage.

30. What does this tell you?
31. What does this NOT tell you?

**Exercise D — AI artifacts.** A project contains a dataset, a model checkpoint, Python source
code, logs, and configuration.

32. Explain why all of these can require persistent storage.

**Exercise E — Linux observation.** Run `df -h`, `lsblk` (if available), and `du -sh .` on your
own system.

33. Document what you observed.
34. Explain what each command measures.
35. Explain what each command does NOT tell you.
36. Explain how WSL2 affects the interpretation of your results.

### Level 4 — Debugging

For each statement, identify exactly what's wrong and explain the corrected understanding.

37. "Storage is just slower RAM."
38. "1 TB storage means the computer is faster than a computer with 512 GB."
39. "df -h tells me the physical SSD model and capacity."
40. "du tells me how much physical disk exists."
41. "Programs execute directly from SSD."

### Level 5 — Integration

**Scenario A — Python project.** A Python project contains source code, a virtual environment,
datasets, and generated artifacts.

42. Which information requires persistent storage, and why?
43. What information may later be loaded into RAM?
44. Why are storage and RAM both needed here?

**Scenario B — AI dataset.** An AI project stores a large dataset locally.

45. Why does dataset size affect storage requirements?
46. Why does storage capacity not directly determine model performance?
47. What distinction exists between storing the dataset and processing it?

**Scenario C — Model checkpoint.** A model checkpoint is stored on disk and later loaded for
inference.

48. Why does the checkpoint need persistent storage?
49. Why is it also loaded into working memory when used?
50. Why should storage and RAM not be treated as interchangeable?

**Scenario D — WSL2.** You run `df -h` and `lsblk` inside WSL2.

51. What do these commands reveal?
52. What can they not prove about the physical host?
53. Why does virtualization matter here?

**Solutions are not provided here.** See
[`exercises/11-storage-answer-key.md`](./exercises/11-storage-answer-key.md) — open it only after
attempting every question above.

---

## 14. Practical Learning Task

This is a **storage observation exercise** — it does not create a new project, does not modify
anything in `project/`, and does not add any implementation code to this repository.

**The task:**

1. Identify your Linux/WSL2 environment using `uname -a`.
2. Inspect filesystem space using `df -h`.
3. Inspect available block-device information using `lsblk`, if available.
4. Inspect this repository's (or another safe, user-owned directory's) disk usage using
   `du -sh .`.
5. Compare filesystem capacity (`df`) with directory usage (`du`) — note how different these
   numbers are, and why (Section 10, Section 11).
6. Explain storage vs. RAM, in your own words.
7. Explain persistent vs. volatile memory, in your own words.
8. Identify what the commands you ran reveal.
9. Identify what the commands you ran cannot prove.
10. Document the WSL2 caveats from Section 10 that apply to your observations.

**Explicit boundaries, matching the safety requirements throughout this lesson:**

- Use only the read-only commands from Section 10 — nothing here requires `sudo`.
- Do not format disks, mount or unmount devices, modify partitions, or delete files.
- Do not write large test files or intentionally consume disk space.
- Do not benchmark storage performance.
- Run `du -sh ./*` only inside your own learning repository or another small, safe, user-owned
  directory — never blindly inside a large system directory.
- Do not modify anything inside `project/` — this task is separate from, and does not affect, the
  three existing Module 0.1 projects.

---

## 15. Review Questions and Production Relevance

### Review Questions

Answers are intentionally not provided directly below these questions.

1. What is storage, and what is its defining purpose?
2. What does persistence mean?
3. What does non-volatile mean?
4. What does storage capacity mean?
5. What does latency mean, in the context of storage?
6. What does throughput mean, in the context of storage?
7. What does IOPS mean?
8. What is a file, and how is it different from a storage device?
9. How is storage different from RAM?
10. How is storage different from cache?
11. How is storage different from registers?
12. Why is program source code an example of data that requires persistent storage?
13. Why do datasets commonly require substantial storage?
14. Why does storage matter to Applied AI Engineering work specifically?
15. Why do WSL2 storage observations need to be interpreted carefully?

### Production Relevance

You now understand what storage is, why it exists as the persistent counterpart to RAM's active
working memory, how it relates to files (introduced only conceptually here) and to the rest of the
memory/storage hierarchy, and what capacity, latency, throughput, and IOPS mean as distinct
storage properties.

**How this connects to the bigger picture:**

```text
Application
   ↓
Files / data
   ↓
Operating system
   ↓
Storage
```

and, in the direction of actually using stored data:

```text
Storage
   ↓
load required data
   ↓
RAM
   ↓
Cache
   ↓
CPU
```

These diagrams are a conceptual hierarchy and data-access model, not a universal literal
execution path for every operation. Data or program code stored persistently is made available to
the running system through the memory system, often by being loaded or mapped into memory as
needed — not every file is always copied completely into RAM before use.

This matters directly to a future Applied AI Engineer working with:

- **Source code** — every project you build depends on storage to persist your work reliably.
- **Python environments** — the tools and libraries your projects depend on occupy real,
  persistent storage space.
- **Datasets** — data too large to hold entirely in RAM at once must live in storage, loaded as
  needed.
- **Model artifacts and checkpoints** — trained models must be saved persistently to be reused
  without retraining.
- **Logs** — records of system/application behavior are written to storage for later review.
- **Configuration** — settings that control application behavior must persist between runs.
- **Local development environments** — your entire practical workflow as a developer relies on
  storage working reliably underneath everything else you do.

**This lesson provides conceptual relevance only — it does not teach advanced storage
engineering.** Exactly how filesystems organize data internally (Module 0.2), how HDD and SSD
technology actually differ (Concept 12, the very next lesson), or how large-scale data
infrastructure is designed and operated are all later, more advanced topics, named here only to
show where this lesson's foundation eventually connects.

---

_This file was written as the completed Concept 11 lesson for Module 0.1. It does not teach HDD
internals, SSD internals, NAND flash architecture, NAND cell types (SLC/MLC/TLC/QLC/PLC), flash
translation layers, wear leveling, garbage collection, TRIM internals, NVMe protocol internals,
SATA protocol internals, PCIe storage internals, disk scheduling, filesystem internals, inode
internals, journaling internals, ext4/NTFS/XFS/ZFS internals, block-device internals,
partition-table internals (GPT/MBR), RAID implementation, storage controllers, storage networking,
SAN, NAS architecture, object-storage architecture, distributed storage, database storage engines,
database pages, WAL, LSM trees, B-trees, memory mapping, virtual memory, swap internals, kernel
I/O internals, DMA, page cache internals, filesystem caching internals, cloud storage
architecture, S3 internals, distributed filesystems, storage performance engineering, IOPS
benchmarking, advanced disk benchmarking, SSD endurance calculations, or AI storage optimization
in depth — those remain scaffolded, unwritten concept files (or entirely untouched, in the case of
later-stage or later-module material) until their own turn in the sequence. HDD vs SSD
specifically is the very next concept, Concept 12, and is not taught here. Filesystem internals
specifically belong to Stage 0 — Module 0.2 — Operating System Fundamentals, not this module._
