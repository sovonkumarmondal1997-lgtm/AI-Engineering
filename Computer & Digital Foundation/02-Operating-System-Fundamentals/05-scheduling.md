# Scheduling

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** CPU scheduling, runnable/waiting states, preemption, context switching, fairness, starvation, throughput vs. latency, CPU-bound vs. I/O-bound workloads
**Status:** Not Started

---

## 1. What Is It?

**Connecting to what you already know.** [Processes](03-processes.md) established that a process can be running, waiting, or in several other states, without necessarily using the CPU at every moment it exists. [Threads](04-threads.md) established that a process can contain multiple independent execution paths, each with its own state, and that "concurrency does not necessarily require multiple CPU cores" — a claim this lesson now explains fully. Both lessons deferred one question: **who decides which runnable process or thread actually gets to use the CPU, and when?** That decision-maker is the **scheduler**, and this lesson is entirely about how it works, conceptually. This lesson also depends on [Kernel and User Space](01-kernel-and-user-space.md) and [System Calls](02-system-calls.md) — scheduling is a kernel responsibility, and the same kernel-mediated mechanisms already introduced apply here too, without being repeated.

**CPU scheduling.** Simple meaning: CPU scheduling is how the operating system decides which runnable piece of work gets to use the CPU right now, out of everything that currently wants to run. Technical meaning: CPU scheduling is the kernel's ongoing process of selecting, from among all currently runnable execution entities (processes and threads), which one is granted CPU execution time at any given moment, and for how long.

**Scheduler.** Simple meaning: the part of the operating system that makes this decision. Technical meaning: the scheduler is the kernel component responsible for implementing a scheduling policy — the specific rules used to choose which runnable entity executes next (Section 5).

**Runnable task.** Simple meaning: a process or thread that is ready and able to execute, if given the chance. Technical meaning: "runnable" describes an execution entity that is not currently waiting on anything (Concept 03's and Concept 04's "waiting/blocked" state) and could execute immediately if the CPU were made available to it.

**CPU time / execution opportunity.** Simple meaning: an actual window of time during which a specific task gets to use the CPU. Technical meaning: CPU time refers to the actual periods during which a specific execution entity's instructions are being carried out by a CPU core, as granted by the scheduler.

**Waiting/blocked state.** Already introduced in Concept 03 and Concept 04: a process or thread that exists, but cannot currently make progress because it's waiting for something (a file, a network reply, another event) — and, critically for this lesson, does not need CPU time while it waits.

**Preemption.** Simple meaning: the OS's ability to interrupt a currently running task and hand the CPU to something else. Technical meaning: preemption is the scheduler's ability to suspend a currently executing task before it has voluntarily given up the CPU, in order to grant execution time to a different runnable entity (Section 5).

**Why scheduling exists, in one sentence, expanded fully in Section 2:** there is very often more runnable work than the CPU can execute all at once, so the operating system needs a mechanism for deciding, over and over, "who gets to execute now?"

**The core mental model** for this lesson:

```text
Many runnable execution entities            (processes and/or threads — Concepts 03, 04)
     ↓
Operating system scheduler
     ↓
Selects an execution entity
     ↓
CPU executes it
     ↓
Entity continues / waits / yields / is interrupted
     ↓
Scheduler makes another decision
     ↓
CPU executes another runnable entity
```

**Important caveat, repeated throughout this lesson:** this is a conceptual model, not a literal representation of any one real scheduler's implementation. Real operating systems use genuinely sophisticated scheduling policies (Section 5), and this lesson deliberately does not teach any specific one's internal algorithm or data structures — that level of detail belongs to advanced, later curriculum, not this beginner-level foundation.

---

## 2. Why Does It Exist?

**The fundamental problem: CPU capacity vs. workload.** A computer's CPU has a limited number of cores, each able to actively execute exactly one instruction stream at any given instant (Module 0.1's CPU lessons). But the number of processes and threads that *want* to run — that are runnable, per Section 1 — is very often larger than the number of available cores.

**A concrete illustration:**

```text
CPU cores = 2
Runnable threads = 6      (T1, T2, T3, T4, T5, T6)

Runnable:
T1  T2  T3  T4  T5  T6

CPU:
Core 1 → can execute exactly one of these threads at a time
Core 2 → can execute exactly one of these threads at a time

The other four threads cannot literally execute right now — something
must decide which two run first, for how long, and what happens next.
```

Six runnable threads cannot all literally execute simultaneously on only two CPU cores — this is simply a physical fact about the hardware, not a design choice. **The operating system needs a mechanism for managing these limited execution opportunities fairly and effectively.** That mechanism is the scheduler.

**With multiple cores, real parallel execution is possible** — up to as many runnable entities as there are cores can genuinely execute at the exact same instant (Concept 04's parallelism definition, reinforced in Section 6). **With only one core, tasks can still make progress through time-sharing** — the scheduler rapidly alternates which task is executing, so that over a longer stretch of time, multiple tasks each get *some* progress, even though at any single instant, only one is actually executing on that core.

**Why this matters even as core counts grow:** more cores raise the number of tasks that can genuinely run in parallel, but they don't eliminate the underlying problem — a busy production server can easily have far more runnable threads than it has cores, at which point scheduling decisions matter just as much as they would on a single-core machine.

---

## 3. Why an AI Engineer Needs It

- **Every Python AI service runs inside this same scheduling reality.** Whether your service feels fast or sluggish under load is not purely a function of your application code — it also depends on how the scheduler is currently dividing CPU time among everything runnable on the machine, including work entirely unrelated to your service.
- **"Why did my API get slower when this other job started running?" is a scheduling question.** Section 18's scenarios and Section 11's debugging scenarios both build directly toward being able to reason about exactly this kind of production symptom.
- **CPU-bound and I/O-bound workloads interact with the scheduler very differently** (Section 12) — correctly classifying your own workload is a direct, practical skill for reasoning about whether adding more workers, more threads, or more CPU capacity will actually help.
- **"More workers" is not a free performance lever.** Multiple worker processes or threads are still all competing for the same underlying CPU capacity (Section 2's core example) — understanding scheduling is what lets you reason correctly about when adding workers helps and when it just adds contention.

**CPU scheduling and GPU-accelerated AI workloads.** It's tempting to think that once GPU-accelerated inference or training is involved, CPU scheduling stops mattering. It doesn't. GPU execution is a genuinely separate execution system from CPU scheduling — this lesson does not teach GPU scheduling, CUDA kernel scheduling, or GPU driver internals, all of which are out of scope. But CPU scheduling still matters directly in GPU-accelerated AI systems, because:

- **CPU processes/threads prepare the work** that eventually runs on a GPU — data loading, preprocessing, and orchestration all happen on the CPU, and all of that work is still subject to ordinary CPU scheduling.
- **Data must move between CPU-managed memory and GPU memory**, and the CPU-side code that manages this transfer still competes for CPU scheduling time like any other runnable work.
- **CPU-side orchestration** — deciding what to send to the GPU next, handling the result, managing multiple concurrent requests — consumes real CPU resources, meaning a CPU-scheduling bottleneck can leave an otherwise-idle, powerful GPU waiting for work.

A concrete preview, expanded fully in Section 18:

```text
Python AI service (one process, possibly several workers/threads)
     ↓
several requests arrive at once                → several execution entities become runnable
     ↓
a CPU-heavy preprocessing task is also running   → competing for the same CPU capacity
     ↓
the scheduler decides who executes when            → this decision directly shapes
                                                       request latency and overall throughput,
                                                       independent of whether your code is
                                                       "efficient" in isolation
```

---

## 4. Beginner Explanation

**Analogy: a single barista, many orders.**

```text
Coffee shop with one barista and one espresso machine   = one CPU core
Customers who have placed orders and are waiting          = runnable tasks
The barista actually making a specific drink right now      = the task currently executing
The barista's decision about which order to work on next     = a scheduling decision
The barista pausing one drink to start another                 = preemption/context switching
```

Imagine a coffee shop with exactly one barista and one espresso machine, and five customers who have all placed orders. The barista can only physically make one drink at a time — but a good barista doesn't robotically finish one entire order before even looking at the next. Instead, they make deliberate choices: start drink 1, but while milk is steaming (a "waiting" moment for that drink), glance at drink 2's order and start something on it, then come back to drink 1 once it needs attention again. Over the course of a few minutes, all five customers make progress on their orders, even though the barista was only ever physically doing one specific thing at any single instant.

The barista is making constant, small decisions about *whose* order to attend to *right now* — sometimes based on what's ready to be worked on, sometimes based on who's been waiting longest, sometimes based on which drink is quick versus which is complicated. This is a rough, beginner-level picture of what a scheduler does, continuously, for runnable processes and threads.

**Extending the analogy for multi-core:** now imagine the shop has *two* baristas and two espresso machines. Now two drinks really can be made at the exact literal same instant — this is the shop's version of parallelism (Section 6). With five waiting customers and two baristas, three customers still have to wait for a barista to become free — exactly the "more runnable work than execution capacity" problem from Section 2, just with two execution resources instead of one.

**Where this analogy is useful:** it captures the core shape of scheduling — a limited number of execution resources (baristas), more runnable work than can be handled all at once, and an ongoing, repeated decision process about who goes next, including the ability to pause one thing to attend to another.

**Where this analogy breaks down:**

- A human barista uses judgment and social awareness (who looks impatient, who ordered something quick); a real scheduler follows a defined, consistent policy (Section 5), not situational human judgment.
- Pausing and resuming a drink in this analogy is trivial for a human; a real context switch (Section 6) requires the OS to carefully save and later restore a task's exact execution state, which is why context switching has real, measurable overhead — not something this analogy conveys.
- A barista decides for themselves when to switch; an OS scheduler can also forcibly interrupt a running task through preemption (Section 5) — a running task doesn't get to unilaterally refuse to be paused.

**What you should take away from this section, in one sentence:** because there is usually more runnable work than available CPU execution capacity, the operating system's scheduler continuously decides which runnable process or thread actually gets to execute, for how long, switching between them so that many tasks can each make progress over time.

---

## 5. Technical Explanation

### What the scheduler actually decides

Every time the scheduler makes a decision, it is choosing an answer to: **"Of everything currently runnable, what should execute next, and for how long?"** Several factors can plausibly influence this decision, depending on the specific operating system and its scheduling policy:

| Factor | What it means |
|---|---|
| Which tasks are runnable | Only tasks that are actually ready to execute (not waiting/blocked) are candidates at all |
| Priority | Some tasks may be treated as more or less important than others (Section 5's priority subsection) |
| Fairness | Avoiding a situation where some runnable task never gets a meaningful chance to execute (Section 5's fairness subsection) |
| CPU availability | How many cores exist, and which ones currently have capacity |
| Task behavior | Whether a task tends to use short bursts of CPU (often typical of I/O-bound work) or long continuous stretches (often typical of CPU-bound work) |
| Waiting/blocked state | Tasks that are waiting are simply not eligible to be scheduled onto a CPU right now |
| Scheduling policy | The specific overall strategy the kernel uses to weigh all of the above |
| Time-sharing | How CPU time is divided among runnable tasks over time, on systems with more runnable tasks than cores |
| Latency considerations | Some scheduling decisions favor getting a quick response to certain tasks over maximizing total throughput (Section 5's throughput/latency subsection) |

**An important, explicit correction of a natural but incorrect beginner guess:** it is *not* accurate to say the scheduler simply picks whichever task has been waiting longest, or gives every task strictly equal time. **Real scheduler policies are considerably more sophisticated than either of those simple rules**, weighing multiple factors like the ones above together. This lesson does not teach any specific real scheduler's exact algorithm (Linux's specific scheduler implementation, for example, is explicitly out of this lesson's scope) — only that the decision is genuinely more nuanced than "first come, first served" or "perfectly equal shares."

### Preemption

**Preemption**, defined precisely: the scheduler's ability to interrupt a currently running task — before that task has voluntarily paused or finished — in order to let a different runnable task execute instead.

**Why preemption exists:**

- **Fairness** — without it, one long-running task could simply keep the CPU indefinitely, starving every other runnable task (Section 5's starvation subsection).
- **Responsiveness** — a system that can interrupt a long computation to briefly let something urgent run feels far more responsive than one that can't.
- **Preventing monopolization** — no single task, however important it seems to itself, is allowed unlimited, uninterrupted CPU time by default.
- **Multitasking** — preemption is precisely what makes it possible for a system to run many programs at once, switching between them faithfully enough that each one appears to be making steady progress.

**A conceptual timeline:**

```text
Task A: ████
Task B:     ████
Task A:         ███
Task C:             ████
```

Each transition in this diagram represents a scheduling decision — the scheduler decided to interrupt whatever was currently running and grant CPU time to something else. **This lesson does not teach the hardware-level interrupt mechanism that makes preemption physically possible** — only the conceptual fact that the OS has this capability, and why it's useful.

### Context switching

**Context switch**, defined: the act of the CPU stopping execution of one task and beginning (or resuming) execution of another, while preserving enough of each task's state that it can correctly continue later, exactly where it left off.

```text
Running task A
     ↓
OS saves task A's execution state          (enough information to resume it correctly later)
     ↓
OS restores task B's previously saved execution state
     ↓
Task B runs
     ↓
OS may later switch again
     ↓
Task A resumes, exactly where it left off
```

**Connecting to what you already know:** Concept 04 described each thread as having its own execution state and its own stack, distinct from other threads. A context switch is precisely the mechanism that makes this matter in practice — the OS must save one task's execution context (conceptually, its in-progress register values and its position in the code — Module 0.1's CPU lessons, not repeated here) before it can safely let another task use the CPU, and restore it correctly later.

**Context switching happens between threads, not only between processes.** Switching which thread is executing — even within the same process — is also a context switch; it is not a concept reserved only for switching between entirely separate processes.

**Context switching has real overhead.** Saving and restoring execution state takes actual time — it is not free. This is part of *why* the scheduler doesn't switch tasks after every single instruction; excessive switching would waste a meaningful share of CPU time purely on switching overhead rather than useful work. This lesson does not teach the specific architecture-level instructions or data structures involved in performing a context switch — only that the operation is real, necessary, and has a genuine cost.

### Scheduling and process/thread states, connected

```text
Runnable
     ↓
Running                    (currently executing — the scheduler chose this entity)
     ↓
Waiting / blocked           (cannot currently continue — waiting for an event/resource)
     ↓
Runnable                     (the event/resource became available again)
     ↓
Running
     ↓
Terminated
```

This mirrors Concept 03's and Concept 04's state models directly, now with the scheduler's specific role made explicit: **"runnable" means eligible to receive CPU time when the scheduler next chooses it; "running" means the scheduler has currently chosen it and it is actively executing; "waiting/blocked" means it is not currently eligible, because it's waiting for something else entirely (an event, a resource) that has nothing to do with the scheduler's decision.** A waiting task generally does not need to consume CPU continuously while it waits — a direct, important consequence covered further in Section 9's observations.

**Not every operating system uses exactly these state names.** This is a conceptual model; Section 9 explicitly connects it to Linux-specific `ps` state notation without treating that notation as universal.

### CPU-bound vs. I/O-bound work

This distinction matters enormously for how a workload interacts with scheduling, and directly for AI-engineering reasoning (Section 18).

**CPU-bound.** Simple meaning: work that spends most of its time actually computing. Technical meaning: a CPU-bound task's execution time is dominated by CPU computation rather than waiting on external resources — it stays runnable and actively executing for long, largely continuous stretches whenever the scheduler grants it CPU time. Examples: numerical computation, CPU-heavy preprocessing, CPU-heavy data transformation.

**I/O-bound.** Simple meaning: work that spends most of its time waiting for something else. Technical meaning: an I/O-bound task's execution time is dominated by waiting for external resources (network responses, disk/file operations, database operations, external API calls) rather than active computation — it frequently transitions into the waiting/blocked state, needing very little continuous CPU time relative to how long it takes overall to complete.

**Why this distinction interacts differently with scheduling:** a CPU-bound task wants sustained CPU execution time and directly competes with other CPU-bound work for it; an I/O-bound task spends much of its life *not* runnable at all (while waiting), so it can share CPU capacity with other work far more easily, and preemption/context-switching between many I/O-bound tasks is often what makes a system with far more runnable-at-various-times tasks than cores still feel responsive.

**Not every AI workload is GPU-bound.** Data loading, preprocessing, orchestration logic, and API-facing request handling in a typical AI service are frequently CPU-bound or I/O-bound work happening on the CPU, entirely separate from whatever GPU-bound computation a model's inference might also involve (Section 3's GPU subsection).

### Priority and fairness

**Priority.** Some tasks may be given different scheduling priorities, which can influence how much or how promptly they receive CPU time relative to other runnable tasks. **This lesson does not teach how to configure or change process priority** (tools like `nice`/`renice`, or real-time scheduling configuration, are mentioned here only by name, as advanced topics entirely outside this lesson's practical scope — they are not used as hands-on exercises in this lesson).

**Fairness.** Simple meaning: making sure no runnable task is effectively ignored forever just because other tasks keep getting chosen instead. Technical meaning: fairness, as a scheduling goal, means the policy avoids indefinitely denying CPU execution opportunities to any specific runnable task, even while accounting for priority and other factors.

**Starvation.** Simple meaning: when a runnable task keeps *not* getting a fair chance to run, for a long time, because other tasks keep being chosen instead. Technical meaning: starvation occurs when a runnable task receives insufficient CPU execution opportunity relative to other work, over a meaningful stretch of time, due to scheduling policy or priority effects — an outcome well-designed scheduling policies specifically try to avoid, though this lesson does not teach the theoretical guarantees or proofs behind any specific policy's fairness properties.

**A simple conceptual example:** if a scheduling policy always chose the highest-priority runnable task with no other consideration, and high-priority tasks kept arriving continuously, a low-priority task could in principle wait indefinitely — this is the shape of a starvation problem, without this lesson claiming any particular real scheduler actually behaves this simplistically (Section 5 already noted real policies are more sophisticated than any single simple rule).

### Throughput vs. latency

**Throughput.** Simple meaning: how much total work gets completed over a stretch of time. Technical meaning: throughput measures the total volume of work a system completes per unit of time — for example, requests handled per second, or batches processed per hour.

**Latency.** Simple meaning: how long one specific task takes to get done. Technical meaning: latency measures the time a single operation or task takes from when it becomes runnable (or is requested) to when it completes (or receives service).

**Why scheduling policy can involve a real trade-off between them:** a policy tuned to maximize total throughput might let some tasks wait relatively longer in exchange for more total work completed overall; a policy tuned to minimize latency for specific tasks might interrupt other work more frequently to keep response times low, at some cost to total throughput. **No single scheduler setting optimizes every workload** — a batch-processing workload generally cares most about throughput, while an interactive API request generally cares most about latency, and these preferences can genuinely conflict when both kinds of work share the same machine (Section 18's scenarios return to this directly).

### Multi-core scheduling

**One CPU core:** one execution stream can execute at any given instant — multiple runnable tasks on one core must take turns (time-sharing/concurrency, Section 6).

**Multiple CPU cores:** multiple execution streams can execute at the exact same instant — genuine parallelism becomes possible, up to the number of cores available.

**The scheduler's job, generalized to multiple cores:** it must coordinate runnable work across *all* available CPU execution resources — deciding not just "who runs next" but "who runs next, and on which core." **This lesson does not teach CPU affinity configuration, NUMA, cache topology, or advanced load-balancing algorithms** — all genuinely important topics for advanced systems engineering, but well beyond this beginner-level foundation.

---

## 6. How It Works Internally

### The scheduling cycle

```text
Runnable tasks
     ↓
Scheduler evaluates runnable work
     ↓
Execution entity selected
     ↓
CPU executes it
     ↓
Task:
     - continues
     - waits
     - blocks
     - completes
     - gets preempted
     ↓
Scheduler evaluates again
     ↓
Next execution opportunity
```

This cycle repeats continuously, for as long as the system is running — it is not a one-time event, but the ongoing, moment-to-moment mechanism by which every runnable process and thread on the system eventually gets its turn.

### Concurrency vs. parallelism, with timelines

This distinction, first introduced in Concept 03 and Concept 04, is now shown directly as a consequence of scheduling.

**One core — concurrency, not parallelism:**

```text
Time  →  0   1   2   3   4   5   6   7   8
Core 1:  A   A   A   B   B   B   A   A   B
```

Only one letter appears at any single moment in time — never two at once. Tasks A and B are both making progress *over* this stretch of time, but never executing at the literal same instant. This is concurrency: overlapping progress, achieved entirely through the scheduler rapidly switching which task is running.

**Two cores — genuine parallelism:**

```text
Time  →  0   1   2   3   4   5
Core 1:  A   A   A   A   A   A
Core 2:  B   B   B   B   B   B
```

Here, A and B genuinely execute at the same instant, on separate cores — this is parallelism, and it requires more than one execution resource to be possible at all.

**Scheduling is what enables controlled sharing of CPU execution opportunities in both cases** — on a single core, it's the entire mechanism making concurrency possible; on multiple cores, it additionally decides how to distribute runnable work across the available parallel execution resources.

### Python's perspective on scheduling

Concept 04 introduced Python's `threading` module and the CPython GIL. This lesson adds the scheduling-specific piece of that picture.

```text
Python program                     e.g. a script defining functions and calling them
     ↓
Python process                      the running interpreter instance (Concept 03)
     ↓
Python threads                       Concept 04's OS-managed execution paths within it
     ↓
OS scheduling                         this lesson — decides which runnable thread/process
                                       actually gets CPU time
     ↓
CPU execution
```

**The single most important clarification in this subsection:** the operating system's scheduler does not understand Python functions, and has no concept of what `def generate_embeddings(): ...` means. The scheduler operates entirely on OS-managed execution entities (processes and threads, Concepts 03–04) — it schedules *threads*, not Python-level function calls, Python objects, or Python-level logical tasks.

**Two scheduling-relevant layers, kept clearly separate:**

- **OS scheduling** — what this lesson teaches: the kernel deciding which runnable OS thread/process gets CPU time. This layer exists for every program on the system, in every language.
- **Python runtime behavior (the GIL)** — a CPython-specific constraint, already introduced in Concept 04, that affects which of a Python process's *threads* can be actively executing Python bytecode at a given moment, even when the OS scheduler has made multiple of that process's threads "running" from the OS's point of view.

**These are not the same concept, and conflating them is a direct source of confusion:** the OS scheduler can absolutely grant CPU time to more than one of a Python process's threads; what CPython's GIL constrains is something layered *on top of* that, specific to CPU-bound Python bytecode execution within one process. I/O-bound Python workloads (Section 5, Section 18) benefit from OS-level thread scheduling largely undisturbed by this extra constraint, because a thread that's waiting on I/O isn't holding the GIL in the first place. **This lesson does not re-teach the GIL's full mechanics** (Concept 04 already covered it carefully) — only its relationship to the OS-scheduling concepts this lesson introduces.

**Why processes provide a separate execution context worth remembering here:** because CPython's GIL applies within a single process, running separate Python *processes* (Concept 03) — each with its own interpreter and its own GIL — is one way real systems get around GIL-related constraints for CPU-bound work. This lesson does not teach Python multiprocessing in depth; it is mentioned only to connect this lesson's scheduling model back to the process/thread distinction Concepts 03–04 already built.

---

## 7. Real-World Example

Each example states the workload, its runnable/waiting behavior, its CPU requirement, the scheduling implication, and the engineering trade-off involved.

| Example | Workload | Runnable/waiting behavior | CPU requirement | Scheduling implication | Engineering trade-off |
|---|---|---|---|---|---|
| 1. Web server handling requests | Accepting and responding to client connections | Mostly waiting on network I/O between requests | Generally modest per request | Many runnable-when-active entities, each briefly | Responsiveness vs. total throughput under load |
| 2. Python API process | A FastAPI/similar service process | Alternates between handling logic (runnable) and waiting on I/O | Varies by endpoint | Competes with other processes on the machine for CPU time | Simplicity of one process vs. scaling via more workers |
| 3. Background worker | A queue-consuming or scheduled task | Runnable when work is available, waiting otherwise | Depends on the task | Competes with request-serving work for CPU (Section 18) | Background throughput vs. foreground responsiveness |
| 4. CPU-heavy data preprocessing | Transforming/cleaning a dataset | Runnable for long stretches — CPU-bound (Section 5) | High, sustained | Can noticeably delay other runnable work sharing the same CPU | Preprocessing speed vs. other services' responsiveness |
| 5. I/O-heavy application | An app mostly calling external services | Frequently waiting/blocked | Low, in short bursts | Shares CPU easily with other work, since it needs little continuous time | Simplicity vs. maximizing concurrent I/O in flight |
| 6. Batch inference | Processing many inputs without a live user waiting | Runnable for long stretches, CPU/GPU-bound | High (CPU for prep, possibly GPU for compute) | Scheduling favors throughput over any single item's latency | Throughput-oriented tuning vs. responsiveness (Section 5) |
| 7. Online inference | Serving live prediction requests | Runnable in short bursts per request | Moderate to high, latency-sensitive | Scheduling responsiveness for this work matters directly to user experience | Latency-sensitive priority vs. fairness to other runnable work |
| 8. Multiple worker processes | Several processes handling load together (Concept 03) | Each independently runnable/waiting per its own work | Aggregate demand can exceed available cores | Scheduler distributes CPU time across all of them (Section 5) | More workers can raise throughput but also raise contention |
| 9. Multiple threads in one process | Several threads sharing one process (Concept 04) | Each thread independently runnable/waiting | Aggregate demand within one process | Scheduler treats threads as schedulable entities (Concept 04) too | Shared-memory convenience vs. GIL/synchronization considerations |
| 10. A process waiting for I/O | Any process blocked on a file/network/database call | Waiting/blocked — not runnable | Near-zero while waiting | Doesn't compete for CPU time during this period | Nothing to trade off — this is expected, efficient behavior |
| 11. Several CPU-bound tasks competing | Multiple heavy computations runnable at once | All runnable, all CPU-bound | High, cumulatively exceeding available cores | Direct competition for CPU time (Section 2's core example) | Running them concurrently vs. serializing to protect other work |
| 12. AI service responsiveness under CPU load | An online API sharing a machine with a CPU-heavy job | API work becomes runnable amid already-runnable CPU-bound work | Both compete for the same cores | Scheduling decisions directly affect API latency (Section 18's Scenario 2) | Isolating workloads vs. simplicity of running them together |

---

## 8. Relationships to Other Concepts

| Concept | Relationship to scheduling | Prerequisite or later? | Full treatment |
|---|---|---|---|
| Kernel and User Space | Scheduling is a kernel responsibility; application code in user space has no direct control over it | Prerequisite (Concept 01) | Already covered |
| System Calls | Scheduling decisions can be triggered by system calls (e.g., a task blocking on I/O makes it not runnable) | Prerequisite (Concept 02) | Already covered |
| Processes | Provide one kind of schedulable execution entity, with their own resource/isolation boundary | Prerequisite (Concept 03) | Already covered |
| Threads | Provide execution paths within a process; on Linux, threads are important schedulable entities in their own right (Concept 04, Section 6) | Prerequisite (Concept 04) | Already covered |
| Virtual Memory | Provides the memory context the scheduler must ensure is correctly available whenever a task is scheduled to run | Later | Concept 06 |
| Filesystems | File I/O is a common reason a task transitions to waiting/blocked, removing it from scheduling contention temporarily | Later | Concept 07 |
| Permissions | Independent of scheduling — governs what a task may access, not when it executes | Later | Concept 08 |
| Environment Variables | Independent of scheduling — part of a process's environment (Concept 03), not its execution timing | Later | Concept 09 |
| Signals | Can affect a process's/thread's state (for example, waking it or stopping it), which in turn affects its scheduling eligibility | Later | Concept 10 |
| Standard Input/Output | Waiting on I/O (Section 5) commonly involves these channels, directly affecting runnable/waiting transitions | Later | Concept 11 |
| Pipes | Communication through pipes can cause a task to block (waiting for data), again affecting scheduling eligibility | Later | Concept 12 |
| Shell | A process (Concept 03) itself subject to ordinary scheduling like any other | Later | Concept 13 |
| Process Lifecycle | Scheduling operates throughout a process's runnable/running/waiting phases, between creation and termination | Later | Concept 14 |

**The chain this lesson completes, stated explicitly:**

```text
Processes (Concept 03)         → the resource/isolation container
     ↓
Threads (Concept 04)            → multiple execution paths inside that container
     ↓
Runnable execution                → threads/processes eligible for CPU time
     ↓
Scheduler (this lesson)             → decides which runnable entity executes, when, for how long
     ↓
CPU execution                         → the actual work getting done
```

**Later concepts build on this model without repeating it.** Virtual Memory (Concept 06, next) will explain what must be true about a task's memory for the scheduler to safely run it; this lesson does not anticipate that detail.

---

## 9. Practical Observation / Commands

You are working in Ubuntu inside WSL2. All commands below are safe, read-only, and involve no `sudo`, no package installation, no scheduling-policy changes, no priority changes, and no CPU-affinity changes. The lab's bounded CPU-bound processes are the only ones ever inspected or waited on — no unrelated process is touched.

### CPU inspection first: `nproc` and `lscpu`

```bash
nproc
```

Actual observed output in this environment:

```text
8
```

```bash
lscpu
```

Actual observed output (trimmed to the fields this lesson needs):

```text
Architecture:                            x86_64
CPU(s):                                  8
Vendor ID:                               GenuineIntel
Model name:                              Intel(R) Core(TM) i7-8650U CPU @ 1.90GHz
Thread(s) per core:                      2
Core(s) per socket:                      4
Socket(s):                               1
Virtualization:                          VT-x
Hypervisor vendor:                       Microsoft
Virtualization type:                     full
```

**What to notice:** `CPU(s): 8` matches `nproc`'s output — this environment has 8 logical CPUs available to schedule work onto (4 physical cores, 2 threads per core). The `Hypervisor vendor: Microsoft` line is a direct, concrete confirmation that this is a virtualized WSL2 environment, not a bare-metal Linux installation — a caveat worth keeping in mind for every CPU-related observation in this lesson: **what's reported here is what WSL2 exposes to this Linux environment, not necessarily an unmediated view of the physical host's full capability or of how Windows itself is scheduling this VM against other host activity.**

### `htop` — checked, not assumed

```bash
command -v htop
```

**Actual result in this environment:** not installed (exit status 1, no output) — consistent with the previous two lessons in this module. As before, it is not installed as part of this lesson; `ps` and `top`, both used below, are sufficient.

### Safe scheduling observation lab

This lab uses **bounded-duration** CPU-bound Python processes — each runs for a fixed, short wall-clock time and then exits on its own — deliberately avoiding any unbounded or infinite loop. Nothing is force-terminated; every process in this lab is simply allowed to finish naturally, and its completion is verified afterward.

**The bounded workload used**, entered directly for this observation (not saved as a permanent project file):

```python
import time
start = time.time()
x = 0
while time.time() - start < 2.5:
    x += 1
print("done, x =", x)
```

This busy-loop runs for a fixed 2.5 seconds of wall-clock time, regardless of the machine's speed, then exits — a deliberately bounded, safe stand-in for genuine CPU-bound work.

**Step 1 — start two of these processes at once**, to create more runnable CPU-bound work than a single core could handle alone, and capture their PIDs:

```bash
python3 -c "$CMD" &   # CMD holds the busy-loop code above
PID1=$!
python3 -c "$CMD" &
PID2=$!
echo "Started PID1=$PID1 PID2=$PID2"
```

Actual observed output:

```text
Started PID1=5697 PID2=5698
```

**Step 2 — while both are still running, inspect them with `ps`:**

```bash
ps -p "$PID1,$PID2" -o pid,ppid,stat,%cpu,%mem,cmd
```

Actual observed output:

```text
    PID    PPID STAT %CPU %MEM CMD
   5697    5695 R    98.7  0.2 python3 -c ...
   5698    5695 R    98.7  0.2 python3 -c ...
```

**What this demonstrates, concretely:** both processes show `STAT R` (running — Concept 03's Linux-specific state notation) and roughly `98.7%` CPU each, at the same moment. Because this environment has 8 logical CPUs (confirmed above) and only 2 CPU-bound processes were competing, **both got to run in genuine parallel**, each essentially saturating one logical CPU — a direct, observed instance of Section 6's "multiple cores permit genuine parallelism" diagram, with real numbers instead of an abstract example. On a machine with fewer available CPUs than runnable CPU-bound tasks, this same lab would instead show lower per-process `%CPU` figures, as the scheduler time-shared a smaller number of cores across more runnable work — this lesson did not need to force that scenario to demonstrate the underlying principle, since the principle itself (Section 2, Section 6) holds regardless of which specific numbers a given machine happens to produce.

**Step 3 — a `top` snapshot capturing the same kind of moment**, from a separate single-process run of the same bounded workload:

```bash
top -b -n 1
```

Actual observed output (trimmed to the relevant rows):

```text
top - 14:37:17 up  1:01,  1 user,  load average: 0.20, 0.13, 0.10
Tasks:  33 total,   2 running,  31 sleeping,   0 stopped,   0 zombie
%Cpu(s): 13.4 us,  0.0 sy,  0.0 ni, 86.6 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   5716 sovon     20   0   16056   9972   6872 R 100.0   0.3   0:00.70 python3
      1 root      20   0   24416  14688  10620 S   0.0   0.4   0:01.81 systemd
```

The bounded Python process (PID `5716`) shows `S` (state) `R` and `100.0%` CPU, actively saturating one logical CPU, while `systemd` (PID `1`) sits at `0.0%` — visibly `S` (sleeping/waiting), consistent with Section 5's "a waiting task generally does not need to consume CPU continuously."

**Step 4 — let both processes finish naturally, and verify cleanup:**

```bash
wait "$PID1"; echo "PID1 exit status: $?"
wait "$PID2"; echo "PID2 exit status: $?"
ps -p "$PID1,$PID2"
```

Actual observed output:

```text
done, x = 17502462
done, x = 17252256
PID1 exit status: 0
PID2 exit status: 0
    PID TTY          TIME CMD
```

Both processes completed on their own (their bounded 2.5-second loops simply ran out), both exited successfully (status `0`, Concept 03), and the final, empty `ps` result confirms neither process — nor anything else this lab created — remains running. **No `kill` was needed anywhere in this lab; every process was allowed to finish naturally, exactly as this lesson's safety rules require.**

**A note on interpreting these numbers, generally:** the exact CPU percentages, PIDs, and even how many processes can genuinely run in parallel on your own machine will vary by CPU core count, current system load, WSL2's configuration, what else is running on the Windows host at the time, and simple timing — none of this is a discrepancy to worry about; it's exactly what Section 6's model predicts should vary between environments and runs.

---

## 10. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "If a process is running, it is continuously using the CPU." | "Running" means currently executing at this instant; a process can be running now and waiting a moment later, and the two states can alternate rapidly (Section 5). |
| "Every process gets its own CPU core." | Only as many processes/threads as there are cores can literally execute at the same instant; the rest share cores via time-sharing (Section 2, Section 6). |
| "The OS runs all processes at exactly the same time." | On a machine with fewer cores than runnable tasks, tasks take turns (concurrency), not literal simultaneous execution (Section 6). |
| "Concurrency means parallelism." | Concurrency is overlapping progress over time; parallelism specifically requires literal simultaneous execution on separate cores (Section 6) — Concept 04 already introduced this distinction, and it applies identically here. |
| "Multiple CPU cores mean scheduling is no longer necessary." | Even with many cores, the number of runnable tasks can still exceed available cores (Section 2); scheduling remains necessary whenever that's true. |
| "The scheduler chooses the process that started first." | Real scheduling policies weigh multiple factors (priority, fairness, task behavior, and more — Section 5), not simply arrival order. |
| "The scheduler simply gives every process the same amount of CPU time." | Real policies are more nuanced than strict equal division, accounting for priority and other factors (Section 5) — this lesson deliberately avoids claiming any single simple rule describes real schedulers. |
| "A waiting process is still actively consuming CPU." | A waiting/blocked process generally needs little to no CPU time while it waits (Section 5, Section 9's `top` observation of `systemd` at `0.0%`). |
| "Context switching means copying the entire process." | A context switch preserves execution state (registers, position in code) so execution can resume correctly — it is not a full copy of the process's entire memory or resources (Section 5). |
| "Context switching always happens between processes, never threads." | Switching which thread executes — even within the same process — is also a context switch (Section 5). |
| "A CPU-bound process is always using 100% CPU." | A CPU-bound process *wants* sustained CPU time and will use close to 100% of a core when granted it, but it can still be waiting for its turn if other work is competing for the same limited cores (Section 5, Section 9). |
| "High CPU usage automatically means a bug." | Sustained high CPU usage can reflect entirely legitimate, expected work (Section 9's bounded lab intentionally produced ~100% CPU by design) — high usage alone doesn't indicate a problem (Concept 03's related misconception, reinforced here). |
| "Low CPU usage means a process is healthy." | Low CPU usage can also mean a process is stuck waiting on something that should have responded already (Section 11's Scenario 7) — low usage alone doesn't guarantee everything is fine. |
| "I/O-bound tasks do not involve scheduling." | I/O-bound tasks are still scheduled during the (often brief) periods when they are runnable; they simply spend more time in the waiting/blocked state, needing CPU less continuously (Section 5). |
| "The OS scheduler understands Python functions." | The scheduler operates on OS-managed threads and processes; it has no concept of Python-level functions, objects, or logical tasks (Section 6). |
| "Python's GIL is the same thing as the OS scheduler." | The OS scheduler decides which OS threads get CPU time; the GIL is a separate, CPython-specific constraint layered on top of that, affecting which thread can execute Python bytecode at a given moment (Section 6). |
| "The GIL means Python threads never run concurrently." | Python threads can still make concurrent progress, especially for I/O-bound work, where a thread waiting on I/O isn't holding the GIL (Concept 04, Section 6). |
| "Scheduling only matters for operating-system developers." | Every Python AI service's real-world latency and throughput is directly shaped by scheduling decisions happening underneath it (Section 3, Section 18). |
| "GPU acceleration makes CPU scheduling irrelevant." | CPU-side preparation, orchestration, and data movement around GPU-accelerated work still depend entirely on ordinary CPU scheduling (Section 3). |
| "More workers always improve AI-service performance." | More workers means more runnable work competing for the same underlying CPU capacity; beyond a certain point, additional workers can increase contention rather than throughput (Section 2, Section 18's Scenario 5). |

---

## 11. Debugging and Troubleshooting

Each scenario follows: problem, beginner's likely assumption, correct mental model, investigation approach, and expected conclusion.

**Scenario 1 — A Python AI service consumes significant CPU.**

1. *Problem:* `ps`/`top` shows a Python service process using a high share of CPU.
2. *Beginner's likely assumption:* "The scheduler must be misbehaving, or something in the OS is wrong."
3. *Correct mental model:* high CPU usage reflects that this process is runnable and doing genuine (or excessive) computation — it says nothing, by itself, about the scheduler being at fault; the scheduler is simply granting CPU time to work that's asking for it (Section 10).
4. *Investigation approach:* consider the workload itself first — how many worker processes/threads are running, what kind of work they're doing (CPU-bound, per Section 5), and whether the observed usage matches what that workload should reasonably require.
5. *Expected conclusion:* the scheduler is very rarely the root cause of unexpectedly high CPU usage — the workload, its concurrency level, and its CPU-bound nature are the more likely places to look first.

**Scenario 2 — A background CPU-heavy job causes API request latency to increase.**

1. *Problem:* while a background CPU-heavy job runs, an otherwise-fine API service becomes noticeably slower to respond.
2. *Beginner's likely assumption:* "There must be a bug in the API code that only shows up under certain conditions."
3. *Correct mental model:* both the background job and the API's request-handling work are runnable at the same time, competing for the same limited CPU capacity (Section 2); the scheduler dividing time between them can directly increase the API's latency, with no change to the API's own code at all.
4. *Investigation approach:* check whether the slowdown correlates specifically with the background job's activity, and whether the machine's total runnable CPU-bound work exceeds its available cores during that window (Section 9's `nproc`/`lscpu` observations are directly relevant here).
5. *Expected conclusion:* this is a resource-contention/scheduling effect, not necessarily an application bug — a direct, realistic application of Section 2's core problem.

**Scenario 3 — Several workers are competing for limited CPU resources.**

1. *Problem:* a service running several worker processes/threads shows degraded per-request performance as load increases.
2. *Beginner's likely assumption:* "Adding more workers should always help; something else must be broken."
3. *Correct mental model:* every worker, once runnable, competes for the same underlying CPU capacity (Section 2); beyond the point where runnable work exceeds available cores, adding more workers increases contention rather than proportionally increasing throughput, and can even increase per-request latency (Section 5's throughput/latency trade-off).
4. *Investigation approach:* compare the number of concurrently active workers against `nproc`'s reported core count, and consider whether the workload is CPU-bound (where this ceiling matters directly) or I/O-bound (where it matters much less, per Section 5).
5. *Expected conclusion:* "more workers" has a genuine capacity ceiling tied to available CPU cores for CPU-bound work — recognizing this ceiling is a direct, practical scheduling-informed conclusion, not a sign of something broken.

**Scenario 4 — A process exists but uses very little CPU.**

1. *Problem:* a process is visibly running (`ps` shows it) but its CPU usage stays near zero.
2. *Beginner's likely assumption:* "It must be frozen or broken."
3. *Correct mental model:* a process spending most of its time waiting/blocked (Section 5) — on I/O, a network reply, or another event — will show low CPU usage precisely *because* it's doing exactly what I/O-bound work is expected to do, not because it's malfunctioning (Concept 03's related debugging scenario, reinforced here with the scheduling explanation for *why*).
4. *Investigation approach:* check the process's state (`ps`'s `STAT` column, Concept 03) — a sleeping/waiting state alongside near-zero CPU is consistent with legitimate I/O-bound behavior, not evidence of a problem by itself.
5. *Expected conclusion:* low CPU usage on its own is not evidence of a broken process — it is the expected signature of I/O-bound work, and further investigation (is the wait unusually long?) would be needed before concluding anything is actually wrong.

**Scenario 5 — More threads do not improve CPU performance.**

1. *Problem:* a learner adds more threads to a CPU-heavy Python workload and doesn't see the expected speedup.
2. *Beginner's likely assumption:* "The OS scheduler must not be distributing my threads across cores properly."
3. *Correct mental model:* this could stem from several distinct causes — the workload may already exceed available core count (Section 2), or, specific to Python, CPython's GIL (Section 6) may be constraining how much of this CPU-bound work can actually execute in parallel within a single process, regardless of how many OS threads exist.
4. *Investigation approach:* first check whether more threads were created than available cores (`nproc`); separately, consider whether this is CPU-bound work running as Python threads within one CPython process, in which case Concept 04's GIL discussion and Section 6's clarification both apply directly.
5. *Expected conclusion:* there is no single universal cause here — both a genuine CPU-capacity ceiling and Python-runtime-specific constraints are plausible, non-exclusive explanations, and distinguishing between them requires knowing both the core count and the runtime being used.

**Scenario 6 — CPU usage appears different across tools.**

1. *Problem:* `ps` and `top` (or two different moments of the same tool) report noticeably different CPU percentages for what seems like the same activity.
2. *Beginner's likely assumption:* "One of these tools must be wrong or broken."
3. *Correct mental model:* CPU percentage is a *measurement*, not a direct window into every scheduler decision — different tools sample at different intervals, average over different time windows, and may present process-level versus thread-level views differently (Concept 04's `ps -T`/`ps -L` distinction is directly relevant here).
4. *Investigation approach:* check whether the two readings were taken at genuinely the same moment, over comparable time windows, and at the same level (whole process vs. individual thread) before assuming a contradiction.
5. *Expected conclusion:* differing CPU readings across tools or moments are usually a sampling/measurement artifact, not evidence that either tool is malfunctioning — this lesson's own lab (Section 9) intentionally distinguished "actual observed output" from general expectations for exactly this reason.

**Scenario 7 — One task appears "stuck."**

1. *Problem:* a task hasn't produced any visible progress in a while, and the learner isn't sure what kind of "stuck" this is.
2. *Beginner's likely assumption:* "It's stuck, so something is definitely broken."
3. *Correct mental model:* "stuck" can mean several genuinely different things — CPU-bound and legitimately still computing (Section 5), waiting/blocked on a slow but eventually-responding resource (Section 5), truly blocked indefinitely on something that will never resolve, or exhibiting deadlock-like application behavior. **This lesson does not teach synchronization internals or how to diagnose deadlocks** (that belongs to more advanced curriculum) — only how to tell these categories apart at a basic level.
4. *Investigation approach:* check the task's CPU usage and state (`ps`) — high, sustained CPU usage suggests it's still actively computing (CPU-bound, possibly just slow); near-zero CPU with a waiting state suggests it's blocked on something; near-zero CPU that persists far longer than the resource it's waiting on should reasonably take suggests a genuine problem worth investigating further.
5. *Expected conclusion:* "stuck" is not one single diagnosis — correctly distinguishing "still legitimately computing," "normally waiting," and "abnormally stuck" is the practical, transferable skill this scenario is built to teach, even though this lesson does not go further into diagnosing the last category's specific causes.

---

## 12. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. In your own words, what is CPU scheduling?
2. What does "runnable" mean, and how is it different from "running"?
3. What is preemption?
4. What is a context switch?
5. What is the difference between throughput and latency?
6. What does `nproc` report, and how was it used in this lesson's lab?
7. Was `htop` available in this lesson's environment? How was that determined?
8. What does CPU-bound mean, and what does I/O-bound mean?

### Level 2 — Understanding

9. Explain why an operating system needs a scheduler at all, using Section 2's CPU-capacity-vs-workload example.
10. Explain the difference between concurrency and parallelism, using a scheduling-specific example (not copied from this lesson).
11. Explain why context switching has real overhead, and why that matters for how often switching happens.
12. Explain why a waiting/blocked task generally needs little or no CPU time.
13. Explain the difference between fairness and starvation.
14. Explain why "the scheduler chooses whoever arrived first" is an inaccurate description of real scheduling policy.
15. Explain why CPU-bound and I/O-bound workloads interact differently with the scheduler.
16. Explain, in your own words, why the OS scheduler "does not understand Python functions."

### Level 3 — Application

17. Run `nproc` and `lscpu` in your own WSL2 terminal. Record your CPU count and compare it to this lesson's actual observed values (8 CPUs).
18. Using a bounded-duration Python busy-loop (time-limited, like Section 9's example — never an unbounded loop), start two of them in your own terminal, capture their PIDs, and inspect both with `ps -p <PID1>,<PID2> -o pid,stat,%cpu,cmd` while they run.
19. Run `top -b -n 1` while a bounded CPU-bound process is running in your terminal. Identify its `%CPU` and `S` (state) values and compare them to Section 9's actual observed output.
20. Let your bounded processes from Exercise 18 finish naturally, then verify with `ps` that neither remains running.
21. A classmate says, "My AI service uses 4 worker processes, so it should be exactly 4 times faster than 1 worker." Using Section 2 and Section 10, explain what's incorrect about this expectation.
22. Using Section 6's one-core and two-core timeline diagrams, sketch (in text) what a three-task, one-core timeline might conceptually look like.
23. Explain, using Section 9's lab, why both bounded Python processes were observed at close to 100% CPU *simultaneously*, rather than one waiting for the other.
24. Using Section 5's throughput/latency distinction, classify batch inference and online inference (Section 7) by which one they should generally prioritize, and explain why.

### Level 4 — Debugging

25. A Python AI service shows high CPU usage in `ps`. Using Scenario 1 from Section 11, explain why this alone doesn't point to a scheduler problem.
26. An API's latency increases whenever a background CPU-heavy job runs. Using Scenario 2, explain the likely mechanism, without assuming a code bug.
27. A service's per-request performance degrades as more workers are added under heavy load. Using Scenario 3, explain the CPU-capacity reasoning behind this.
28. A process shows near-zero CPU usage but is clearly still running. Using Scenario 4, explain why this isn't automatically evidence of a problem.
29. Adding more threads to CPU-heavy Python code doesn't produce a speedup. Using Scenario 5, explain the two distinct, non-exclusive possible explanations.
30. Two different tools report different CPU percentages for what looks like the same activity. Using Scenario 6, explain why this doesn't necessarily mean either tool is wrong.
31. A task hasn't shown progress in a while. Using Scenario 7, explain how to distinguish "still legitimately CPU-bound," "normally waiting," and "abnormally stuck" using only `ps`-level observations.
32. A learner assumes that because their machine has 8 CPUs (`nproc`), it can run 8 CPU-bound tasks with zero contention forever, no matter how many more tasks are added later. Explain what's incorrect about this generalization, using Section 2.

### Level 5 — Integration

33. Draw (in text/ASCII) a production AI service with an online-inference API, a CPU-heavy preprocessing background job, and several I/O-bound worker threads, all runnable at once — using Section 6's scheduling-cycle diagram as your model, and label which parts are CPU-bound vs. I/O-bound.
34. A friend claims, "Since my server has 8 cores, I never need to think about scheduling — everything just runs in parallel." Using Section 2, Section 6, and Section 9's lab, construct a response explaining when this claim holds and when it breaks down.
35. Explain how "I/O-bound work spends most of its time waiting, not runnable" (Section 5) and "waiting tasks don't compete for CPU" (Section 9) together explain why a service handling many concurrent LLM API calls can remain responsive even with far more logical tasks than CPU cores.
36. A production AI inference service's latency spikes only during batch-inference runs, never otherwise. Using Section 5's throughput/latency trade-off and Section 11's Scenario 2, construct a plausible, reasoned explanation and a non-dangerous way to investigate it.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "my code is correct" and "my service is fast" are genuinely different claims, and why scheduling is a big part of the gap between them.

---

## 13. Expected Results

**Expected conceptual results — these should hold regardless of your specific machine:**

- Correctly define CPU scheduling, runnable, running, and waiting/blocked, in your own words.
- Explain why an operating system needs a scheduler, referencing the CPU-capacity-vs-workload problem.
- Correctly distinguish concurrency from parallelism, and explain why multiple cores are required for genuine parallelism.
- Explain preemption and context switching, including why context switching has real overhead.
- Explain the difference between CPU-bound and I/O-bound work, and why they interact differently with scheduling.
- Explain the difference between throughput and latency, and why scheduling can involve trade-offs between them.
- Explain why the OS scheduler operates on threads/processes, not Python-level functions, and how this differs from CPython's GIL.
- Correctly identify, for several of this lesson's twenty misconceptions, why each is wrong and what the accurate idea is instead.

**What the practical scheduling observations should generally demonstrate, regardless of the exact numbers:**

- Two bounded CPU-bound processes, run at the same time on a machine with enough available CPUs, should each show `%CPU` close to what a single core can provide (often near 100% each, if enough cores are free) — a direct, observable instance of parallelism.
- A CPU-bound process's `ps`/`top` state should show as actively running (`R`) while it's genuinely computing; a waiting process (like a typical idle system service) should show a much lower `%CPU` and a waiting/sleeping state (`S`).
- Bounded processes should terminate on their own, without needing `kill`, and disappear from `ps` afterward.

**Possible environment-dependent results — these will vary by machine and are expected to vary:**

- Your own `nproc`/`lscpu` output will differ from this lesson's actual observed values (`8` CPUs, an Intel i7-8650U) if you're on different hardware or a differently configured WSL2 instance.
- The exact `%CPU` values you observe for concurrently running bounded processes depend on your core count, current system load, and what else is running on your machine or host at the time — this lesson's environment happened to have enough spare cores (8) for two bounded processes to run without meaningful contention; a busier or smaller machine could show lower per-process percentages instead, which would still be entirely consistent with this lesson's model.
- Whether `htop` is installed depends on your specific environment — this lesson's environment did not have it, and that did not block the lesson's practical work.

**Why observed CPU percentages are measurements, not a direct view of every scheduler decision:** as Section 11's Scenario 6 explained, `%CPU` reflects a sampled measurement over some time window, not a complete, instant-by-instant record of every scheduling decision the kernel made — treat it as a useful, genuine signal, not a literal transcript of the scheduler's internal reasoning.

---

## 14. Review Questions

Answers are intentionally not provided directly below these questions.

### Scheduling definition

- What is CPU scheduling?
- What is a scheduler, and what decision does it make repeatedly?

### Why scheduling exists

- Why can't every runnable process or thread simply execute all at once?
- What is the relationship between CPU capacity and workload that makes scheduling necessary?

### Runnable vs. waiting

- What does it mean for a task to be runnable?
- Why does a waiting/blocked task generally not need continuous CPU time?

### Process/thread relationship

- How does scheduling relate to the process states introduced in Concept 03?
- Why are threads, not just processes, important schedulable entities on Linux?

### Concurrency and parallelism

- What is the difference between concurrency and parallelism?
- Why does genuine parallelism require multiple CPU cores?

### Preemption and context switching

- What is preemption, and why is it useful?
- What is a context switch, and why does it have overhead?
- Can a context switch happen between two threads in the same process? Why or why not?

### Fairness and starvation

- What does fairness mean in a scheduling context?
- What is starvation, and how can priority contribute to it?

### Throughput and latency

- What is the difference between throughput and latency?
- Why might a scheduling policy favor one over the other for different workloads?

### CPU-bound vs. I/O-bound

- What distinguishes CPU-bound work from I/O-bound work?
- Why do I/O-bound tasks typically need less continuous CPU time?

### Python and the GIL

- Why doesn't the OS scheduler understand Python functions?
- What is the difference between OS-level thread scheduling and CPython's GIL?

### AI services

- Give two examples of AI-engineering workloads that are CPU-bound, and two that are I/O-bound.
- Why does CPU scheduling still matter in a GPU-accelerated AI system?

### Production debugging

- Why might an API's latency increase when an unrelated CPU-heavy job starts running?
- Why doesn't adding more worker processes always improve throughput?

---

## 15. Production Relevance

At this point, you understand what CPU scheduling is, why it exists, how it relates to runnable/waiting states, what preemption and context switching are, how concurrency differs from parallelism, how CPU-bound and I/O-bound workloads interact differently with the scheduler, what fairness/starvation and throughput/latency trade-offs mean, and how Python's threading model relates to (but is distinct from) OS scheduling. You are not yet expected to know virtual memory's full implementation, specific scheduler algorithms, or synchronization mechanisms — those remain later, more advanced topics.

For a production Applied AI Engineer, this lesson's mental model is genuinely foundational — arguably more than any other lesson so far in this module, because of one central idea:

**Application-level performance cannot be understood solely by looking at application code.** Your Python code can be perfectly correct and reasonably efficient, and your service can still be slow, because scheduling decisions happening underneath it — entirely outside your code's control — are shaping how much CPU time it actually gets, and when.

This shows up constantly in real systems:

- **API latency.** Request-handling threads/processes compete for CPU time with everything else runnable on the machine (Section 11, Scenario 2) — latency is a function of scheduling, not just your handler's own logic.
- **CPU saturation.** When total runnable CPU-bound work exceeds available cores (Section 2), *everything* sharing that machine slows down together, regardless of which specific process is "to blame."
- **Background workers vs. model-serving processes.** These frequently share machines and compete directly for CPU time (Section 7, Section 11) — understanding this competition is the foundation for reasoning about isolating or prioritizing them.
- **Data pipelines, batch inference, online inference.** Different workloads reasonably favor different scheduling outcomes (throughput vs. latency, Section 5) — recognizing which your workload actually needs is a real architectural decision.
- **Concurrent requests and worker contention.** More workers helps only up to the point where CPU capacity, not worker count, becomes the limiting factor (Section 2, Section 11 Scenario 3) — a direct, practical capacity-planning insight.
- **CPU-heavy preprocessing.** Recognizing CPU-bound work for what it is (Section 5) is the first step toward deciding whether it belongs on the same machine as latency-sensitive request handling at all.
- **I/O-heavy applications.** Recognizing I/O-bound work for what it is explains why such applications can remain responsive with surprisingly many concurrent logical tasks, sharing CPU capacity easily because they need so little of it continuously (Section 5, Exercise 35).
- **Throughput, responsiveness, and reliability.** All three are shaped by scheduling outcomes, not solely by application design — a system's reliability under load depends partly on whether its scheduling behavior degrades gracefully or catastrophically as runnable work grows.

**Why this lesson matters more than it might initially seem:** it is one of the foundational reasons a purely code-level view of "is my application correct" is not the same question as "will my application perform well in production." Scheduling is the layer, invisible from inside your Python code, that ultimately decides how much of the CPU your correct, efficient code actually gets to use, moment to moment, in a system shared with everything else running alongside it.

**What comes next**, building directly on this lesson:

```text
Scheduling                      ← this lesson
  → Virtual Memory                (what must be true about a task's memory for the
                                     scheduler to safely run it)
  → Filesystems                    (I/O operations that commonly cause the
                                      runnable/waiting transitions this lesson described)
  → Permissions                     (independent of scheduling, but shares the same
                                       process/thread execution model)
  → Environment Variables             (part of a process's context, unaffected by scheduling)
  → Signals                            (can change a process's/thread's scheduling eligibility)
  → Standard Input/Output                (I/O channels commonly involved in waiting states)
  → Pipes                                 (another common source of waiting/blocked transitions)
  → Shell                                  (a process, scheduled like any other)
  → Process Lifecycle                       (the complete creation-to-termination story,
                                               with scheduling operating throughout it)
```

None of these are taught here — this section exists only to show where this lesson sits within the larger Module 0.2 sequence you are building, one concept at a time.

---

_This file is the completed lesson for Concept 05 of Module 0.2. It intentionally does not teach Linux CFS/EEVDF implementation details, scheduler source code, scheduler kernel data structures, CPU affinity configuration, NUMA, real-time scheduling configuration, interrupt internals, hardware-specific context-switch instructions, synchronization-mechanism internals, virtual-memory internals, container CPU cgroups, Kubernetes scheduling, distributed scheduling systems, or GPU kernel scheduling in depth — those remain the subject of their own dedicated lessons later in this module, later stages of the roadmap, or advanced curriculum beyond this roadmap's current scope._
