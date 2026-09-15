# Concept 3 — CPU Cores — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../03-cores.md`](../03-cores.md), Section 12. Attempt every question yourself first, in your
> own words, before reading any answer below — the value of the exercise comes from reasoning it
> out, not from recognizing the "correct" phrasing.

---

## Level 1 — Recognition

**1. In your own words, what is a CPU core?**

A CPU core is an independent execution unit inside a CPU, capable of fetching, decoding, and
executing instructions on its own, without needing another core to do that work for it.

**2. What is a physical core?**

A physical core is an actual, distinct execution unit that is physically manufactured into the
CPU chip.

**3. What is a logical processor?**

A logical processor is an execution "slot" that the operating system sees and can assign work to.
Usually one physical core corresponds to one logical processor, but on some CPUs a single physical
core can expose more than one logical processor to the operating system.

**4. What is the difference between a single-core CPU and a multi-core CPU?**

A single-core CPU contains exactly one execution unit, so only one fetch-decode-execute cycle can
actively progress at a time. A multi-core CPU contains more than one execution unit, each capable
of independently running its own fetch-decode-execute cycle, making true simultaneous execution
(parallelism) possible.

---

## Level 2 — Understanding

**5. Explain why CPU designers began using multiple cores instead of only making a single core
faster.**

Continuing to push a single core to higher and higher clock frequencies eventually runs into
practical limits — it requires disproportionately more power and generates more heat for each
additional bit of speed. Rather than continuing down that increasingly inefficient path,
designers began placing multiple, somewhat less individually extreme, execution units on one chip
instead — trading "one very fast core" for "several moderately fast cores working together,"
which can be a more practical way to increase overall capacity.

**6. Explain why more cores do not automatically mean proportionally more performance.**

Extra cores only help with work that can actually be divided into independent pieces and that
software has actually been written to divide across them. If a task is strictly sequential (each
step depends on the previous step's result), additional cores have no independent work to do and
sit idle. Even for divisible work, splitting it up and combining results afterward introduces some
overhead, which eats into the theoretical benefit.

**7. Explain the difference between concurrency and parallelism.**

Concurrency means multiple tasks are being managed or making progress, not necessarily at the
exact same instant — a single core can create this appearance by rapidly switching between tasks.
Parallelism means multiple tasks are genuinely executing at the same literal instant, which
requires more than one execution unit (multiple cores) actually working simultaneously.

**8. Explain the difference between a physical core and a logical processor.**

A physical core is an actual execution unit manufactured into the chip. A logical processor is
what the operating system sees as an available execution slot. Usually these are 1-to-1, but a
technique exists (not taught in this lesson) that lets one physical core expose more than one
logical processor — meaning a system can report more "CPUs" via software than it has actual
physical cores.

---

## Level 3 — Application

**9. Record `CPU(s)`, `Core(s) per socket`, `Socket(s)`, and `Thread(s) per core` from your own
`lscpu` output.**

There is no single correct answer — this exercise is about observing *your own* system's real
values inside WSL2. Record whatever `lscpu` actually reports for these four fields on your
machine.

**10. Check whether `Socket(s) × Core(s) per socket × Thread(s) per core` matches `CPU(s)`.**

On virtually all systems, this multiplication will match the `CPU(s)` value (and the `nproc` /
`grep -c "^processor" /proc/cpuinfo` counts) exactly, because all of these are different views of
the same underlying logical-processor count. If `Thread(s) per core` is `1`, your logical
processor count equals your physical core count. If it's `2` (or more), your system is exposing
more logical processors than physical cores — the physical-core-vs-logical-processor distinction
from Section 5, made concrete with your own numbers.

---

## Level 4 — Debugging

**11. `nproc` inside WSL2 is lower than the logical processor count Windows Task Manager shows
for the same machine. Why?**

This is expected virtualization behavior, not an error. WSL2 runs Ubuntu inside a virtual machine
layer that Windows manages, and Windows can be configured to expose only a portion of the host's
total logical processors to that virtual environment. `nproc` reports what's available *within
WSL2 specifically*, which is not guaranteed to match the physical host's full topology as reported
natively by Windows.

**12. A benchmark shows only a modest improvement going from 1 core to 2 cores, not double.
List at least three plausible explanations, and how to start reasoning about which applies.**

At least three of: (a) the workload is partly or wholly sequential, so a second core has limited
independent work available; (b) overhead from splitting work and combining results eats into the
gain; (c) synchronization/dependencies between the two halves force some waiting; (d) shared
resources (memory/data access) become a bottleneck when two cores compete for them; (e) the total
workload is too small to divide meaningfully; (f) the software implementation simply doesn't use
more than one core effectively. To start reasoning about which applies, one would look at whether
the benchmark's task is inherently sequential or divisible (the biggest first clue), and whether
the workload size is large enough that overhead would be negligible by comparison. This lesson
does not require or expect a definitive diagnosis — only recognizing plausible causes.

---

## Level 5 — Integration

**13. Independent data-processing tasks: resizing 100 completely separate image files.**

Yes, additional cores would likely help substantially. Each image resize is independent of every
other — nothing about resizing image #1 depends on image #2's result — so this closely resembles
Section 7's Example 1 and Example 3. Work can be spread across available cores, with each core
handling a subset of the images, closely approaching the "independent work" ideal case.

**14. Strictly sequential computation: each step's result feeds directly into the next step, with
no independent branches.**

No, additional cores would provide little to no benefit. This is exactly Section 7's Example 2 —
because each step must wait for the previous step's result, only one core can be doing useful work
at any given moment. Extra cores would sit idle with no independent work to take on, regardless of
how many are available.

**15. Multiple independent API requests from many different users.**

Yes, additional cores would likely help, assuming the requests are genuinely independent of one
another (one user's request doesn't need to wait on another's). This resembles Section 7's Example
4 — more cores give the server more capacity to make progress on multiple requests around the
same time rather than forcing every request through a single line. The assumption this depends on
(also relevant to Review Question 3 in Section 14) is that the requests really are independent,
and that the server software is actually written to take advantage of more than one core.

**16. AI preprocessing pipeline: cleaning/reformatting many records, where each record is
processed independently of the others.**

Yes, additional cores would likely help, for the same reason as Question 13 — this is Section 7's
Example 3 directly. Since no record's processing depends on any other record's result, the work
can be divided across available cores, and more cores generally means more of that independent
work can happen at the same time (subject to the same caveats about overhead and software
implementation noted throughout this lesson).

---

_This answer key covers Concept 3 (CPU Cores) only. It does not contain, reference, or anticipate
answers for Concept 4 (Binary, Bits, and Bytes) or any later concept._
