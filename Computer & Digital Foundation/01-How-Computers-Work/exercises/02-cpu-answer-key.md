# Concept 2 — CPU — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../02-cpu.md`](../02-cpu.md), Section 12. Attempt every question yourself first, in your own
> words, before reading any answer below — the value of the exercise comes from reasoning it out,
> not from recognizing the "correct" phrasing.

---

## Level 1 — Recognition

**1. In your own words, what is a CPU?**

The CPU (Central Processing Unit) is the hardware component in a computer responsible for
executing instructions — reading each step a program specifies and carrying it out. It is one
component among several in a computer, not the whole machine.

**2. What is a "processor," and how does that word relate to "CPU"?**

"Processor" and "CPU" refer to the same thing and are used interchangeably. It's called a
processor because its job is to *process* information: take input, apply an operation from an
instruction, and produce a result.

**3. What is an instruction, at the beginner level this lesson introduced it?**

An instruction is one single, small, well-defined step a CPU can carry out — for example, "add
these two values" or "check whether one value is greater than another." Programs are made of long
sequences of instructions like these.

**4. What does "execution" mean, as distinct from "instruction" and "result"?**

An instruction is the specification of a step to take. Execution is the CPU actually carrying
that step out. The result is what comes out of having carried it out (e.g., a computed value or a
decision about what happens next). All three are related but distinct: instruction (what to do) →
execution (doing it) → result (what came out of doing it).

---

## Level 2 — Understanding

**5. Explain why a computer needs a CPU at all — what problem does it solve?**

A program is just a sequence of instructions — inert data sitting in storage or memory, doing
nothing by itself. Something has to actually read and carry out each instruction for the program
to do anything. A general-purpose computer needs a component able to execute *any* sequence of
instructions it's given, rather than having fixed logic for only one task — that component is the
CPU.

**6. In your own words, what does "processing" mean?**

Processing means taking a piece of information and transforming it into a different, more useful
piece of information according to some rule or operation — for example, turning `2` and `3`, with
an "add" operation, into `5`.

**7. Explain fetch, decode, and execute, each in one sentence.**

- **Fetch** — the CPU retrieves the next instruction it needs to carry out.
- **Decode** — the CPU figures out what that instruction actually requires (what type of
  operation, on what values).
- **Execute** — the CPU actually carries out the operation and produces a result.

**8. What is the difference between what the ALU does and what the control unit does?**

The ALU (Arithmetic Logic Unit) is the part of the CPU that actually performs arithmetic (like
addition) and logical/comparison operations (like "is A greater than B"). The control unit doesn't
do the math itself — it coordinates the overall process: figuring out what an instruction requires
and directing the right part of the CPU (such as the ALU) to carry it out, and managing the order
instructions happen in. In short: control unit = coordinates the workflow; ALU = performs the
actual computation.

---

## Level 3 — Application

**9. Run `lscpu`, `nproc`, and `uname -m`. Record model name, `nproc` output, and architecture.**

There is no single correct answer here — this exercise is about actually running the commands on
your own WSL2 environment and recording *your* system's real values. When checking your own
output:

- `lscpu`'s "Model name" field names your specific CPU.
- `nproc`'s single number is how many logical processors are currently available *to WSL2* — not
  necessarily your full physical CPU specification (see Section 11, Scenario 2, in the lesson).
- `uname -m` typically prints something like `x86_64` (most common on modern PCs/laptops) or
  `aarch64` (common on ARM-based machines, including some newer laptops).

**10. Run `cat /proc/cpuinfo`. Compare the number of repeated blocks to `nproc`'s output.**

On virtually all systems, the number of repeated `processor` blocks in `/proc/cpuinfo` will match
the number reported by `nproc` exactly — both are reporting the same thing (the number of logical
processing units visible to your environment), just in different formats: `nproc` gives you a
single summary number, while `/proc/cpuinfo` gives you one detailed block per unit.

---

## Level 4 — Debugging

**11. `nproc` is lower than the physical CPU's advertised core count. Why?**

This is expected WSL2 behavior, not an error. WSL2 runs Ubuntu inside a lightweight virtual
machine that Windows manages, and Windows allocates only a defined portion of the host's
processing resources to that virtual machine. `nproc` reports what's available *within the WSL2
environment*, which can be lower than the physical CPU's full core/thread count depending on how
WSL2 is configured. This does not mean anything is broken.

**12. A learner sees several near-identical blocks in `/proc/cpuinfo` and assumes the system is
"broken" or "listing the same CPU multiple times." What's really going on?**

The system isn't broken and isn't listing the same CPU redundantly — it's listing one block per
*logical processing unit* the system can see. A single physical CPU commonly exposes more than
one such unit (the full explanation of why belongs to the Cores lesson, which comes next). For
now, the correct takeaway is simply: seeing multiple similar blocks is normal and expected on
almost any modern system, and is not evidence of a problem.

---

## Level 5 — Integration

**13. Using fetch-decode-execute, explain step by step how the CPU computes `5 + 3` = `8`.**

```text
Fetch    → The CPU retrieves the instruction meaning "add these two values" (5 and 3).
Decode   → The CPU determines this is an arithmetic operation requiring the ALU, using the
           values 5 and 3 as inputs.
Execute  → The control unit directs the ALU to perform the addition; the ALU computes 5 + 3
           and produces the result, 8.
Repeat   → The CPU moves on to fetch whatever instruction comes next in the program.
```

**14. "Since my AI application uses a GPU, the CPU doesn't matter for it." What's wrong with
this, and what are two concrete counterexamples?**

This statement is incorrect because a GPU (or other accelerator) typically only handles the heavy
numerical computation of a model — everything around that still depends on the CPU. Two concrete
examples (see Section 3 of the lesson for more): (1) **Preprocessing/data preparation** — raw
input data (text, images, etc.) usually needs to be loaded, cleaned, and reshaped by CPU-executed
code before it's ever sent to the GPU. (2) **Orchestration/model-serving infrastructure** — the
software that receives a request, decides what to do, sends work to the GPU, and returns a
response runs on the CPU; if that surrounding software is slow or overloaded, the whole
application suffers even if the GPU itself is fast.

**15. Explain why a higher-GHz CPU isn't guaranteed to make an AI application run faster
overall.**

GHz (clock frequency) is only one of several factors that determine real CPU performance —
architecture/design, the number of available processing resources, the specific workload's
characteristics, and how quickly the CPU can actually get the data it needs (memory/data access)
all matter too. In an AI application specifically, a great deal of the CPU-side work is
preprocessing, orchestration, and coordination with the accelerator (Section 3) — if any of those
are bottlenecked by something other than raw clock speed (for example, waiting on data to arrive,
or software that can't use multiple cores effectively), a higher GHz number alone won't fix it.
Overall application speed depends on the whole system working together, not one number describing
one component.

---

_This answer key covers Concept 2 (CPU) only. It does not contain, reference, or anticipate
answers for Concept 3 (Cores) or any later concept._
